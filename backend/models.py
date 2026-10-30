from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(15), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=True)
    lang = Column(String(10), default="hi")
    session_token = Column(String(500), unique=True, index=True, nullable=True)
    consecutive_cancellations = Column(Integer, default=0)
    cancelled_orders = Column(Integer, default=0)
    is_cod_blocked = Column(Boolean, default=False)
    is_blacklisted = Column(Boolean, default=False)
    warning_alert = Column(String(255), nullable=True)
    trust_score = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)

    landmarks = relationship("Landmark", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user")


class OTPRecord(Base):
    __tablename__ = "otp_records"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(15), index=True, nullable=False)
    otp_code = Column(String(10), nullable=False)
    is_verified = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)


class Landmark(Base):
    __tablename__ = "landmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    phone = Column(String(15), index=True, nullable=False)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    district = Column(String(100), nullable=True, default="Muzaffarpur")
    block = Column(String(100), nullable=True, default="Minapur")
    village = Column(String(150), nullable=False)
    landmark_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="landmarks")


class Store(Base):
    __tablename__ = "stores"

    id = Column(String(50), primary_key=True, index=True)  # e.g. "sharma_brothers"
    name = Column(String(100), nullable=False)
    hindi_name = Column(String(100), nullable=True)
    category = Column(String(50), default="kirana")
    store_type = Column(String(50), default="kirana")  # "kirana", "pharma", "agri", "dairy", "electronics"
    rating = Column(Float, nullable=True, default=None)  # Dynamic variable from DB or None for new stores
    total_orders = Column(Integer, default=0)
    distance_km = Column(Float, default=1.2)
    eta_mins = Column(String(50), default="30 Mins")
    lat = Column(Float, default=29.1350)
    lng = Column(Float, default=77.0100)
    is_open = Column(Boolean, default=True)
    trust_badge = Column(String(100), nullable=True, default=None)  # Dynamic variable or None
    phone = Column(String(15), nullable=True, default=None)
    owner_name = Column(String(100), nullable=True, default=None)
    id_type = Column(String(20), default="Aadhar")
    id_number = Column(String(50), default="XXXX-XXXX-8921")
    photo_url = Column(Text, nullable=True)
    payout_upi = Column(String(100), default="sharma.kirana@okaxis")
    bank_account_name = Column(String(150), nullable=True, default=None)
    bank_account_number = Column(Text, nullable=True, default=None)
    bank_ifsc = Column(String(20), nullable=True, default=None)
    bank_verification_status = Column(String(20), default="pending")  # "pending", "verified", "rejected"
    status = Column(String(30), default="approved")  # "approved", "pending_approval", "rejected"
    store_code = Column(String(50), unique=True, nullable=True)  # e.g. "GB-S000001"
    village = Column(String(100), default="Rampur")
    address = Column(Text, nullable=True)
    landmark = Column(String(150), nullable=True)
    pickup_location = Column(String(150), nullable=True)
    opening_time = Column(String(20), default="07:00 AM")
    closing_time = Column(String(20), default="09:00 PM")
    weekly_schedule = Column(String(50), default="All Days")
    kyc_status = Column(String(30), default="approved")  # "pending", "under_review", "approved", "rejected", "resubmission_requested"
    kyc_document_type = Column(String(50), default="Aadhaar")
    kyc_document_number = Column(String(100), default="XXXX-XXXX-8921")
    kyc_document_url = Column(Text, nullable=True)
    kyc_rejection_reason = Column(Text, nullable=True)
    kyc_submitted_at = Column(DateTime, nullable=True)
    kyc_reviewed_at = Column(DateTime, nullable=True)
    is_verified = Column(Boolean, default=True)  # GaonBazaar Verified badge
    theme_preference = Column(String(20), default="system")
    lang_preference = Column(String(10), default="hi")
    created_at = Column(DateTime, default=datetime.utcnow)

    products = relationship("Product", back_populates="store", cascade="all, delete-orphan")


class StoreCategory(Base):
    __tablename__ = "store_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_type = Column(String(50), index=True, nullable=False)  # "kirana", "pharma", "agri", "dairy", "electronics"
    category_id = Column(String(50), nullable=False)  # "all", "atta", "pharma", "seeds", etc.
    name_en = Column(String(100), nullable=False)
    name_hi = Column(String(100), nullable=False)
    icon = Column(String(50), default="category")


class CentralProduct(Base):
    __tablename__ = "central_products"

    id = Column(String(50), primary_key=True, index=True)  # e.g. "PROD-VEG-001"
    name_en = Column(String(150), nullable=False, index=True)
    name_hi = Column(String(150), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)  # "vegetables", "dairy", "grains", "oil", etc.
    category_name = Column(String(100), nullable=True)
    brand = Column(String(100), nullable=True)
    variant = Column(String(100), nullable=True)
    default_unit = Column(String(50), default="1 kg")
    default_mrp = Column(Float, nullable=True, default=None)
    image_url = Column(Text, nullable=False)
    search_aliases = Column(Text, nullable=True)  # e.g. "tamatar, pyaz, doodh"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    store_listings = relationship("Product", back_populates="central_product")


class Product(Base):
    __tablename__ = "products"

    id = Column(String(50), primary_key=True, index=True)  # e.g. "item_1"
    store_id = Column(String(50), ForeignKey("stores.id"), nullable=False)
    name_en = Column(String(150), nullable=False)
    name_hi = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False)  # "atta", "oil", "spices", "tea", etc.
    weight = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    mrp = Column(Float, nullable=False)
    icon = Column(String(50), default="inventory_2")
    in_stock = Column(Boolean, default=True)
    central_product_id = Column(String(50), ForeignKey("central_products.id"), nullable=True)
    image_url = Column(Text, nullable=True)
    stock_qty = Column(Integer, default=50)
    is_available = Column(Boolean, default=True)

    store = relationship("Store", back_populates="products")
    central_product = relationship("CentralProduct", back_populates="store_listings")


class Order(Base):
    __tablename__ = "orders"

    id = Column(String(50), primary_key=True, index=True)  # e.g. "#RUR-9482"
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_phone = Column(String(15), nullable=False)
    user_name = Column(String(100), nullable=False)
    district = Column(String(100), nullable=True, default="Muzaffarpur")
    block = Column(String(100), nullable=True, default="Minapur")
    village = Column(String(150), nullable=False)
    landmark = Column(Text, nullable=False)
    customer_lat = Column(Float, nullable=True)
    customer_lng = Column(Float, nullable=True)
    runner_id = Column(String(50), ForeignKey("runners.id"), nullable=True)
    store_id = Column(String(50), ForeignKey("stores.id"), nullable=False)
    store_name = Column(String(100), nullable=False)
    subtotal = Column(Float, nullable=False)
    delivery_fee = Column(Float, default=0.0)
    delivery_discount = Column(Float, default=0.0)
    base_delivery_fee = Column(Float, default=0.0)
    platform_fee = Column(Float, default=3.0)
    savings = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    vendor_payout = Column(Float, default=0.0)
    runner_payout = Column(Float, default=0.0)
    admin_profit = Column(Float, default=13.0)
    distance_km = Column(Float, default=1.5)
    distance_type = Column(String(50), default="road_routing_estimate")
    eta_mins = Column(String(50), default="30 Mins")
    payment_mode = Column(String(20), default="COD")
    status = Column(String(50), default="Order Placed")
    timeline_stage = Column(Integer, default=1)  # 1 to 5
    delivery_otp = Column(String(10), nullable=False)  # 4-digit code e.g. "4821"
    refund_amount = Column(Float, default=0.0)
    refund_penalty = Column(Float, default=0.0)
    cancellation_reason = Column(String(255), nullable=True)
    payment_status = Column(String(30), default="PENDING")  # "PENDING", "PAID", "FAILED"
    razorpay_order_id = Column(String(100), nullable=True, index=True)
    razorpay_payment_id = Column(String(100), nullable=True)
    razorpay_signature = Column(String(255), nullable=True)
    split_payout_status = Column(String(30), default="unprocessed")  # "unprocessed", "prepared", "settled"
    vendor_transfer_id = Column(String(100), nullable=True)
    runner_transfer_id = Column(String(100), nullable=True)
    paid_at = Column(DateTime, nullable=True)
    data_origin = Column(String(30), default="live", nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    transactions = relationship("PaymentTransaction", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), ForeignKey("orders.id"), nullable=False)
    product_id = Column(String(50), nullable=False)
    product_name = Column(String(150), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="items")


class ArchivedOrderItem(Base):
    __tablename__ = "archived_order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), nullable=False, index=True)
    product_id = Column(String(50), nullable=False)
    product_name = Column(String(150), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    archive_reason = Column(String(100), default="synthetic_test_fixture_unlinked")
    archived_at = Column(DateTime, default=datetime.utcnow)


class Runner(Base):
    __tablename__ = "runners"

    id = Column(String(50), primary_key=True, index=True)  # e.g. "gm_1"
    name = Column(String(100), nullable=False)
    phone = Column(String(15), unique=True, index=True, nullable=False)
    runner_code = Column(String(50), unique=True, nullable=False)
    hub_id = Column(String(50), default="hub_rampur_mandi")
    hub_name = Column(String(100), default="Rampur Mandi Cluster Hub #RMP-04")
    id_type = Column(String(20), default="Aadhar")
    id_number = Column(String(50), default="XXXX-XXXX-4821")
    photo_url = Column(Text, nullable=True)
    vehicle_type = Column(String(50), default="Motorcycle")
    vehicle_number = Column(String(50), default="UP-14-EA-4921")
    payout_upi = Column(String(100), default="kamal.singh@ybl")
    bank_account_name = Column(String(150), nullable=True, default=None)
    bank_account_number = Column(Text, nullable=True, default=None)
    bank_ifsc = Column(String(20), nullable=True, default=None)
    bank_verification_status = Column(String(20), default="pending")  # "pending", "verified", "rejected"
    status = Column(String(30), default="approved")  # "approved", "pending_approval", "rejected"
    is_online = Column(Boolean, default=True)
    rating = Column(Float, default=4.9)
    total_completed_missions = Column(Integer, default=142)
    partner_code = Column(String(50), unique=True, nullable=True)  # e.g. "GB-DP-000001"
    village = Column(String(100), default="Rampur")
    address = Column(Text, nullable=True)
    emergency_contact = Column(String(15), nullable=True)
    vehicle_reg_number = Column(String(50), nullable=True)
    driving_licence_number = Column(String(50), nullable=True)
    driving_licence_url = Column(Text, nullable=True)
    kyc_status = Column(String(30), default="approved")  # "pending", "under_review", "approved", "rejected", "resubmission_requested"
    kyc_document_type = Column(String(50), default="Aadhaar")
    kyc_document_number = Column(String(100), default="XXXX-XXXX-4821")
    kyc_document_url = Column(Text, nullable=True)
    kyc_rejection_reason = Column(Text, nullable=True)
    kyc_submitted_at = Column(DateTime, nullable=True)
    kyc_reviewed_at = Column(DateTime, nullable=True)
    is_verified = Column(Boolean, default=True)  # GaonBazaar Verified badge
    primary_village = Column(String(100), default="Rampur")
    service_radius_km = Column(Float, default=5.0)
    theme_preference = Column(String(20), default="system")
    lang_preference = Column(String(10), default="hi")
    created_at = Column(DateTime, default=datetime.utcnow)


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(50), unique=True, index=True, nullable=False)
    user_phone = Column(String(15), index=True, nullable=False)
    order_id = Column(String(50), nullable=True)
    category = Column(String(50), default="general")
    message = Column(Text, nullable=False)
    status = Column(String(20), default="open")  # "open", "in_progress", "resolved"
    preferred_resolution = Column(String(30), default="refund")  # "refund", "replacement"
    affected_items_json = Column(Text, nullable=True)
    evidence_url = Column(Text, nullable=True)
    replacement_id = Column(String(50), nullable=True)
    refund_id = Column(String(50), nullable=True)
    responsible_party = Column(String(30), default="unclear")  # "vendor", "runner", "platform", "unclear", "customer"
    admin_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SavedPaymentMethod(Base):
    __tablename__ = "saved_payment_methods"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_phone = Column(String(15), index=True, nullable=False)
    method_type = Column(String(20), nullable=False)  # "upi", "card"
    title = Column(String(100), nullable=False)  # e.g. "Google Pay UPI", "HDFC Debit Card"
    vpa_or_card = Column(String(100), nullable=False)  # e.g. "user@okhdfcbank" or "•••• •••• •••• 4242"
    is_default = Column(Boolean, default=False)
    token_id = Column(String(100), nullable=True)  # e.g. "tok_rzp_mock_12345"
    created_at = Column(DateTime, default=datetime.utcnow)


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(String(50), ForeignKey("orders.id"), nullable=False, index=True)
    razorpay_order_id = Column(String(100), index=True, nullable=True)
    razorpay_payment_id = Column(String(100), index=True, nullable=True)
    amount = Column(Float, nullable=False)
    amount_in_paise = Column(Integer, nullable=False)
    currency = Column(String(10), default="INR")
    status = Column(String(30), default="created")  # "created", "captured", "failed", "verified"
    payment_mode = Column(String(30), default="ONLINE")
    signature = Column(String(255), nullable=True)
    verified = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)
    raw_payload = Column(Text, nullable=True)

    # Razorpay Route split payout preparation
    vendor_split_amount = Column(Float, default=0.0)
    runner_split_amount = Column(Float, default=0.0)
    admin_platform_fee = Column(Float, default=3.0)
    admin_margin = Column(Float, default=0.0)
    route_transfer_status = Column(String(30), default="prepared")  # "prepared", "settled", "failed"
    vendor_transfer_id = Column(String(100), nullable=True)
    runner_transfer_id = Column(String(100), nullable=True)
    settlement_id = Column(String(100), nullable=True)
    settled_at = Column(DateTime, nullable=True)
    failure_reason = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="transactions")


class ArchivedPaymentTransaction(Base):
    __tablename__ = "archived_payment_transactions"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), nullable=False, index=True)
    razorpay_order_id = Column(String(100), index=True, nullable=True)
    razorpay_payment_id = Column(String(100), index=True, nullable=True)
    amount = Column(Float, nullable=False)
    amount_in_paise = Column(Integer, nullable=False)
    currency = Column(String(10), default="INR")
    status = Column(String(30), default="created")
    payment_mode = Column(String(30), default="ONLINE")
    signature = Column(String(255), nullable=True)
    verified = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)
    raw_payload = Column(Text, nullable=True)
    vendor_split_amount = Column(Float, default=0.0)
    runner_split_amount = Column(Float, default=0.0)
    admin_platform_fee = Column(Float, default=3.0)
    admin_margin = Column(Float, default=0.0)
    route_transfer_status = Column(String(30), default="prepared")
    vendor_transfer_id = Column(String(100), nullable=True)
    runner_transfer_id = Column(String(100), nullable=True)
    settlement_id = Column(String(100), nullable=True)
    settled_at = Column(DateTime, nullable=True)
    failure_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    archive_reason = Column(String(100), default="synthetic_test_fixture_unlinked")
    archived_at = Column(DateTime, default=datetime.utcnow)






class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(50), primary_key=True, index=True)  # e.g. "ntf_..."
    user_id = Column(String(50), nullable=True, index=True)  # phone, store_id, runner_id, or "admin"
    user_role = Column(String(20), index=True, nullable=False)  # "customer", "vendor", "runner", "admin"
    order_id = Column(String(50), nullable=True, index=True)
    title = Column(String(200), nullable=False)
    title_hi = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    message_hi = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # "order_placed", "order_packed", etc.
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class MessageThread(Base):
    __tablename__ = "message_threads"

    id = Column(String(50), primary_key=True, index=True)
    order_id = Column(String(50), ForeignKey("orders.id"), nullable=True, index=True)
    vendor_id = Column(String(50), nullable=False, index=True)
    runner_id = Column(String(50), nullable=True, index=True)
    customer_phone = Column(String(20), nullable=True)
    subject = Column(String(200), default="Order Coordination")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("ChatMessage", back_populates="thread", cascade="all, delete-orphan", order_by="ChatMessage.created_at")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    thread_id = Column(String(50), ForeignKey("message_threads.id"), nullable=False, index=True)
    sender_id = Column(String(50), nullable=False)
    sender_role = Column(String(20), nullable=False)  # "vendor", "runner", "customer", "admin"
    sender_name = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    thread = relationship("MessageThread", back_populates="messages")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    action = Column(String(100), nullable=False, index=True)
    actor_role = Column(String(50), nullable=False, index=True)  # "admin", "vendor", "runner", "customer", "system"
    actor_id = Column(String(100), nullable=True, index=True)
    target_entity = Column(String(50), nullable=True, index=True)  # "order", "store", "runner", "kyc", "payout"
    target_id = Column(String(100), nullable=True, index=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)



class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    token_hash = Column(String(64), unique=True, index=True, nullable=False)
    revoked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    reason = Column(String(255), nullable=True)


class ProcessedWebhookEvent(Base):
    __tablename__ = "processed_webhook_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event_id = Column(String(100), unique=True, index=True, nullable=False)
    event_type = Column(String(100), nullable=True)
    processed_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Replacement(Base):
    __tablename__ = "replacements"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    replacement_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g. "REP-847291"
    original_order_id = Column(String(50), ForeignKey("orders.id"), nullable=False, index=True)
    ticket_id = Column(String(50), nullable=True, index=True)
    original_order_item_id = Column(Integer, nullable=True)
    replacement_product_id = Column(String(50), ForeignKey("products.id"), nullable=False)
    product_name = Column(String(150), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    item_price = Column(Float, default=0.0)
    reason = Column(String(100), nullable=False)
    preferred_resolution = Column(String(30), default="replacement")
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    customer_phone = Column(String(20), nullable=False, index=True)
    customer_name = Column(String(100), nullable=True)
    store_id = Column(String(50), ForeignKey("stores.id"), nullable=False, index=True)
    store_name = Column(String(150), nullable=True)
    runner_id = Column(String(50), ForeignKey("runners.id"), nullable=True, index=True)
    runner_name = Column(String(100), nullable=True)
    runner_phone = Column(String(20), nullable=True)
    inventory_reservation = Column(Boolean, default=False)
    replacement_cost_paise = Column(Integer, default=0)
    customer_charge_paise = Column(Integer, default=0)  # Free replacement: strictly 0
    approved_by = Column(String(50), nullable=True)
    approval_timestamp = Column(DateTime, nullable=True)
    responsible_party = Column(String(30), default="unclear")  # "vendor", "runner", "platform", "unclear", "customer"
    status = Column(String(30), default="REQUESTED", index=True)
    # Statuses: REQUESTED, VERIFYING, APPROVED, VENDOR_PACKING, RUNNER_ASSIGNED, OUT_FOR_DELIVERY, REPLACED, REJECTED, STOCK_UNAVAILABLE, FAILED, REFUND_OFFERED, CANCELLED
    promised_eta = Column(String(50), default="45 Mins")
    actual_delivery_timestamp = Column(DateTime, nullable=True)
    delivery_verification = Column(String(10), nullable=True)  # 4-digit OTP
    reverse_pickup_required = Column(Boolean, default=False)
    reverse_pickup_status = Column(String(30), default="NOT_REQUIRED")
    # Reverse statuses: NOT_REQUIRED, PENDING_PICKUP, PICKED_UP, QUARANTINED, DISPOSED, RETURNED_TO_VENDOR
    admin_notes = Column(Text, nullable=True)
    evidence_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow)


class RefundRecord(Base):
    __tablename__ = "refund_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    refund_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g. "REF-109284"
    order_id = Column(String(50), ForeignKey("orders.id"), nullable=False, index=True)
    ticket_id = Column(String(50), nullable=True, index=True)
    replacement_id = Column(String(50), nullable=True, index=True)
    user_phone = Column(String(20), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    amount_paise = Column(Integer, nullable=False)
    reason = Column(String(100), nullable=False)
    payment_mode = Column(String(20), default="UPI")  # "UPI", "CARD", "COD"
    original_razorpay_payment_id = Column(String(100), nullable=True)
    razorpay_refund_id = Column(String(100), nullable=True)
    status = Column(String(30), default="REQUESTED", index=True)
    # Statuses: REQUESTED, UNDER_REVIEW, APPROVED, INITIATED, PROCESSING, PROCESSED, FAILED, REJECTED
    responsible_party = Column(String(30), default="unclear")
    reimbursement_method = Column(String(30), default="ORIGINAL_SOURCE")  # "ORIGINAL_SOURCE", "UPI_DIRECT", "CASH_RETURN", "STORE_CREDIT"
    reimbursement_destination = Column(String(100), nullable=True)
    approved_by = Column(String(50), nullable=True)
    approval_timestamp = Column(DateTime, nullable=True)
    admin_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow)
