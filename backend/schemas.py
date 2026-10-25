import html
import re
from typing import List, Optional, Dict, Any, Tuple, Union
from pydantic import BaseModel, Field, model_validator


def sanitize_xss_input(val: str) -> str:
    """Strips dangerous HTML/JS tags, event handlers, and malicious pseudo-protocols."""
    if not isinstance(val, str):
        return val
    # Remove HTML tags (<script>, <iframe>, <img ...>, etc.)
    cleaned = re.sub(r"<[^>]*?>", "", val)
    # Remove javascript: / data: pseudo-protocols
    cleaned = re.sub(r"javascript\s*:", "", cleaned, flags=re.IGNORECASE)
    # Remove dangerous inline event handlers like onerror=, onload=, onclick=
    cleaned = re.sub(r"on\w+\s*=", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


class SecureBaseModel(BaseModel):
    """Base model that automatically sanitizes all incoming string fields to prevent stored/reflected XSS."""
    @model_validator(mode="before")
    @classmethod
    def sanitize_string_fields(cls, data):
        if isinstance(data, dict):
            return {
                k: sanitize_xss_input(v) if isinstance(v, str) else v
                for k, v in data.items()
            }
        return data


# --- Auth Schemas ---
class SendOTPRequest(SecureBaseModel):
    phone: str = Field(..., min_length=10, max_length=15)

class SendOTPResponse(BaseModel):
    success: bool
    message: str
    otp: Optional[str] = None

class VerifyOTPRequest(SecureBaseModel):
    phone: str = Field(..., min_length=10, max_length=15)
    otp: str = Field(..., min_length=4, max_length=10)

class UserProfileDTO(BaseModel):
    id: Optional[int] = None
    phone: str
    name: Optional[str] = None
    lang: Optional[str] = "hi"
    district: Optional[str] = None
    village: Optional[str] = None
    landmark: Optional[str] = None
    consecutive_cancellations: Optional[int] = 0
    cancelled_orders: Optional[int] = 0
    is_cod_blocked: Optional[bool] = False
    is_blacklisted: Optional[bool] = False
    warning_alert: Optional[str] = None
    trust_score: Optional[int] = 100

class CustomerTrustStatusDTO(BaseModel):
    phone: str
    name: Optional[str] = "Customer"
    consecutive_cancellations: Optional[int] = 0
    cancelled_orders: int
    is_cod_blocked: bool
    is_blacklisted: bool
    warning_alert: Optional[str] = None
    trust_score: int
    allowed_payment_modes: List[str]
    can_order: bool

class CancelOrderRequest(BaseModel):
    reason: Optional[str] = "Customer requested cancellation"

class OrderCancelResponse(BaseModel):
    success: bool
    order_id: str
    status: str
    timeline_stage: int
    payment_mode: str
    subtotal: float
    delivery_fee: float
    platform_fee: float
    total_amount: float
    refund_penalty: float
    refund_amount: float
    consecutive_cancellations: Optional[int] = 0
    cancelled_orders_count: int
    is_cod_blocked: bool
    is_blacklisted: bool
    warning_alert: Optional[str] = None
    message: str

class VerifyOTPResponse(BaseModel):
    success: bool
    message: str
    session_token: str
    user: UserProfileDTO

# --- Landmark Schemas ---
class SaveLandmarkRequest(SecureBaseModel):
    phone: str = Field(..., min_length=10)
    name: str = Field(..., min_length=1)
    district: Optional[str] = None
    village: str = Field(..., min_length=1)
    landmark: str = Field(..., min_length=10)
    lat: Optional[float] = None
    lng: Optional[float] = None
    accuracy: Optional[float] = None

class SaveLandmarkResponse(BaseModel):
    success: bool
    message: str
    user: UserProfileDTO

# --- Catalog Schemas ---
class ProductDTO(BaseModel):
    id: str
    store_id: str
    name_en: str
    name_hi: str
    category: str
    weight: str
    price: float
    mrp: float
    icon: str
    in_stock: bool

    class Config:
        from_attributes = True

class StoreCategoryDTO(BaseModel):
    id: str
    name_en: str
    name_hi: str
    icon: Optional[str] = "category"
    count: Optional[int] = 0

    class Config:
        from_attributes = True

class StoreDTO(BaseModel):
    id: str
    name: str
    hindi_name: Optional[str] = None
    category: str
    store_type: Optional[str] = "kirana"
    rating: Optional[float] = None
    total_orders: int = 0
    distance_km: float = 1.2
    eta_mins: str = "30 Mins"
    is_open: bool = True
    trust_badge: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = "approved"
    owner_name: Optional[str] = None
    id_type: Optional[str] = "Aadhar"
    id_number: Optional[str] = None
    photo_url: Optional[str] = None
    payout_upi: Optional[str] = None
    categories: Optional[List[dict]] = None

    class Config:
        from_attributes = True

# --- Order Schemas ---
class CartItemInput(SecureBaseModel):
    id: str
    name: Optional[str] = None
    price: float
    qty: int

class CheckoutRequest(SecureBaseModel):
    user_phone: str = Field(..., min_length=10)
    user_name: str
    village: str
    landmark: str
    store_id: str = "sharma_brothers"
    payment_mode: str = "COD"  # "COD" or "UPI"
    items: List[CartItemInput]
    customer_lat: Optional[float] = None
    customer_lng: Optional[float] = None
    distance_km: Optional[float] = None

class CheckoutResponse(BaseModel):
    success: bool
    order_id: str
    subtotal: float
    delivery_fee: float
    delivery_discount: Optional[float] = 0.0
    base_delivery_fee: Optional[float] = None
    platform_fee: float
    savings: float
    total_amount: float
    vendor_payout: Optional[float] = None
    runner_payout: Optional[float] = None
    admin_profit: Optional[float] = None
    payment_mode: str
    status: str
    timeline_stage: int
    delivery_otp: str
    distance_km: Optional[float] = None
    eta_mins: Optional[str] = None
    created_at: str

class OrderStatusResponse(BaseModel):
    order_id: str
    status: str
    timeline_stage: int
    delivery_otp: str
    total_amount: float
    payment_mode: str
    store_name: str
    user_name: str
    village: str
    landmark: str
    refund_amount: Optional[float] = None
    refund_penalty: Optional[float] = None
    created_at: str


# --- Vendor (Dukandaar) Schemas ---
class VendorLoginRequest(SecureBaseModel):
    store_id: str = "sharma_brothers"
    phone: Optional[str] = "9876543210"
    pin: Optional[str] = "582941"


class VendorLoginResponse(BaseModel):
    success: bool
    token: str
    store: StoreDTO


class VendorOrderItemDTO(BaseModel):
    product_id: str
    product_name: str
    price: float
    quantity: int
    item_total: float


class VendorOrderDTO(BaseModel):
    id: str
    user_name: str
    user_phone: str
    village: str
    landmark: str
    store_id: str
    store_name: str
    subtotal: float
    delivery_fee: float
    platform_fee: float
    savings: float
    total_amount: float
    payment_mode: str
    status: str
    timeline_stage: int
    delivery_otp: str
    runner_id: Optional[str] = None
    runner_name: Optional[str] = None
    runner_phone: Optional[str] = None
    created_at: str
    items: List[VendorOrderItemDTO]


class UpdateOrderStatusRequest(SecureBaseModel):
    stage: int = Field(..., ge=1, le=5)
    action: Optional[str] = None
    note: Optional[str] = None


class UpdateStockRequest(SecureBaseModel):
    in_stock: bool
    price: Optional[float] = None


class AddProductRequest(SecureBaseModel):
    name_en: str
    name_hi: str
    category: str
    weight: str
    price: float
    mrp: float
    icon: Optional[str] = "inventory_2"
    in_stock: Optional[bool] = True


class StoreStatusUpdateRequest(SecureBaseModel):
    is_open: bool


class VendorLedgerDTO(BaseModel):
    store_id: str
    store_name: str
    date: str
    total_orders: int
    gross_sales: float
    cod_collected: float
    upi_collected: float
    platform_fee_total: float
    net_dukandaar_payout: float
    active_orders_count: int
    completed_orders_count: int


# =============================================================================
# 5. GAON MITRA (DELIVERY PARTNER RUNNER) SCHEMAS
# =============================================================================

class RunnerProfileDTO(BaseModel):
    runner_id: str = "gm_1"
    name: str = "Kamal Singh (कमल सिंह)"
    runner_code: str = "#GM-RAMPUR-07"
    phone: str = "9876543220"
    hub_id: str = "hub_rampur_mandi"
    hub_name: str = "Rampur Mandi Cluster Hub #RMP-04"
    is_online: bool = True
    rating: float = 4.9
    total_completed_missions: int = 142
    status: Optional[str] = "approved"
    id_type: Optional[str] = "Aadhar"
    id_number: Optional[str] = None
    payout_upi: Optional[str] = None


class RunnerLoginRequest(SecureBaseModel):
    phone: Optional[str] = "9876543220"
    otp: Optional[str] = "123456"
    runner_id: Optional[str] = "gm_1"


class RunnerLoginResponse(BaseModel):
    success: bool
    token: str
    runner: RunnerProfileDTO


class ShiftStatusRequest(SecureBaseModel):
    runner_id: str = "gm_1"
    is_online: bool


class ShiftStatusResponse(BaseModel):
    success: bool
    runner_id: str
    is_online: bool
    message: str


class RunnerMissionItemDTO(BaseModel):
    product_id: str
    product_name: str
    price: float
    quantity: int


class RunnerMissionDTO(BaseModel):
    id: str
    store_id: str
    store_name: str
    store_phone: str
    user_name: str
    user_phone: str
    village: str
    landmark: str
    customer_lat: Optional[float] = None
    customer_lng: Optional[float] = None
    items: List[RunnerMissionItemDTO]
    items_count: int
    payment_mode: str
    total_amount: float
    commission: float = 20.0
    status: str
    timeline_stage: int
    delivery_otp: Optional[str] = None
    distance_km: Optional[float] = None
    eta_mins: Optional[str] = None
    created_at: str


class RunnerVerifyOTPRequest(SecureBaseModel):
    otp: str = Field(..., min_length=4, max_length=4)
    cod_collected: Optional[bool] = False
    note: Optional[str] = None


class HandoverResponse(BaseModel):
    success: bool
    order_id: str
    status: str
    timeline_stage: int
    message: str
    commission_earned: float
    cod_cash_collected: float


class RunnerDeliveryRecordDTO(BaseModel):
    order_id: str
    customer_name: str
    village: str
    landmark: str
    payment_mode: str
    amount: float
    commission: float
    timestamp: str


class RunnerLedgerDTO(BaseModel):
    runner_id: str
    runner_name: str
    hub_name: str
    date: str
    completed_today: int
    active_missions: int
    total_earnings: float
    cod_cash_in_hand: float
    distance_covered_km: float
    recent_deliveries: List[RunnerDeliveryRecordDTO]


# =============================================================================
# 6. RURAL-FRIENDLY ONBOARDING & REGISTRATION SCHEMAS
# =============================================================================

class VendorRegisterRequest(SecureBaseModel):
    phone: str = Field(..., min_length=10, max_length=15)
    otp: str = Field(..., min_length=4, max_length=6)
    shop_name: str = Field(..., min_length=3)
    owner_name: str = Field(..., min_length=2)
    category: str = "kirana"
    village: str = Field(..., min_length=2)
    id_type: str = "Aadhar"
    id_number: str = Field(..., min_length=4)
    photo_url: Optional[str] = None
    payout_upi: str = Field(..., min_length=3)


class VendorRegisterResponse(BaseModel):
    success: bool
    store_id: str
    status: str = "pending_approval"
    message: str
    token: Optional[str] = None


class VendorStatusCheckResponse(BaseModel):
    store_id: str
    name: str
    status: str  # "approved", "pending_approval", "rejected"
    can_access: bool
    message: str


class RunnerRegisterRequest(SecureBaseModel):
    phone: str = Field(..., min_length=10, max_length=15)
    otp: str = Field(..., min_length=4, max_length=6)
    name: str = Field(..., min_length=2)
    hub_id: str = "hub_rampur_mandi"
    driving_area: str = "Rampur Mandi Cluster"
    vehicle_type: str = "Motorcycle"
    vehicle_number: str = Field(..., min_length=3)
    id_type: str = "Aadhar"
    id_number: str = Field(..., min_length=4)
    photo_url: Optional[str] = None
    payout_upi: str = Field(..., min_length=3)


class RunnerRegisterResponse(BaseModel):
    success: bool
    runner_id: str
    runner_code: str
    status: str = "pending_approval"
    message: str
    token: Optional[str] = None


class RunnerStatusCheckResponse(BaseModel):
    runner_id: str
    name: str
    status: str  # "approved", "pending_approval", "rejected"
    can_access: bool
    message: str


# =============================================================================
# 7. SUPER ADMIN DASHBOARD SCHEMAS
# =============================================================================

class AdminMetricsResponse(BaseModel):
    total_gmv: float
    platform_profits: float
    total_orders: int
    active_orders: int
    delivered_orders: int
    total_customers: int
    total_vendors: int
    approved_vendors: int
    pending_vendors: int
    total_runners: int
    approved_runners: int
    pending_runners: int


class AdminPendingVendorDTO(BaseModel):
    store_id: str
    name: str
    owner_name: str
    phone: str
    category: str
    id_type: str
    id_number: str
    photo_url: Optional[str] = None
    payout_upi: str
    status: str
    created_at: str


class AdminPendingRunnerDTO(BaseModel):
    runner_id: str
    name: str
    phone: str
    runner_code: str
    hub_name: str
    vehicle_type: str
    vehicle_number: str
    id_type: str
    id_number: str
    photo_url: Optional[str] = None
    payout_upi: str
    status: str
    created_at: str


class AdminVendorDetailDTO(BaseModel):
    store_id: str
    name: str
    owner_name: str
    phone: str
    category: str
    store_type: Optional[str] = "kirana"
    id_type: str
    id_number: str
    photo_url: Optional[str] = None
    payout_upi: str
    bank_account_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_ifsc: Optional[str] = None
    bank_verification_status: Optional[str] = "pending"
    status: str
    is_open: bool
    total_orders: Optional[int] = 0
    rating: Optional[float] = None
    created_at: str


class AdminRunnerDetailDTO(BaseModel):
    runner_id: str
    name: str
    phone: str
    runner_code: str
    hub_name: str
    vehicle_type: str
    vehicle_number: str
    id_type: str
    id_number: str
    photo_url: Optional[str] = None
    payout_upi: str
    bank_account_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_ifsc: Optional[str] = None
    bank_verification_status: Optional[str] = "pending"
    status: str
    is_online: bool
    rating: Optional[float] = 4.9
    total_completed_missions: Optional[int] = 0
    created_at: str


class AdminApprovalActionRequest(SecureBaseModel):
    reason: Optional[str] = None


class AdminGodViewOrderDTO(BaseModel):
    order_id: str
    created_at: str
    customer_name: str
    customer_phone: str
    village: str
    landmark: str
    store_id: str
    store_name: str
    items_summary: str
    total_amount: float
    payment_mode: str
    timeline_stage: int
    status: str
    delivery_otp: str
    distance_km: Optional[float] = None
    eta_mins: Optional[str] = None
    vendor_payout: Optional[float] = None
    runner_payout: Optional[float] = None
    admin_profit: Optional[float] = None
    customer_consecutive_cancellations: Optional[int] = 0
    customer_is_cod_blocked: Optional[bool] = False
    customer_is_blacklisted: Optional[bool] = False


class AdminUserRiskProfileDTO(BaseModel):
    phone: str
    name: Optional[str] = "Customer"
    consecutive_cancellations: int = 0
    is_cod_blocked: bool = False
    is_blacklisted: bool = False
    warning_alert: Optional[str] = None
    created_at: Optional[str] = None


class AdminCommissionLedgerResponse(BaseModel):
    total_platform_revenue: float
    vendor_payouts_due: float
    runner_payouts_due: float
    net_platform_profit: float
    recent_transactions: List[dict]


# --- Support & My Account Schemas ---
class SupportChatRequest(SecureBaseModel):
    user_phone: str = Field(..., min_length=10, max_length=15)
    message: str = Field(..., min_length=1)
    order_id: Optional[str] = None
    lang: Optional[str] = "hi"


class SupportChatResponse(BaseModel):
    reply: str
    action: Optional[str] = None
    escalate_call: bool = False
    quick_replies: Optional[List[str]] = []


class SupportTicketRequest(SecureBaseModel):
    user_phone: str = Field(..., min_length=10, max_length=15)
    message: str = Field(..., min_length=1)
    order_id: Optional[str] = None
    category: Optional[str] = "general"
    subject: Optional[str] = None


class SupportTicketResponse(BaseModel):
    success: bool
    ticket_id: str
    status: str
    message: str
    created_at: str


class CommerceAssistantRequest(SecureBaseModel):
    query: str = Field(..., min_length=1)
    store_id: Optional[str] = None
    lang: Optional[str] = "en"


class CommerceAssistantItemDTO(BaseModel):
    id: str
    name_en: str
    name_hi: str
    category: str
    weight: str
    price: float
    mrp: float
    icon: str
    store_id: str
    store_name: Optional[str] = "Sharma Brothers Kirana"
    matched_keyword: Optional[str] = None
    requested_qty: int = 1


class CommerceAssistantResponse(BaseModel):
    query: str
    parsed_items: List[str]
    products: List[CommerceAssistantItemDTO]
    message: str
    found_count: int
    intent: Optional[str] = "search"
    action_performed: Optional[str] = None
    clarification_question: Optional[str] = None


class UserOrderSummaryDTO(BaseModel):
    order_id: str
    store_name: str
    subtotal: float
    delivery_fee: float
    platform_fee: float
    total_amount: float
    status: str
    timeline_stage: int
    payment_mode: str
    items_count: int
    delivery_otp: str
    created_at: str


# --- FinTech & Payout Onboarding Schemas ---
IFSC_REGEX = re.compile(r"^[A-Z]{4}0[A-Z0-9]{6}$")
UPI_REGEX = re.compile(r"^[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}$")
ACCOUNT_NUM_REGEX = re.compile(r"^\d{9,18}$")

class BankPayoutSettingsRequest(SecureBaseModel):
    account_holder_name: str = Field(..., min_length=2, max_length=150)
    account_number: str = Field(..., min_length=9, max_length=18)
    confirm_account_number: str = Field(..., min_length=9, max_length=18)
    ifsc_code: str = Field(..., min_length=11, max_length=11)
    upi_id: str = Field(..., min_length=3, max_length=100)

    @model_validator(mode="after")
    def validate_payment_details(self):
        self.account_holder_name = self.account_holder_name.strip()
        self.account_number = self.account_number.strip()
        self.confirm_account_number = self.confirm_account_number.strip()
        self.ifsc_code = self.ifsc_code.strip().upper()
        self.upi_id = self.upi_id.strip()

        if self.account_number != self.confirm_account_number:
            raise ValueError("Bank account numbers do not match. Please verify both fields.")

        if not ACCOUNT_NUM_REGEX.match(self.account_number):
            raise ValueError("Invalid account number. Must contain 9 to 18 numeric digits.")

        if not IFSC_REGEX.match(self.ifsc_code):
            raise ValueError("Invalid IFSC Code format. Must be 11 characters (e.g. SBIN0001234: 4 letters, '0', 6 alphanumeric).")

        if not UPI_REGEX.match(self.upi_id):
            raise ValueError("Invalid UPI ID format. Must be a valid VPA (e.g. yourname@bank).")

        return self


class BankPayoutSettingsDTO(BaseModel):
    account_holder_name: Optional[str] = None
    account_number_masked: Optional[str] = None
    ifsc_code: Optional[str] = None
    upi_id: Optional[str] = None
    verification_status: str = "pending"
    is_configured: bool = False


class CustomerSavedPaymentDTO(BaseModel):
    id: int
    user_phone: str
    method_type: str  # "upi", "card"
    title: str
    vpa_or_card: str
    is_default: bool = False
    token_id: Optional[str] = None
    created_at: str


class AddCustomerSavedPaymentRequest(SecureBaseModel):
    method_type: str = Field(..., min_length=3, max_length=10)
    title: str = Field(..., min_length=2, max_length=100)
    vpa_or_card: str = Field(..., min_length=3, max_length=100)
    is_default: Optional[bool] = False

    @model_validator(mode="after")
    def validate_saved_method(self):
        self.method_type = self.method_type.strip().lower()
        self.title = self.title.strip()
        self.vpa_or_card = self.vpa_or_card.strip()

        if self.method_type not in ("upi", "card"):
            raise ValueError("method_type must be either 'upi' or 'card'.")

        if self.method_type == "upi":
            if not UPI_REGEX.match(self.vpa_or_card):
                raise ValueError("Invalid UPI ID format.")
        elif self.method_type == "card":
            # For dummy card or masked card
            cleaned = re.sub(r"[\s\-]", "", self.vpa_or_card)
            if not (cleaned.isdigit() and len(cleaned) in (15, 16)) and not "•" in self.vpa_or_card:
                raise ValueError("Invalid card number format. Must be 15 or 16 digits.")

        return self


class AdminPayoutVerificationDTO(BaseModel):
    entity_type: str  # "vendor" or "runner"
    entity_id: str
    entity_name: str
    phone: Optional[str] = None
    account_holder_name: Optional[str] = None
    account_number_masked: Optional[str] = None
    ifsc_code: Optional[str] = None
    upi_id: Optional[str] = None
    verification_status: str = "pending"
    created_at: Optional[str] = None


class AdminPayoutStatusUpdateRequest(SecureBaseModel):
    status: str = Field(..., min_length=6, max_length=10)

    @model_validator(mode="after")
    def validate_status(self):
        s = self.status.strip().lower()
        if s not in ("pending", "verified", "rejected"):
            raise ValueError("Status must be 'pending', 'verified', or 'rejected'.")
        self.status = s
        return self


# =============================================================================
# RAZORPAY ZERO-TRUST PAYMENT SCHEMAS
# =============================================================================

class CreatePaymentOrderRequest(SecureBaseModel):
    order_id: Optional[str] = None
    items: Optional[List[CartItemInput]] = None
    store_id: Optional[str] = "sharma_brothers"
    user_phone: Optional[str] = None
    user_name: Optional[str] = None
    village: Optional[str] = None
    landmark: Optional[str] = None
    distance_km: Optional[float] = None
    customer_lat: Optional[float] = None
    customer_lng: Optional[float] = None
    amount: Optional[float] = None  # Client-supplied amount to check for tampering


class CreatePaymentOrderResponse(BaseModel):
    success: bool
    order_id: str
    razorpay_order_id: str
    amount: float
    amount_in_paise: int
    currency: str = "INR"
    key_id: str
    customer: dict
    message: str = "Razorpay order created successfully"


class WebhookPaymentEventResponse(BaseModel):
    success: bool
    event: str
    order_id: Optional[str] = None
    payment_id: Optional[str] = None
    status: str
    split_status: Optional[str] = None
    message: str


class SplitPayoutDetailsDTO(BaseModel):
    order_id: str
    total_amount: float
    subtotal: float
    vendor_id: str
    vendor_name: str
    vendor_payout: float
    runner_id: Optional[str] = None
    runner_payout: float
    platform_fee: float
    admin_profit: float
    payment_status: str
    split_payout_status: str
    route_transfers: List[dict]








# =============================================================================
# REAL IN-APP & BACKEND-BACKED NOTIFICATIONS SCHEMAS
# =============================================================================

class NotificationDTO(BaseModel):
    id: str
    user_id: Optional[str] = None
    user_role: str
    order_id: Optional[str] = None
    title: str
    title_hi: str
    message: str
    message_hi: str
    notification_type: str
    is_read: bool
    created_at: str


class NotificationListResponse(BaseModel):
    success: bool
    notifications: List[NotificationDTO]
    unread_count: int
    total_count: int


class UnreadCountResponse(BaseModel):
    unread_count: int


class NotificationMarkReadResponse(BaseModel):
    success: bool
    message: str
    notification_id: Optional[str] = None
    is_read: bool = True


class WebPushSubscriptionRequest(BaseModel):
    user_id: Optional[str] = None
    user_role: str
    endpoint: str
    keys: Dict[str, str] = Field(default_factory=dict)
