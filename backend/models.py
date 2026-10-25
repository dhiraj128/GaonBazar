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
    session_token = Column(String(100), unique=True, index=True, nullable=True)
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
    district = Column(String(100), nullable=True)
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
    bank_account_number = Column(String(50), nullable=True, default=None)
    bank_ifsc = Column(String(20), nullable=True, default=None)
    bank_verification_status = Column(String(20), default="pending")  # "pending", "verified", "rejected"
    status = Column(String(30), default="approved")  # "approved", "pending_approval", "rejected"
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

    store = relationship("Store", back_populates="products")


class Order(Base):
    __tablename__ = "orders"

    id = Column(String(50), primary_key=True, index=True)  # e.g. "#RUR-9482"
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_phone = Column(String(15), nullable=False)
    user_name = Column(String(100), nullable=False)
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
    paid_at = Column(DateTime, nullable=True)
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
    bank_account_number = Column(String(50), nullable=True, default=None)
    bank_ifsc = Column(String(20), nullable=True, default=None)
    bank_verification_status = Column(String(20), default="pending")  # "pending", "verified", "rejected"
    status = Column(String(30), default="approved")  # "approved", "pending_approval", "rejected"
    is_online = Column(Boolean, default=True)
    rating = Column(Float, default=4.9)
    total_completed_missions = Column(Integer, default=142)
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
    route_transfer_status = Column(String(30), default="prepared")  # "prepared", "settled"

    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="transactions")




