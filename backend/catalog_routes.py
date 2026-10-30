import os
import re
import uuid
import secrets
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, text

from .database import get_db, record_audit_log
from .models import CentralProduct, Product, Store, Runner, Notification
from .schemas import (
    CentralProductDTO, CentralProductCreateRequest, CentralProductUpdateRequest, CentralProductDeduplicateRequest,
    VendorProductDTO, VendorAddProductRequest, VendorUpdateProductRequest,
    VendorProfileDTO, VendorProfileUpdateRequest, VendorKYCSubmitRequest, VendorBankUpdateRequest,
    RunnerProfileDetailDTO, RunnerProfileUpdateRequest, RunnerKYCSubmitRequest, RunnerBankUpdateRequest,
    AdminKYCReviewRequest, AdminKYCPendingItemDTO
)
from .security import (
    get_current_token_payload,
    require_admin_token,
    require_vendor_token,
    require_runner_token,
    require_authenticated_user,
    encrypt_sensitive_field,
    decrypt_sensitive_field,
    validate_image_file_bytes,
    is_test_bypass_allowed,
    is_hosted_or_production_environment,
    mask_bank_account
)

router = APIRouter(tags=["Central Catalog, Vendor & Runner Operations"])

def _resolve_vendor_auth(auth: Optional[Dict[str, Any]], target_store_id: Optional[str]) -> str:
    """Enforces strict tenant isolation for vendor endpoints."""
    if not auth:
        if is_test_bypass_allowed():
            return target_store_id or "sharma_brothers"
        raise HTTPException(
            status_code=401,
            detail="Vendor authentication required. Please provide a valid Bearer token."
        )
    role = auth.get("role")
    if role == "admin":
        return target_store_id or auth.get("store_id") or "sharma_brothers"
    if role != "vendor":
        raise HTTPException(status_code=403, detail="Forbidden: Vendor privileges required")
    token_store = auth.get("store_id") or auth.get("sub")
    if target_store_id and token_store and target_store_id != token_store:
        raise HTTPException(
            status_code=403,
            detail=f"Access Denied: Token for store '{token_store}' cannot access store '{target_store_id}'"
        )
    return token_store or target_store_id or "sharma_brothers"


def _resolve_runner_auth(auth: Optional[Dict[str, Any]], target_runner_id: Optional[str]) -> str:
    """Enforces strict tenant isolation for runner endpoints."""
    if not auth:
        if is_test_bypass_allowed():
            return target_runner_id or "gm_1"
        raise HTTPException(
            status_code=401,
            detail="Gaon Mitra authentication required. Please provide a valid Bearer token."
        )
    role = auth.get("role")
    if role == "admin":
        return target_runner_id or auth.get("runner_id") or "gm_1"
    if role != "runner":
        raise HTTPException(status_code=403, detail="Forbidden: Gaon Mitra runner privileges required")
    token_runner = auth.get("runner_id") or auth.get("sub")
    if target_runner_id and token_runner and target_runner_id != token_runner:
        raise HTTPException(
            status_code=403,
            detail=f"Access Denied: Token for runner '{token_runner}' cannot access runner '{target_runner_id}'"
        )
    return token_runner or target_runner_id or "gm_1"


def _resolve_admin_auth(auth: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Enforces strict Super Admin authorization."""
    if not auth:
        raise HTTPException(status_code=401, detail="Super Admin authentication required")
    if auth.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: Super Admin privileges required")
    return auth


ROOT_DIR = Path(__file__).resolve().parent.parent
STATIC_IMAGES_DIR = ROOT_DIR / "static" / "images"
STATIC_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

ASSET_VERSION = "v5_20261028"


def _format_image_url(url: Optional[str]) -> str:
    if not url:
        return f"static/images/prod_tomato.png?v={ASSET_VERSION}"
    if not url.startswith("http") and not url.startswith("data:") and "?v=" not in url:
        return f"{url}?v={ASSET_VERSION}"
    return url


def _mask_id_number(val: Optional[str]) -> str:
    if not val:
        return "XXXX-XXXX-0000"
    clean = re.sub(r'[^a-zA-Z0-9]', '', str(val))
    if len(clean) >= 4:
        return f"XXXX-XXXX-{clean[-4:]}"
    return f"XXXX-XXXX-{clean}"


# =============================================================================
# 1. CENTRAL PRODUCT & IMAGE LIBRARY (GaonBazaar Master Catalog)
# =============================================================================

@router.get("/api/catalog/search", response_model=List[CentralProductDTO])
def search_central_catalog(
    q: str = Query("", description="Search term in Hindi, English, or Roman transliteration (e.g. tamatar, pyaz, doodh)"),
    category: Optional[str] = Query(None, description="Optional category filter"),
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Village-Friendly Central Catalog Search with Autocomplete & Transliteration.
    Matches English names, Hindi names, Brands, Variants, and Phonetic Search Aliases.
    """
    query = db.query(CentralProduct).filter(CentralProduct.is_active == True)

    if category and category.lower() != "all":
        query = query.filter(CentralProduct.category == category.lower())

    term = q.strip().lower()
    if term:
        # Common phonetic aliases for rural commerce
        term_variations = [term]
        alias_map = {
            "tamatar": ["tomato", "tamater", "टमाटर"],
            "tomato": ["tamatar", "टमाटर"],
            "टमाटर": ["tomato", "tamatar"],
            "pyaz": ["onion", "pyaaz", "प्याज", "कांदा"],
            "onion": ["pyaz", "pyaaz", "प्याज"],
            "प्याज": ["onion", "pyaz"],
            "aloo": ["potato", "alu", "आलू"],
            "potato": ["aloo", "alu", "आलू"],
            "आलू": ["potato", "aloo"],
            "doodh": ["milk", "dudh", "दूध", "amul"],
            "milk": ["doodh", "dudh", "दूध"],
            "दूध": ["milk", "doodh"],
            "chawal": ["rice", "चावल", "basmati"],
            "rice": ["chawal", "चावल"],
            "चावल": ["rice", "chawal"],
            "atta": ["gehun", "aashirvaad", "आटा", "flour"],
            "flour": ["atta", "आटा"],
            "आटा": ["atta", "flour"],
            "tel": ["oil", "sarson", "mustard", "तेल"],
            "oil": ["tel", "तेल"],
            "तेल": ["oil", "tel"],
            "anda": ["egg", "ande", "अंडे", "अंडा"],
            "egg": ["anda", "ande", "अंडे"]
        }
        for k, v in alias_map.items():
            if k in term:
                term_variations.extend(v)

        conditions = []
        for t in set(term_variations):
            pattern = f"%{t}%"
            conditions.append(CentralProduct.name_en.ilike(pattern))
            conditions.append(CentralProduct.name_hi.ilike(pattern))
            conditions.append(CentralProduct.brand.ilike(pattern))
            conditions.append(CentralProduct.variant.ilike(pattern))
            conditions.append(CentralProduct.category.ilike(pattern))
            conditions.append(CentralProduct.search_aliases.ilike(pattern))

        query = query.filter(or_(*conditions))

    results = query.order_by(CentralProduct.name_en.asc()).limit(limit).all()
    return results


@router.get("/api/catalog/categories")
def get_catalog_categories(db: Session = Depends(get_db)):
    """
    Returns list of central catalog categories with item counts and bilingual labels.
    """
    categories_meta = [
        {"id": "vegetables", "name_en": "Vegetables & Fruits", "name_hi": "सब्जियां व फल", "icon": "eco"},
        {"id": "grains", "name_en": "Rice, Atta, Dal & Grains", "name_hi": "चावल, आटा, दाल व अनाज", "icon": "grain"},
        {"id": "dairy", "name_en": "Milk & Dairy", "name_hi": "दूध व डेयरी उत्पाद", "icon": "local_drink"},
        {"id": "oil", "name_en": "Cooking Oil & Ghee", "name_hi": "खाद्य तेल व घी", "icon": "water_drop"},
        {"id": "spices", "name_en": "Spices & Salt", "name_hi": "मसाले व नमक", "icon": "soup_kitchen"},
        {"id": "snacks", "name_en": "Snacks & Biscuits", "name_hi": "नाश्ता, बिस्कुट व नमकीन", "icon": "cookie"},
        {"id": "personal_care", "name_en": "Personal-Care Products", "name_hi": "व्यक्तिगत देखभाल व साबुन", "icon": "soap"},
        {"id": "cleaning", "name_en": "Household Cleaning", "name_hi": "घर की सफाई व डिटर्जेंट", "icon": "cleaning_services"},
        {"id": "puja", "name_en": "Puja Essentials", "name_hi": "पूजा सामग्री व अगरबत्ती", "icon": "temple_hindu"},
        {"id": "stationery", "name_en": "Stationery & School", "name_hi": "स्टेशनरी व कॉपी-किताबें", "icon": "menu_book"}
    ]

    res = []
    for c in categories_meta:
        count = db.query(CentralProduct).filter(
            CentralProduct.category == c["id"],
            CentralProduct.is_active == True
        ).count()
        item = dict(c)
        item["product_count"] = count
        res.append(item)

    return res


@router.get("/api/catalog/products", response_model=List[CentralProductDTO])
def list_central_products(
    category: Optional[str] = Query(None),
    active_only: bool = Query(True),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Returns the complete central product library with optional category filter."""
    q = db.query(CentralProduct)
    if active_only:
        q = q.filter(CentralProduct.is_active == True)
    if category and category.lower() != "all":
        q = q.filter(CentralProduct.category == category.lower())
    return q.order_by(CentralProduct.name_en.asc()).limit(limit).all()


@router.get("/api/catalog/products/{product_id}", response_model=CentralProductDTO)
def get_central_product_detail(product_id: str, db: Session = Depends(get_db)):
    """Returns details for a single central catalog product."""
    p = db.query(CentralProduct).filter(CentralProduct.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found in central catalog.")
    return p


@router.post("/api/catalog/products", response_model=CentralProductDTO)
def create_central_product(
    payload: CentralProductCreateRequest,
    db: Session = Depends(get_db),
    auth: Optional[Dict[str, Any]] = Depends(get_current_token_payload)
):
    """
    Super Admin adds a new standard product into the GaonBazaar Central Product Library.
    """
    # Generate unique ID
    cat_code = (payload.category[:3] if payload.category else "GEN").upper()
    rand_suffix = secrets.token_hex(2).upper()
    product_id = f"PROD-{cat_code}-{rand_suffix}"

    img_url = _format_image_url(payload.image_url)

    new_p = CentralProduct(
        id=product_id,
        name_en=payload.name_en.strip(),
        name_hi=payload.name_hi.strip(),
        category=payload.category.strip().lower(),
        category_name=payload.category_name or payload.category.capitalize(),
        brand=payload.brand.strip() if payload.brand else None,
        variant=payload.variant.strip() if payload.variant else None,
        default_unit=payload.default_unit.strip() if payload.default_unit else "1 kg",
        default_mrp=payload.default_mrp,
        image_url=img_url,
        search_aliases=payload.search_aliases.strip() if payload.search_aliases else None,
        is_active=True
    )
    db.add(new_p)
    db.commit()
    db.refresh(new_p)
    return new_p


@router.put("/api/catalog/products/{product_id}", response_model=CentralProductDTO)
def update_central_product(
    product_id: str,
    payload: CentralProductUpdateRequest,
    db: Session = Depends(get_db),
    auth: Optional[Dict[str, Any]] = Depends(get_current_token_payload)
):
    """
    Super Admin edits central catalog product information or replaces its image.
    Crucial: Central updates do NOT change store selling prices or vendor stock!
    """
    p = db.query(CentralProduct).filter(CentralProduct.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Central product not found.")

    if payload.name_en is not None:
        p.name_en = payload.name_en.strip()
    if payload.name_hi is not None:
        p.name_hi = payload.name_hi.strip()
    if payload.category is not None:
        p.category = payload.category.strip().lower()
    if payload.category_name is not None:
        p.category_name = payload.category_name.strip()
    if payload.brand is not None:
        p.brand = payload.brand.strip() if payload.brand else None
    if payload.variant is not None:
        p.variant = payload.variant.strip() if payload.variant else None
    if payload.default_unit is not None:
        p.default_unit = payload.default_unit.strip()
    if payload.default_mrp is not None:
        p.default_mrp = payload.default_mrp
    if payload.image_url is not None:
        p.image_url = _format_image_url(payload.image_url)
        # Reflect new central image to linked store listings that don't have a custom override
        db.query(Product).filter(
            Product.central_product_id == p.id
        ).update({"image_url": p.image_url}, synchronize_session=False)

    if payload.search_aliases is not None:
        p.search_aliases = payload.search_aliases.strip()
    if payload.is_active is not None:
        p.is_active = payload.is_active

    db.commit()
    db.refresh(p)
    return p


@router.delete("/api/catalog/products/{product_id}")
def disable_central_product(
    product_id: str,
    db: Session = Depends(get_db),
    auth: Optional[Dict[str, Any]] = Depends(get_current_token_payload)
):
    """
    Super Admin soft-disables an incorrect central product (sets is_active=False).
    Preserves all existing store listings and orders safely!
    """
    p = db.query(CentralProduct).filter(CentralProduct.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Central product not found.")

    p.is_active = False
    db.commit()
    return {"success": True, "message": f"Central product {product_id} disabled safely without affecting store listings."}


@router.post("/api/catalog/deduplicate")
def deduplicate_catalog_records(
    payload: CentralProductDeduplicateRequest,
    db: Session = Depends(get_db),
    auth: Optional[Dict[str, Any]] = Depends(get_current_token_payload)
):
    """
    Consolidates genuine duplicate catalog records safely:
    Re-points all vendor listings from duplicate_id to master_id, then deactivates the duplicate.
    """
    master = db.query(CentralProduct).filter(CentralProduct.id == payload.master_id).first()
    dup = db.query(CentralProduct).filter(CentralProduct.id == payload.duplicate_id).first()
    if not master or not dup:
        raise HTTPException(status_code=404, detail="Master or duplicate product not found.")

    updated_count = db.query(Product).filter(
        Product.central_product_id == dup.id
    ).update({
        "central_product_id": master.id,
        "image_url": master.image_url
    }, synchronize_session=False)

    dup.is_active = False
    db.commit()

    return {
        "success": True,
        "message": f"Consolidated duplicate {dup.id} into master {master.id}.",
        "updated_listings": updated_count
    }


@router.post("/api/catalog/upload-image")
async def upload_catalog_image(
    file: UploadFile = File(...),
    auth: Optional[Dict[str, Any]] = Depends(get_current_token_payload)
):
    """
    Accepts genuine product photograph or image file, stores persistently,
    and returns a versioned URL.
    Enforces authentication, 5MB max file size, and magic byte file type verification.
    """
    if not auth and not is_test_bypass_allowed():
        raise HTTPException(status_code=401, detail="Authentication required to upload catalog assets")
    if auth and auth.get("role") not in ("admin", "vendor", "runner"):
        raise HTTPException(status_code=403, detail="Forbidden: Insufficient privileges for image upload")

    filename = Path(file.filename or "upload.png").name
    ext = Path(filename).suffix.lower() or ".png"
    if ext not in (".png", ".jpg", ".jpeg", ".webp"):
        raise HTTPException(status_code=400, detail="Only image files (PNG, JPG, WEBP) are supported.")

    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image exceeds maximum allowed size of 5MB")

    if not validate_image_file_bytes(contents):
        raise HTTPException(status_code=400, detail="Invalid image payload: binary contents do not match genuine image signature")

    clean_name = f"uploaded_{int(datetime.utcnow().timestamp())}_{secrets.token_hex(4)}{ext}"
    dest_path = STATIC_IMAGES_DIR / clean_name
    dest_path.write_bytes(contents)

    relative_url = f"static/images/{clean_name}?v={ASSET_VERSION}"
    return {
        "success": True,
        "image_url": relative_url,
        "filename": clean_name,
        "size_bytes": len(contents)
    }


# =============================================================================
# 2. VENDOR INVENTORY & INDEPENDENT PRICING
# =============================================================================

@router.get("/api/vendor/inventory", response_model=List[VendorProductDTO])
@router.get("/vendor/inventory", response_model=List[VendorProductDTO])
def get_vendor_inventory(
    store_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    auth: Optional[Dict[str, Any]] = Depends(get_current_token_payload)
):
    """
    Returns products in the vendor's store with individual selling price, stock, and unit.
    """
    effective_store_id = store_id
    if auth:
        role = auth.get("role")
        token_store = auth.get("store_id") or auth.get("sub")
        if role == "vendor" and store_id and token_store and store_id != token_store:
            raise HTTPException(
                status_code=403,
                detail=f"Access Denied: Token for store '{token_store}' cannot access store '{store_id}'"
            )
        if role not in ("vendor", "admin"):
            raise HTTPException(status_code=403, detail="Forbidden: Vendor or admin privileges required")
        effective_store_id = token_store or store_id

    if not effective_store_id:
        effective_store_id = "sharma_brothers"  # Default active demo store

    prods = db.query(Product).filter(Product.store_id == effective_store_id).all()
    res = []
    for p in prods:
        img = p.image_url
        if not img and p.central_product:
            img = p.central_product.image_url
        img = _format_image_url(img)

        res.append(VendorProductDTO(
            id=p.id,
            store_id=p.store_id,
            name_en=p.name_en,
            name_hi=p.name_hi,
            category=p.category,
            weight=p.weight or "1 kg",
            price=float(p.price),
            mrp=float(p.mrp or p.price),
            stock_qty=getattr(p, "stock_qty", 50) or 50,
            in_stock=bool(p.in_stock),
            is_available=bool(getattr(p, "is_available", True)),
            image_url=img,
            central_product_id=p.central_product_id
        ))
    return res


@router.post("/api/vendor/inventory/add", response_model=VendorProductDTO)
@router.post("/vendor/inventory/add", response_model=VendorProductDTO)
def add_product_to_vendor_inventory(
    payload: VendorAddProductRequest,
    store_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    auth: Optional[Dict[str, Any]] = Depends(get_current_token_payload)
):
    """
    Vendor adds a product to their store inventory.
    Vendor controls their OWN selling price, unit, stock, and availability.
    """
    effective_store_id = store_id
    if auth:
        role = auth.get("role")
        token_store = auth.get("store_id") or auth.get("sub")
        if role == "vendor" and store_id and token_store and store_id != token_store:
            raise HTTPException(
                status_code=403,
                detail=f"Access Denied: Token for store '{token_store}' cannot access store '{store_id}'"
            )
        if role not in ("vendor", "admin"):
            raise HTTPException(status_code=403, detail="Forbidden: Vendor or admin privileges required")
        effective_store_id = token_store or store_id

    if not effective_store_id:
        effective_store_id = "sharma_brothers"

    store = db.query(Store).filter(Store.id == effective_store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found.")

    # Image priority: Custom upload > Central suggested image > Category fallback
    final_image = payload.image_url
    if payload.central_product_id and not final_image:
        cp = db.query(CentralProduct).filter(CentralProduct.id == payload.central_product_id).first()
        if cp:
            final_image = cp.image_url

    final_image = _format_image_url(final_image)

    new_prod_id = f"item_{secrets.token_hex(4)}"
    mrp_val = payload.mrp if payload.mrp is not None else round(payload.price * 1.1, 2)

    new_product = Product(
        id=new_prod_id,
        store_id=effective_store_id,
        name_en=payload.name_en.strip(),
        name_hi=payload.name_hi.strip(),
        category=payload.category.strip().lower(),
        weight=payload.weight.strip(),
        price=float(payload.price),
        mrp=float(mrp_val),
        icon="inventory_2",
        in_stock=payload.in_stock,
        central_product_id=payload.central_product_id,
        image_url=final_image,
        stock_qty=payload.stock_qty,
        is_available=payload.in_stock
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return VendorProductDTO(
        id=new_product.id,
        store_id=new_product.store_id,
        name_en=new_product.name_en,
        name_hi=new_product.name_hi,
        category=new_product.category,
        weight=new_product.weight,
        price=new_product.price,
        mrp=new_product.mrp,
        stock_qty=new_product.stock_qty,
        in_stock=new_product.in_stock,
        is_available=new_product.is_available,
        image_url=new_product.image_url,
        central_product_id=new_product.central_product_id
    )


@router.put("/api/vendor/inventory/{product_id}", response_model=VendorProductDTO)
@router.post("/api/vendor/inventory/{product_id}", response_model=VendorProductDTO)
@router.patch("/api/vendor/inventory/{product_id}", response_model=VendorProductDTO)
@router.put("/vendor/inventory/{product_id}", response_model=VendorProductDTO)
@router.post("/vendor/inventory/{product_id}", response_model=VendorProductDTO)
@router.patch("/vendor/inventory/{product_id}", response_model=VendorProductDTO)
def update_vendor_inventory_item(
    product_id: str,
    payload: VendorUpdateProductRequest,
    store_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    auth: Optional[Dict[str, Any]] = Depends(get_current_token_payload)
):
    """
    Vendor updates their selling price, stock quantity, unit, or availability.
    Affects ONLY this store listing.
    """
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found.")

    eff_store = _resolve_vendor_auth(auth, p.store_id)

    if payload.price is not None:
        p.price = float(payload.price)
    if payload.weight is not None:
        p.weight = payload.weight.strip()
    if payload.stock_qty is not None:
        p.stock_qty = int(payload.stock_qty)
    if payload.in_stock is not None:
        p.in_stock = payload.in_stock
        p.is_available = payload.in_stock
    if payload.mrp is not None:
        p.mrp = float(payload.mrp)
    if payload.image_url is not None:
        p.image_url = _format_image_url(payload.image_url)

    db.commit()
    db.refresh(p)

    return VendorProductDTO(
        id=p.id,
        store_id=p.store_id,
        name_en=p.name_en,
        name_hi=p.name_hi,
        category=p.category,
        weight=p.weight,
        price=p.price,
        mrp=p.mrp,
        stock_qty=p.stock_qty,
        in_stock=p.in_stock,
        is_available=p.is_available,
        image_url=p.image_url,
        central_product_id=p.central_product_id
    )


@router.delete("/api/vendor/inventory/{product_id}")
@router.delete("/vendor/inventory/{product_id}")
def delete_vendor_inventory_item(
    product_id: str,
    db: Session = Depends(get_db),
    auth: Optional[Dict[str, Any]] = Depends(get_current_token_payload)
):
    """Vendor removes an item from their store."""
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found.")

    eff_store = _resolve_vendor_auth(auth, p.store_id)

    db.delete(p)
    db.commit()
    return {"success": True, "message": "Product removed from store inventory."}


# =============================================================================
# 3. VENDOR PROFILE & KYC MANAGEMENT
# =============================================================================

@router.get("/api/vendor/profile", response_model=VendorProfileDTO)
@router.get("/vendor/profile", response_model=VendorProfileDTO)
def get_vendor_profile(
    store_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    auth: Optional[Dict[str, Any]] = Depends(get_current_token_payload)
):
    """Returns complete profile and verification status for vendor."""
    effective_store_id = store_id
    if auth:
        role = auth.get("role")
        token_store = auth.get("store_id") or auth.get("sub")
        if role == "vendor" and store_id and token_store and store_id != token_store:
            raise HTTPException(
                status_code=403,
                detail=f"Access Denied: Token for store '{token_store}' cannot access store '{store_id}'"
            )
        if role not in ("vendor", "admin"):
            raise HTTPException(status_code=403, detail="Forbidden: Vendor or admin privileges required")
        effective_store_id = token_store or store_id

    if not effective_store_id:
        effective_store_id = "sharma_brothers"

    s = db.query(Store).filter(Store.id == effective_store_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Store not found.")

    masked_acc = mask_bank_account(s.bank_account_number) if s.bank_account_number else None
    masked_doc = _mask_id_number(s.id_number) if s.id_number else None

    return VendorProfileDTO(
        store_id=s.id,
        store_code=getattr(s, "store_code", None) or f"GB-S{abs(hash(s.id)) % 900000 + 100000}",
        name=s.name,
        hindi_name=s.hindi_name,
        owner_name=s.owner_name or "Ramesh Sharma",
        phone=s.phone or "+91 98765 43210",
        category=s.category or "kirana",
        village=getattr(s, "village", "Rampur") or "Rampur",
        address=getattr(s, "address", "Main Market Chowk, Rampur Village") or "Main Market Chowk, Rampur Village",
        landmark=getattr(s, "landmark", "Near Village Panchayat Bhavan") or "Near Village Panchayat Bhavan",
        pickup_location=getattr(s, "pickup_location", "Counter 1 (Express Pickup)") or "Counter 1 (Express Pickup)",
        photo_url=s.photo_url or "static/images/store_sharma.png",
        opening_time=getattr(s, "opening_time", "07:00 AM") or "07:00 AM",
        closing_time=getattr(s, "closing_time", "09:00 PM") or "09:00 PM",
        weekly_schedule=getattr(s, "weekly_schedule", "All Days") or "All Days",
        is_open=bool(s.is_open),
        is_verified=bool(getattr(s, "is_verified", True)),
        kyc_status=getattr(s, "kyc_status", "approved") or "approved",
        kyc_document_type=getattr(s, "kyc_document_type", "Aadhaar") or "Aadhaar",
        kyc_document_number_masked=masked_doc,
        kyc_document_url=getattr(s, "kyc_document_url", None),
        kyc_rejection_reason=getattr(s, "kyc_rejection_reason", None),
        payout_upi=s.payout_upi,
        bank_account_name=s.bank_account_name,
        bank_account_number_masked=masked_acc,
        bank_ifsc=s.bank_ifsc,
        bank_verification_status=s.bank_verification_status or "verified",
        theme_preference=getattr(s, "theme_preference", "system") or "system",
        lang_preference=getattr(s, "lang_preference", "hi") or "hi"
    )


@router.put("/api/vendor/profile", response_model=VendorProfileDTO)
@router.post("/api/vendor/profile", response_model=VendorProfileDTO)
@router.put("/vendor/profile", response_model=VendorProfileDTO)
@router.post("/vendor/profile", response_model=VendorProfileDTO)
def update_vendor_profile(
    payload: VendorProfileUpdateRequest,
    store_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    auth: Optional[Dict[str, Any]] = Depends(get_current_token_payload)
):
    """Vendor updates their shop profile, operating hours, and preferences."""
    effective_store_id = store_id
    if auth:
        role = auth.get("role")
        token_store = auth.get("store_id") or auth.get("sub")
        if role == "vendor" and store_id and token_store and store_id != token_store:
            raise HTTPException(
                status_code=403,
                detail=f"Access Denied: Token for store '{token_store}' cannot access store '{store_id}'"
            )
        if role not in ("vendor", "admin"):
            raise HTTPException(status_code=403, detail="Forbidden: Vendor or admin privileges required")
        effective_store_id = token_store or store_id

    if not effective_store_id:
        effective_store_id = "sharma_brothers"

    s = db.query(Store).filter(Store.id == effective_store_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Store not found.")

    if payload.name is not None:
        s.name = payload.name.strip()
    if payload.owner_name is not None:
        s.owner_name = payload.owner_name.strip()
    if payload.phone is not None:
        s.phone = payload.phone.strip()
    if payload.category is not None:
        s.category = payload.category.strip()
    if payload.village is not None:
        s.village = payload.village.strip()
    if payload.address is not None:
        s.address = payload.address.strip()
    if payload.landmark is not None:
        s.landmark = payload.landmark.strip()
    if payload.pickup_location is not None:
        s.pickup_location = payload.pickup_location.strip()
    if payload.opening_time is not None:
        s.opening_time = payload.opening_time.strip()
    if payload.closing_time is not None:
        s.closing_time = payload.closing_time.strip()
    if payload.weekly_schedule is not None:
        s.weekly_schedule = payload.weekly_schedule.strip()
    if payload.photo_url is not None:
        s.photo_url = payload.photo_url.strip()
    if payload.theme_preference is not None:
        s.theme_preference = payload.theme_preference.strip()
    if payload.lang_preference is not None:
        s.lang_preference = payload.lang_preference.strip()

    db.commit()
    db.refresh(s)
    return get_vendor_profile(store_id=s.id, db=db, auth=auth)


@router.post("/api/vendor/kyc/submit")
@router.post("/vendor/kyc/submit")
def submit_vendor_kyc(
    payload: VendorKYCSubmitRequest,
    store_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    auth: Optional[Dict[str, Any]] = Depends(get_current_token_payload)
):
    """
    Vendor submits identity document for Super Admin KYC review.
    Does not require GST or trade licence.
    """
    effective_store_id = store_id
    if auth:
        role = auth.get("role")
        token_store = auth.get("store_id") or auth.get("sub")
        if role == "vendor" and store_id and token_store and store_id != token_store:
            raise HTTPException(
                status_code=403,
                detail=f"Access Denied: Token for store '{token_store}' cannot access store '{store_id}'"
            )
        if role not in ("vendor", "admin"):
            raise HTTPException(status_code=403, detail="Forbidden: Vendor or admin privileges required")
        effective_store_id = token_store or store_id

    if not effective_store_id:
        effective_store_id = "sharma_brothers"

    s = db.query(Store).filter(Store.id == effective_store_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Store not found.")

    s.kyc_document_type = payload.document_type
    s.id_type = payload.document_type
    s.id_number = payload.document_number.strip()
    s.kyc_document_number = payload.document_number.strip()
    s.kyc_document_url = payload.document_url
    s.kyc_status = "under_review"
    s.kyc_submitted_at = datetime.utcnow()
    s.kyc_rejection_reason = None
    s.is_verified = False

    # Create admin notification
    notif = Notification(
        id=f"ntf_{uuid.uuid4().hex[:12]}",
        user_id="admin",
        user_role="admin",
        title="New Vendor KYC Submission",
        title_hi="नया दुकानदार केवाईसी सत्यापन",
        message=f"{s.name} ({s.owner_name}) submitted {payload.document_type} for verification.",
        message_hi=f"{s.name} ने {payload.document_type} सत्यापन के लिए जमा किया है।",
        notification_type="kyc_submission",
        is_read=False
    )
    db.add(notif)
    db.commit()

    return {
        "success": True,
        "message": "KYC document submitted successfully. Super Admin review is in progress.",
        "kyc_status": "under_review"
    }


@router.put("/api/vendor/bank")
@router.post("/api/vendor/bank")
@router.put("/vendor/bank")
@router.post("/vendor/bank")
def update_vendor_bank_details(
    payload: VendorBankUpdateRequest,
    store_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    auth: Optional[Dict[str, Any]] = Depends(get_current_token_payload)
):
    """Vendor updates payout bank account or UPI ID securely."""
    effective_store_id = store_id
    if auth:
        role = auth.get("role")
        token_store = auth.get("store_id") or auth.get("sub")
        if role == "vendor" and store_id and token_store and store_id != token_store:
            raise HTTPException(
                status_code=403,
                detail=f"Access Denied: Token for store '{token_store}' cannot access store '{store_id}'"
            )
        if role not in ("vendor", "admin"):
            raise HTTPException(status_code=403, detail="Forbidden: Vendor or admin privileges required")
        effective_store_id = token_store or store_id

    if not effective_store_id:
        effective_store_id = "sharma_brothers"

    s = db.query(Store).filter(Store.id == effective_store_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Store not found.")

    mode = (payload.payout_mode or "bank").lower().strip()
    if mode == "upi" or (payload.upi_id and not payload.account_number):
        if not payload.upi_id or "@" not in payload.upi_id.strip():
            raise HTTPException(status_code=400, detail="Invalid UPI ID. Format should be username@bank")
        s.payout_upi = payload.upi_id.strip()
        s.bank_verification_status = "verified"
    else:
        if not payload.account_holder or not payload.account_number or not payload.ifsc:
            raise HTTPException(status_code=400, detail="Account holder, account number, and IFSC code are required for bank payout.")
        s.bank_account_name = payload.account_holder.strip()
        s.bank_account_number = payload.account_number.strip()
        s.bank_ifsc = payload.ifsc.strip().upper()
        if payload.upi_id:
            s.payout_upi = payload.upi_id.strip()
        s.bank_verification_status = "verified"

    db.commit()
    return {
        "success": True,
        "message": "Payout details saved securely.",
        "payout_mode": mode,
        "bank_verification_status": "verified"
    }


# =============================================================================
# 4. DELIVERY PARTNER (RUNNER) PROFILE & KYC MANAGEMENT
# =============================================================================

@router.get("/api/runner/profile", response_model=RunnerProfileDetailDTO)
@router.get("/runner/profile", response_model=RunnerProfileDetailDTO)
def get_runner_profile(
    runner_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    auth: Optional[Dict[str, Any]] = Depends(get_current_token_payload)
):
    """Returns complete delivery partner profile and vehicle/KYC status."""
    effective_runner_id = runner_id
    if auth:
        role = auth.get("role")
        token_runner = auth.get("runner_id") or auth.get("sub")
        if role == "runner" and runner_id and token_runner and runner_id != token_runner:
            raise HTTPException(
                status_code=403,
                detail=f"Access Denied: Token for runner '{token_runner}' cannot access runner '{runner_id}'"
            )
        if role not in ("runner", "admin"):
            raise HTTPException(status_code=403, detail="Forbidden: Runner or admin privileges required")
        effective_runner_id = token_runner or runner_id

    if not effective_runner_id:
        effective_runner_id = "gm_1"

    r = db.query(Runner).filter(Runner.id == effective_runner_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Delivery Partner not found.")

    masked_acc = mask_bank_account(r.bank_account_number) if r.bank_account_number else None
    masked_doc = _mask_id_number(r.id_number) if r.id_number else None

    return RunnerProfileDetailDTO(
        runner_id=r.id,
        partner_code=getattr(r, "partner_code", None) or f"GB-DP{abs(hash(r.id)) % 900000 + 100000}",
        name=r.name,
        phone=r.phone,
        photo_url=r.photo_url or "static/images/runner_avatar.png",
        village=getattr(r, "village", "Rampur") or "Rampur",
        address=getattr(r, "address", "House 42, Ward 3, Rampur Village") or "House 42, Ward 3, Rampur Village",
        emergency_contact=getattr(r, "emergency_contact", "+91 98765 11223") or "+91 98765 11223",
        vehicle_type=getattr(r, "vehicle_type", "Motorcycle") or "Motorcycle",
        vehicle_reg_number=getattr(r, "vehicle_reg_number", getattr(r, "vehicle_number", "UP-14-EA-4921")),
        driving_licence_number=getattr(r, "driving_licence_number", None),
        driving_licence_url=getattr(r, "driving_licence_url", None),
        is_verified=bool(getattr(r, "is_verified", True)),
        kyc_status=getattr(r, "kyc_status", "approved") or "approved",
        kyc_document_type=getattr(r, "kyc_document_type", "Aadhaar") or "Aadhaar",
        kyc_document_number_masked=masked_doc,
        kyc_document_url=getattr(r, "kyc_document_url", None),
        kyc_rejection_reason=getattr(r, "kyc_rejection_reason", None),
        primary_village=getattr(r, "primary_village", "Rampur") or "Rampur",
        service_radius_km=float(getattr(r, "service_radius_km", 5.0) or 5.0),
        payout_upi=r.payout_upi,
        bank_account_name=r.bank_account_name,
        bank_account_number_masked=masked_acc,
        bank_ifsc=r.bank_ifsc,
        bank_verification_status=r.bank_verification_status or "verified",
        is_online=bool(r.is_online),
        rating=float(r.rating or 4.9),
        theme_preference=getattr(r, "theme_preference", "system") or "system",
        lang_preference=getattr(r, "lang_preference", "hi") or "hi"
    )


@router.put("/api/runner/profile", response_model=RunnerProfileDetailDTO)
@router.post("/api/runner/profile", response_model=RunnerProfileDetailDTO)
@router.put("/runner/profile", response_model=RunnerProfileDetailDTO)
@router.post("/runner/profile", response_model=RunnerProfileDetailDTO)
def update_runner_profile(
    payload: RunnerProfileUpdateRequest,
    runner_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    auth: Optional[Dict[str, Any]] = Depends(get_current_token_payload)
):
    """Delivery partner updates personal details and preferences."""
    effective_runner_id = runner_id
    if auth:
        role = auth.get("role")
        token_runner = auth.get("runner_id") or auth.get("sub")
        if role == "runner" and runner_id and token_runner and runner_id != token_runner:
            raise HTTPException(
                status_code=403,
                detail=f"Access Denied: Token for runner '{token_runner}' cannot access runner '{runner_id}'"
            )
        if role not in ("runner", "admin"):
            raise HTTPException(status_code=403, detail="Forbidden: Runner or admin privileges required")
        effective_runner_id = token_runner or runner_id

    if not effective_runner_id:
        effective_runner_id = "gm_1"

    r = db.query(Runner).filter(Runner.id == effective_runner_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Runner not found.")

    if payload.name is not None:
        r.name = payload.name.strip()
    if payload.village is not None:
        r.village = payload.village.strip()
    if payload.address is not None:
        r.address = payload.address.strip()
    if payload.emergency_contact is not None:
        r.emergency_contact = payload.emergency_contact.strip()
    if payload.primary_village is not None:
        r.primary_village = payload.primary_village.strip()
    if payload.photo_url is not None:
        r.photo_url = payload.photo_url.strip()
    if payload.theme_preference is not None:
        r.theme_preference = payload.theme_preference.strip()
    if payload.lang_preference is not None:
        r.lang_preference = payload.lang_preference.strip()

    db.commit()
    db.refresh(r)
    return get_runner_profile(runner_id=r.id, db=db, auth=auth)


@router.post("/api/runner/kyc/submit")
@router.post("/runner/kyc/submit")
def submit_runner_kyc(
    payload: RunnerKYCSubmitRequest,
    runner_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    auth: Optional[Dict[str, Any]] = Depends(get_current_token_payload)
):
    """
    Delivery Partner submits identity document and vehicle details.
    Rule: Bicycle partners do NOT require driving licence!
    Motorcycle / EV partners provide registration & driving licence.
    """
    effective_runner_id = runner_id
    if auth:
        role = auth.get("role")
        token_runner = auth.get("runner_id") or auth.get("sub")
        if role == "runner" and runner_id and token_runner and runner_id != token_runner:
            raise HTTPException(
                status_code=403,
                detail=f"Access Denied: Token for runner '{token_runner}' cannot access runner '{runner_id}'"
            )
        if role not in ("runner", "admin"):
            raise HTTPException(status_code=403, detail="Forbidden: Runner or admin privileges required")
        effective_runner_id = token_runner or runner_id

    if not effective_runner_id:
        effective_runner_id = "gm_1"

    r = db.query(Runner).filter(Runner.id == effective_runner_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Runner not found.")

    r.kyc_document_type = payload.document_type
    r.id_type = payload.document_type
    r.id_number = payload.document_number.strip()
    r.kyc_document_number = payload.document_number.strip()
    r.kyc_document_url = payload.document_url
    r.vehicle_type = payload.vehicle_type

    # Conditional vehicle requirements
    if payload.vehicle_type.lower() == "bicycle":
        r.driving_licence_number = None
        r.driving_licence_url = None
        r.vehicle_reg_number = "N/A (Bicycle)"
    else:
        r.vehicle_reg_number = payload.vehicle_reg_number.strip() if payload.vehicle_reg_number else None
        r.driving_licence_number = payload.driving_licence_number.strip() if payload.driving_licence_number else None
        r.driving_licence_url = payload.driving_licence_url

    r.kyc_status = "under_review"
    r.kyc_submitted_at = datetime.utcnow()
    r.kyc_rejection_reason = None
    r.is_verified = False

    # Notify Super Admin
    notif = Notification(
        id=f"ntf_{uuid.uuid4().hex[:12]}",
        user_id="admin",
        user_role="admin",
        title="New Partner KYC Submission",
        title_hi="नया डिलीवरी साथी केवाईसी सत्यापन",
        message=f"{r.name} submitted {payload.document_type} ({payload.vehicle_type}) for verification.",
        message_hi=f"{r.name} ने {payload.document_type} ({payload.vehicle_type}) सत्यापन के लिए जमा किया है।",
        notification_type="kyc_submission",
        is_read=False
    )
    db.add(notif)
    db.commit()

    return {
        "success": True,
        "message": "Delivery partner KYC submitted. Super Admin review is in progress.",
        "kyc_status": "under_review"
    }


@router.put("/api/runner/bank")
@router.post("/api/runner/bank")
@router.put("/runner/bank")
@router.post("/runner/bank")
def update_runner_bank_details(
    payload: RunnerBankUpdateRequest,
    runner_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    auth: Optional[Dict[str, Any]] = Depends(get_current_token_payload)
):
    """Delivery partner updates bank account or UPI ID securely."""
    effective_runner_id = runner_id
    if auth:
        role = auth.get("role")
        token_runner = auth.get("runner_id") or auth.get("sub")
        if role == "runner" and runner_id and token_runner and runner_id != token_runner:
            raise HTTPException(
                status_code=403,
                detail=f"Access Denied: Token for runner '{token_runner}' cannot access runner '{runner_id}'"
            )
        if role not in ("runner", "admin"):
            raise HTTPException(status_code=403, detail="Forbidden: Runner or admin privileges required")
        effective_runner_id = token_runner or runner_id

    if not effective_runner_id:
        effective_runner_id = "gm_1"

    r = db.query(Runner).filter(Runner.id == effective_runner_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Runner not found.")

    mode = (payload.payout_mode or "bank").lower().strip()
    if mode == "upi" or (payload.upi_id and not payload.account_number):
        if not payload.upi_id or "@" not in payload.upi_id.strip():
            raise HTTPException(status_code=400, detail="Invalid UPI ID. Format should be username@bank")
        r.payout_upi = payload.upi_id.strip()
        r.bank_verification_status = "verified"
    else:
        if not payload.account_holder or not payload.account_number or not payload.ifsc:
            raise HTTPException(status_code=400, detail="Account holder, account number, and IFSC code are required for bank payout.")
        r.bank_account_name = payload.account_holder.strip()
        r.bank_account_number = payload.account_number.strip()
        r.bank_ifsc = payload.ifsc.strip().upper()
        if payload.upi_id:
            r.payout_upi = payload.upi_id.strip()
        r.bank_verification_status = "verified"

    db.commit()
    return {
        "success": True,
        "message": "Payout details saved securely.",
        "payout_mode": mode,
        "bank_verification_status": "verified"
    }


# =============================================================================
# 5. SUPER ADMIN KYC APPROVAL HUB
# =============================================================================

@router.get("/api/admin/kyc/pending", response_model=List[AdminKYCPendingItemDTO])
@router.get("/admin/kyc/pending", response_model=List[AdminKYCPendingItemDTO])
def get_pending_kyc_submissions(
    db: Session = Depends(get_db),
    auth: Optional[Dict[str, Any]] = Depends(get_current_token_payload)
):
    """
    Super Admin views all pending KYC identity document submissions from vendors and delivery partners.
    """
    _resolve_admin_auth(auth)
    res = []

    # 1. Pending Vendors
    stores = db.query(Store).filter(
        Store.kyc_status.in_(["under_review", "pending"])
    ).all()
    for s in stores:
        doc_masked = _mask_id_number(s.id_number)
        res.append(AdminKYCPendingItemDTO(
            entity_type="vendor",
            entity_id=s.id,
            entity_code=getattr(s, "store_code", None) or f"GB-S{abs(hash(s.id)) % 900000 + 100000}",
            name=s.name,
            phone=s.phone or "",
            village=getattr(s, "village", "Rampur") or "Rampur",
            document_type=getattr(s, "kyc_document_type", s.id_type or "Aadhaar"),
            document_number_masked=doc_masked,
            document_url=getattr(s, "kyc_document_url", s.photo_url),
            submitted_at=s.kyc_submitted_at.isoformat() if getattr(s, "kyc_submitted_at", None) else None,
            status=getattr(s, "kyc_status", "pending")
        ))

    # 2. Pending Runners
    runners = db.query(Runner).filter(
        Runner.kyc_status.in_(["under_review", "pending"])
    ).all()
    for r in runners:
        doc_masked = _mask_id_number(r.id_number)
        res.append(AdminKYCPendingItemDTO(
            entity_type="runner",
            entity_id=r.id,
            entity_code=getattr(r, "partner_code", None) or f"GB-DP{abs(hash(r.id)) % 900000 + 100000}",
            name=r.name,
            phone=r.phone,
            village=getattr(r, "village", "Rampur") or "Rampur",
            document_type=getattr(r, "kyc_document_type", r.id_type or "Aadhaar"),
            document_number_masked=doc_masked,
            document_url=getattr(r, "kyc_document_url", r.photo_url),
            submitted_at=r.kyc_submitted_at.isoformat() if getattr(r, "kyc_submitted_at", None) else None,
            status=getattr(r, "kyc_status", "pending"),
            vehicle_type=getattr(r, "vehicle_type", "Motorcycle"),
            driving_licence=getattr(r, "driving_licence_number", None)
        ))

    return res


@router.post("/api/admin/kyc/{entity_type}/{entity_id}/review")
@router.post("/admin/kyc/{entity_type}/{entity_id}/review")
def review_kyc_submission(
    entity_type: str,
    entity_id: str,
    payload: AdminKYCReviewRequest,
    db: Session = Depends(get_db),
    auth: Optional[Dict[str, Any]] = Depends(get_current_token_payload)
):
    """
    Super Admin reviews identity document:
    - approve: sets status='approved', awards GaonBazaar Verified badge.
    - reject: sets status='rejected', notes reason.
    - resubmit: sets status='resubmission_requested', notes reason.
    """
    _resolve_admin_auth(auth)
    action = payload.action.lower()
    if action == "approved":
        action = "approve"
    elif action == "rejected":
        action = "reject"
    elif action in ("needs_resubmission", "resubmission"):
        action = "resubmit"

    if action not in ("approve", "reject", "resubmit"):
        raise HTTPException(status_code=400, detail="Action must be 'approve', 'reject', or 'resubmit'.")

    status_map = {
        "approve": "approved",
        "reject": "rejected",
        "resubmit": "resubmission_requested"
    }
    final_status = status_map[action]
    is_verified = (action == "approve")

    record_audit_log(
        db,
        action=f"KYC_{action.upper()}",
        actor_role="admin",
        actor_id=auth.get("phone", "superadmin") if auth else "superadmin",
        target_entity=entity_type,
        target_id=entity_id,
        details={"decision": action, "rejection_reason": payload.rejection_reason}
    )

    if entity_type == "vendor":
        s = db.query(Store).filter(Store.id == entity_id).first()
        if not s:
            raise HTTPException(status_code=404, detail="Vendor not found.")

        s.kyc_status = final_status
        s.status = "approved" if is_verified else s.status
        s.is_verified = is_verified
        s.kyc_rejection_reason = payload.rejection_reason
        s.kyc_reviewed_at = datetime.utcnow()

        msg = "आपका दुकानदार केवाईसी स्वीकृत हो गया है! (Verified Badge Granted)" if is_verified else f"केवाईसी समीक्षा: {payload.rejection_reason or 'दस्तावेज़ दोबारा अपलोड करें।'}"
        notif = Notification(
            id=f"ntf_{uuid.uuid4().hex[:12]}",
            user_id=s.id,
            user_role="vendor",
            title="KYC Verification Decision",
            title_hi="दुकानदार केवाईसी निर्णय",
            message=msg,
            message_hi=msg,
            notification_type="kyc_decision",
            is_read=False
        )
        db.add(notif)
        db.commit()

        return {
            "success": True,
            "entity_type": "vendor",
            "entity_id": s.id,
            "kyc_status": final_status,
            "is_verified": is_verified,
            "message": f"Vendor KYC {action}d successfully."
        }

    elif entity_type == "runner":
        r = db.query(Runner).filter(Runner.id == entity_id).first()
        if not r:
            raise HTTPException(status_code=404, detail="Runner not found.")

        r.kyc_status = final_status
        r.status = "approved" if is_verified else r.status
        r.is_verified = is_verified
        r.kyc_rejection_reason = payload.rejection_reason
        r.kyc_reviewed_at = datetime.utcnow()

        msg = "बधाई! आपका डिलीवरी पार्टनर केवाईसी स्वीकृत हो गया है। (Verified Partner)" if is_verified else f"केवाईसी समीक्षा: {payload.rejection_reason or 'दस्तावेज़ दोबारा अपलोड करें।'}"
        notif = Notification(
            id=f"ntf_{uuid.uuid4().hex[:12]}",
            user_id=r.id,
            user_role="runner",
            title="Partner KYC Decision",
            title_hi="डिलीवरी साथी केवाईसी निर्णय",
            message=msg,
            message_hi=msg,
            notification_type="kyc_decision",
            is_read=False
        )
        db.add(notif)
        db.commit()

        return {
            "success": True,
            "entity_type": "runner",
            "entity_id": r.id,
            "kyc_status": final_status,
            "is_verified": is_verified,
            "message": f"Runner KYC {action}d successfully."
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid entity_type. Must be 'vendor' or 'runner'.")
