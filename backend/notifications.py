"""
GaonBazaar Real In-App & Push Notification Engine
=================================================
Provides persistent, backend-backed notifications for:
- Customers (order placed, vendor accepted, packed, runner assigned, out for delivery, delivered, payments)
- Vendors (new order, customer cancellation, runner assigned, arriving, pickup confirmation, low stock, payout)
- Runners (new mission, reassigned, pickup ready, delivery instructions, OTP verification, earnings)
- Super Admin (pending approvals, operational exceptions, failed settlements, security alerts)

Supports bilingual notifications (English & Hindi) and read/unread state management.
"""

from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
import uuid
import logging
from sqlalchemy.orm import Session
from sqlalchemy import desc

try:
    from backend.models import Notification
except ImportError:
    from .models import Notification

logger = logging.getLogger("gaonbazar.notifications")

# In-memory store for Web Push subscriptions (or database backed)
_WEB_PUSH_SUBSCRIPTIONS: Dict[str, List[Dict[str, Any]]] = {}


def create_notification(
    db: Session,
    user_id: Optional[str],
    user_role: str,
    title: str,
    title_hi: str,
    message: str,
    message_hi: str,
    notification_type: str,
    order_id: Optional[str] = None
) -> Notification:
    """
    Creates and persists a real notification record in the database.
    """
    notif_id = f"ntf_{uuid.uuid4().hex[:12]}"
    notif = Notification(
        id=notif_id,
        user_id=user_id,
        user_role=user_role,
        order_id=order_id,
        title=title,
        title_hi=title_hi,
        message=message,
        message_hi=message_hi,
        notification_type=notification_type,
        is_read=False,
        created_at=datetime.utcnow()
    )
    db.add(notif)
    try:
        db.commit()
        db.refresh(notif)
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create notification {notif_id}: {e}")
        raise

    logger.info(f"Notification {notif_id} dispatched to {user_role} ({user_id}): {title}")
    return notif


def get_user_notifications(
    db: Session,
    user_id: Optional[str] = None,
    user_role: Optional[str] = None,
    unread_only: bool = False,
    limit: int = 50
) -> Tuple[List[Notification], int, int]:
    """
    Retrieves notifications for a specific user and role.
    Returns: (notifications_list, unread_count, total_count)
    """
    query = db.query(Notification)
    if user_role:
        query = query.filter(Notification.user_role == user_role)
    if user_id:
        query = query.filter((Notification.user_id == user_id) | (Notification.user_id.is_(None)))

    total_count = query.count()
    unread_count = query.filter(Notification.is_read == False).count()

    if unread_only:
        query = query.filter(Notification.is_read == False)

    notifications = query.order_by(desc(Notification.created_at)).limit(limit).all()
    return notifications, unread_count, total_count


def mark_notification_as_read(
    db: Session,
    notification_id: str,
    user_id: Optional[str] = None,
    user_role: Optional[str] = None
) -> Optional[Notification]:
    """
    Marks a single notification as read with tenant authorization.
    """
    query = db.query(Notification).filter(Notification.id == notification_id)
    if user_role and user_role != "admin":
        query = query.filter(Notification.user_role == user_role)
    if user_id and user_role != "admin":
        query = query.filter((Notification.user_id == user_id) | (Notification.user_id.is_(None)))

    notif = query.first()
    if notif:
        notif.is_read = True
        db.commit()
        db.refresh(notif)
    return notif


def mark_all_notifications_as_read(
    db: Session,
    user_id: Optional[str] = None,
    user_role: Optional[str] = None
) -> int:
    """
    Marks all notifications matching user/role as read.
    Returns count of updated notifications.
    """
    query = db.query(Notification).filter(Notification.is_read == False)
    if user_role:
        query = query.filter(Notification.user_role == user_role)
    if user_id:
        query = query.filter((Notification.user_id == user_id) | (Notification.user_id.is_(None)))

    updated = query.update({"is_read": True}, synchronize_session=False)
    db.commit()
    return updated


# =============================================================================
# EVENT-SPECIFIC NOTIFICATION DISPATCHERS
# =============================================================================

def notify_order_placed(db: Session, order, store_name: str) -> None:
    """Dispatches real notifications when customer places an order."""
    # 1. Customer notification
    create_notification(
        db=db,
        user_id=order.user_phone,
        user_role="customer",
        order_id=order.id,
        notification_type="order_placed",
        title=f"Order Placed #{order.id}",
        title_hi=f"ऑर्डर दर्ज हुआ #{order.id}",
        message=f"Your order {order.id} for ₹{order.total_amount:.2f} has been placed with {store_name}.",
        message_hi=f"आपका ₹{order.total_amount:.2f} का ऑर्डर {order.id} {store_name} को भेज दिया गया है।"
    )

    # 2. Vendor notification
    create_notification(
        db=db,
        user_id=order.store_id,
        user_role="vendor",
        order_id=order.id,
        notification_type="new_order",
        title=f"New Order Received #{order.id}",
        title_hi=f"नया ऑर्डर प्राप्त हुआ #{order.id}",
        message=f"New order {order.id} for ₹{order.total_amount:.2f} received. Please review and pack items.",
        message_hi=f"नया ऑर्डर {order.id} (₹{order.total_amount:.2f}) प्राप्त हुआ। कृपया सामान पैक करें।"
    )

    # 3. Super Admin notification
    notify_admin_new_order(db, order, store_name)


def notify_order_packed(db: Session, order, runner_id: Optional[str] = None) -> None:
    """Dispatches real notifications when vendor packs the order."""
    # 1. Customer notification
    create_notification(
        db=db,
        user_id=order.user_phone,
        user_role="customer",
        order_id=order.id,
        notification_type="order_packed",
        title=f"Order Packed #{order.id}",
        title_hi=f"ऑर्डर पैक हो गया #{order.id}",
        message=f"Your order {order.id} is packed and ready for delivery partner pickup.",
        message_hi=f"आपका ऑर्डर {order.id} पैक हो चुका है और डिलीवरी मित्र के पिकअप हेतु तैयार है।"
    )

    # 2. Runner notification (mission ready)
    target_runner = runner_id or getattr(order, "runner_id", None) or "gm_1"
    create_notification(
        db=db,
        user_id=target_runner,
        user_role="runner",
        order_id=order.id,
        notification_type="mission_ready",
        title=f"Delivery Mission Ready #{order.id}",
        title_hi=f"डिलीवरी मिशन तैयार #{order.id}",
        message=f"Order {order.id} at {order.store_name} is packed and ready for pickup.",
        message_hi=f"{order.store_name} पर ऑर्डर {order.id} पैक है। कृपया पिकअप करें।"
    )


def notify_runner_out_for_delivery(db: Session, order, runner_name: str) -> None:
    """Dispatches notifications when runner picks up the parcel and is out for delivery."""
    create_notification(
        db=db,
        user_id=order.user_phone,
        user_role="customer",
        order_id=order.id,
        notification_type="out_for_delivery",
        title=f"Out for Delivery #{order.id}",
        title_hi=f"डिलीवरी के लिए रवाना #{order.id}",
        message=f"Delivery Partner {runner_name} has picked up your order {order.id} and is on the way.",
        message_hi=f"डिलीवरी मित्र {runner_name} आपका ऑर्डर {order.id} लेकर निकल चुके हैं।"
    )


def notify_order_delivered(db: Session, order, runner_name: str) -> None:
    """Dispatches notifications when delivery is completed via OTP verification."""
    # 1. Customer notification
    create_notification(
        db=db,
        user_id=order.user_phone,
        user_role="customer",
        order_id=order.id,
        notification_type="delivered",
        title=f"Order Delivered #{order.id}",
        title_hi=f"ऑर्डर डिलीवर हुआ #{order.id}",
        message=f"Your order {order.id} has been delivered successfully. Thank you for choosing GaonBazaar!",
        message_hi=f"आपका ऑर्डर {order.id} सफलतापूर्वक डिलीवर हो गया है। गांवबाज़ार से जुड़ने के लिए धन्यवाद!"
    )

    # 2. Vendor notification
    create_notification(
        db=db,
        user_id=order.store_id,
        user_role="vendor",
        order_id=order.id,
        notification_type="order_completed",
        title=f"Order Completed #{order.id}",
        title_hi=f"ऑर्डर पूरा हुआ #{order.id}",
        message=f"Order {order.id} has been delivered. Product payout of ₹{order.vendor_payout:.2f} is queued for settlement.",
        message_hi=f"ऑर्डर {order.id} डिलीवर हो गया। ₹{order.vendor_payout:.2f} का भुगतान निपटान के लिए तैयार है।"
    )

    # 3. Runner notification
    runner_id = getattr(order, "runner_id", None) or "gm_1"
    create_notification(
        db=db,
        user_id=runner_id,
        user_role="runner",
        order_id=order.id,
        notification_type="delivery_payout_credited",
        title=f"Mission Completed #{order.id}",
        title_hi=f"मिशन संपन्न #{order.id}",
        message=f"Delivery completed! Delivery payout of ₹{order.runner_payout:.2f} credited to your earnings.",
        message_hi=f"डिलीवरी सफल! ₹{order.runner_payout:.2f} की डिलीवरी कमाई आपके खाते में दर्ज हो गई।"
    )


def notify_payout_settlement(
    db: Session,
    user_id: str,
    user_role: str,
    amount: float,
    order_id: str,
    status: str,
    transfer_id: Optional[str] = None
) -> None:
    """Dispatches notifications on payment split settlement state changes."""
    if status in ("settled", "processed"):
        title_en = f"Payout Processed for #{order_id}"
        title_hi = f"भुगतान निपटान पूरा #{order_id}"
        msg_en = f"Payout of ₹{amount:.2f} for order {order_id} has been processed via Razorpay Route (ID: {transfer_id or 'trf_direct'})."
        msg_hi = f"ऑर्डर {order_id} के लिए ₹{amount:.2f} का भुगतान रेज़रपे रूट द्वारा भेजा गया है।"
        ntype = "payout_settled"
    else:
        title_en = f"Payout Failed for #{order_id}"
        title_hi = f"भुगतान विफल #{order_id}"
        msg_en = f"Payout transfer of ₹{amount:.2f} for order {order_id} could not be completed. Our team is investigating."
        msg_hi = f"ऑर्डर {order_id} के ₹{amount:.2f} का भुगतान पूरा नहीं हो सका। टीम समीक्षा कर रही है।"
        ntype = "payout_failed"

    create_notification(
        db=db,
        user_id=user_id,
        user_role=user_role,
        order_id=order_id,
        notification_type=ntype,
        title=title_en,
        title_hi=title_hi,
        message=msg_en,
        message_hi=msg_hi
    )


def notify_admin_new_order(db: Session, order, store_name: str) -> None:
    """Dispatches notification to Super Admin on new platform order placement."""
    create_notification(
        db=db,
        user_id=None,
        user_role="admin",
        order_id=order.id,
        notification_type="admin_new_order",
        title=f"New Platform Order #{order.id}",
        title_hi=f"नया प्लेटफ़ॉर्म ऑर्डर #{order.id}",
        message=f"Order {order.id} placed at {store_name} for ₹{order.total_amount:.2f}.",
        message_hi=f"{store_name} पर नया ऑर्डर {order.id} (₹{order.total_amount:.2f}) प्राप्त हुआ।"
    )


def notify_admin_vendor_registered(db: Session, store) -> None:
    """Dispatches notification to Super Admin on new vendor KYC application."""
    create_notification(
        db=db,
        user_id=None,
        user_role="admin",
        order_id=None,
        notification_type="vendor_kyc_submitted",
        title=f"New Vendor KYC: {store.name}",
        title_hi=f"नया दुकानदार आवेदन: {store.name}",
        message=f"Store '{store.name}' (ID: {store.id}) submitted KYC registration awaiting review.",
        message_hi=f"दुकान '{store.name}' (ID: {store.id}) ने सत्यापन हेतु आवेदन जमा किया है।"
    )


def notify_admin_runner_registered(db: Session, runner) -> None:
    """Dispatches notification to Super Admin on new runner KYC application."""
    create_notification(
        db=db,
        user_id=None,
        user_role="admin",
        order_id=None,
        notification_type="runner_kyc_submitted",
        title=f"New Gaon Mitra KYC: {runner.name}",
        title_hi=f"नया गाँव मित्र आवेदन: {runner.name}",
        message=f"Runner '{runner.name}' (Phone: {runner.phone}) submitted KYC registration awaiting review.",
        message_hi=f"गाँव मित्र '{runner.name}' (मोबाइल: {runner.phone}) ने सत्यापन हेतु आवेदन जमा किया है।"
    )


def notify_vendor_kyc_status(db: Session, store_id: str, status: str, store_name: str) -> None:
    """Dispatches notification to vendor when admin approves/rejects KYC."""
    if status == "approved":
        create_notification(
            db=db,
            user_id=store_id,
            user_role="vendor",
            notification_type="kyc_approved",
            title="Shop Approved & Activated!",
            title_hi="दुकान सत्यापित एवं स्वीकृत!",
            message=f"Congratulations! Your shop '{store_name}' has been verified and approved by GaonBazaar Admin.",
            message_hi=f"बधाई हो! आपकी दुकान '{store_name}' का सत्यापन पूर्ण हुआ और दुकान चालू कर दी गई है।"
        )
    else:
        create_notification(
            db=db,
            user_id=store_id,
            user_role="vendor",
            notification_type="kyc_rejected",
            title="Shop Verification Update",
            title_hi="दुकान सत्यापन सूचना",
            message=f"Your shop registration for '{store_name}' was rejected or needs document corrections.",
            message_hi=f"आपकी दुकान '{store_name}' का सत्यापन आवेदन अस्वीकृत हुआ है। कृपया विवरण जांचें।"
        )


def notify_runner_kyc_status(db: Session, runner_id: str, status: str, runner_name: str) -> None:
    """Dispatches notification to runner when admin approves/rejects KYC."""
    if status == "approved":
        create_notification(
            db=db,
            user_id=runner_id,
            user_role="runner",
            notification_type="kyc_approved",
            title="Gaon Mitra Approved!",
            title_hi="गाँव मित्र सत्यापन स्वीकृत!",
            message=f"Welcome {runner_name}! Your delivery partner profile is approved. You can now accept missions.",
            message_hi=f"स्वागत है {runner_name}! आपका गाँव मित्र प्रोफ़ाइल स्वीकृत हो चुका है। अब आप मिशन शुरू कर सकते हैं।"
        )
    else:
        create_notification(
            db=db,
            user_id=runner_id,
            user_role="runner",
            notification_type="kyc_rejected",
            title="Gaon Mitra Application Update",
            title_hi="गाँव मित्र आवेदन सूचना",
            message=f"Your application for delivery partner '{runner_name}' was not approved.",
            message_hi=f"गाँव मित्र '{runner_name}' का आवेदन स्वीकृत नहीं हो सका।"
        )
