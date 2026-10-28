"""
GaonBazaar Centralized Delivery Economics & Pricing Engine
==========================================================
Single-source-of-truth pricing engine for:
- Customer checkout & cart estimation
- Razorpay order creation & zero-trust total verification
- Vendor product settlement (100% of product subtotal)
- Runner delivery payout based on distance tiers
- Super Admin platform revenue & commission ledger
- Delivery discount promotions with documented funding source

Uses exact integer arithmetic (paise) to guarantee zero float rounding errors.
1 INR = 100 paise.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, NamedTuple, Optional, Tuple
import math
import os


class PricingTier(NamedTuple):
    tier_id: str
    min_dist_exclusive: float  # km
    max_dist_inclusive: float  # km
    delivery_charge_paise: int
    platform_delivery_share_paise: int
    runner_payout_paise: int
    eta_mins: str


# =============================================================================
# COMMERCIAL PRICING CONFIGURATION (Provisional Commercial Settings)
# =============================================================================

# Provisional tiers per owner specifications:
# 1. 0 - 2 km: Delivery charge ₹15 | Platform delivery share ₹10 | Runner payout ₹5
# 2. Above 2 - 4 km: Delivery charge ₹20 | Platform delivery share ₹10 | Runner payout ₹10
# 3. Above 4 - 5 km: Delivery charge ₹25 | Platform delivery share ₹10 | Runner payout ₹15
# 4. Above 5 - 8 km: Delivery charge ₹35 | Platform delivery share ₹10 | Runner payout ₹25
DELIVERY_TIERS: Tuple[PricingTier, ...] = (
    PricingTier(
        tier_id="tier_0_2",
        min_dist_exclusive=0.0,
        max_dist_inclusive=2.0,
        delivery_charge_paise=1500,  # ₹15
        platform_delivery_share_paise=1000,  # ₹10
        runner_payout_paise=500,  # ₹5
        eta_mins="35-45 Mins"
    ),
    PricingTier(
        tier_id="tier_2_4",
        min_dist_exclusive=2.0,
        max_dist_inclusive=4.0,
        delivery_charge_paise=2000,  # ₹20
        platform_delivery_share_paise=1000,  # ₹10
        runner_payout_paise=1000,  # ₹10
        eta_mins="40-50 Mins"
    ),
    PricingTier(
        tier_id="tier_4_5",
        min_dist_exclusive=4.0,
        max_dist_inclusive=5.0,
        delivery_charge_paise=2500,  # ₹25
        platform_delivery_share_paise=1000,  # ₹10
        runner_payout_paise=1500,  # ₹15
        eta_mins="45-55 Mins"
    ),
    PricingTier(
        tier_id="tier_5_8",
        min_dist_exclusive=5.0,
        max_dist_inclusive=8.0,
        delivery_charge_paise=3500,  # ₹35
        platform_delivery_share_paise=1000,  # ₹10
        runner_payout_paise=2500,  # ₹25
        eta_mins="50-60 Mins"
    )
)

PLATFORM_HANDLING_FEE_PAISE = 300  # Flat ₹3 per order, 100% to platform
MAX_DELIVERY_RADIUS_KM = 8.0
MINIMUM_ORDER_VALUE_PAISE = 9900  # ₹99 Minimum Order Value

# ₹299 Promotion rule:
# If subtotal >= ₹299 and distance <= 5.0 km, platform funds a flat ₹10 delivery discount.
# The discount is strictly funded by the Platform's delivery share (₹10 -> ₹0).
# The Runner's distance payout is preserved at 100% without reduction.
DELIVERY_DISCOUNT_THRESHOLD_PAISE = 29900  # ₹299
DELIVERY_DISCOUNT_AMOUNT_PAISE = 1000  # ₹10
DELIVERY_DISCOUNT_MAX_DISTANCE_KM = 5.0  # Only up to 5 km


# =============================================================================
# DISTANCE & ROUTING ENGINE
# =============================================================================

# In rural & semi-urban geography, winding village roads and field bunds typically
# result in road travel distances ~25% longer than straight-line Euclidean/Haversine.
ROAD_ROUTING_FACTOR = 1.25


def calculate_haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates great-circle distance between two GPS coordinates using the Haversine formula.
    Returns straight-line distance in kilometers rounded to 2 decimal places.
    """
    R = 6371.0  # Earth's mean radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)


def calculate_authoritative_distance_km(
    store_lat: float,
    store_lng: float,
    customer_lat: float,
    customer_lng: float
) -> Tuple[float, float, str]:
    """
    Authoritative server-side distance calculation:
    - Computes straight-line Haversine distance
    - Derives estimated road-route distance using rural road-curvature factor (1.25x)
    Returns: (road_distance_km, straight_line_km, distance_type)
    """
    straight_line_km = calculate_haversine_distance_km(store_lat, store_lng, customer_lat, customer_lng)
    road_distance_km = round(straight_line_km * ROAD_ROUTING_FACTOR, 2)
    return road_distance_km, straight_line_km, "road_routing_estimate"


def is_geofence_bypass_permitted() -> bool:
    """
    Strict production safety check for geofence bypass:
    - FORBIDDEN in production or on hosted Render environments.
    - Only allowed when explicitly set in local non-production testing.
    """
    env = os.getenv("ENVIRONMENT", "").strip().lower()
    if env in ("production", "prod") or os.getenv("RENDER") == "true":
        return False
    raw_val = os.getenv("BYPASS_GEOFENCE", "False")
    return str(raw_val).strip().lower() in ("true", "1", "yes")


# =============================================================================
# CENTRALIZED ORDER PRICING CALCULATION
# =============================================================================

class OrderPricingResult:
    def __init__(
        self,
        subtotal_paise: int,
        base_delivery_fee_paise: int,
        delivery_discount_paise: int,
        delivery_fee_charged_paise: int,
        platform_fee_paise: int,
        total_amount_paise: int,
        vendor_payout_paise: int,
        runner_payout_paise: int,
        platform_delivery_share_paise: int,
        platform_net_delivery_share_paise: int,
        platform_total_revenue_paise: int,
        discount_funded_by: Optional[str],
        tier_id: str,
        distance_km: float,
        eta_mins: str
    ):
        self.subtotal_paise = subtotal_paise
        self.base_delivery_fee_paise = base_delivery_fee_paise
        self.delivery_discount_paise = delivery_discount_paise
        self.delivery_fee_charged_paise = delivery_fee_charged_paise
        self.platform_fee_paise = platform_fee_paise
        self.total_amount_paise = total_amount_paise
        self.vendor_payout_paise = vendor_payout_paise
        self.runner_payout_paise = runner_payout_paise
        self.platform_delivery_share_paise = platform_delivery_share_paise
        self.platform_net_delivery_share_paise = platform_net_delivery_share_paise
        self.platform_total_revenue_paise = platform_total_revenue_paise
        self.discount_funded_by = discount_funded_by
        self.tier_id = tier_id
        self.distance_km = distance_km
        self.eta_mins = eta_mins

        # Reconcile exact accounting equality
        # Total collected from Customer MUST equal Vendor Payout + Runner Payout + Platform Revenue
        expected_total = self.vendor_payout_paise + self.runner_payout_paise + self.platform_total_revenue_paise
        assert self.total_amount_paise == expected_total, (
            f"Accounting mismatch: Customer Total {self.total_amount_paise} != "
            f"Vendor ({self.vendor_payout_paise}) + Runner ({self.runner_payout_paise}) + "
            f"Platform ({self.platform_total_revenue_paise}) [diff: {self.total_amount_paise - expected_total} paise]"
        )

    # Decimal / Float helpers for DTOs and serialization
    @property
    def subtotal(self) -> float:
        return round(self.subtotal_paise / 100.0, 2)

    @property
    def base_delivery_fee(self) -> float:
        return round(self.base_delivery_fee_paise / 100.0, 2)

    @property
    def delivery_discount(self) -> float:
        return round(self.delivery_discount_paise / 100.0, 2)

    @property
    def delivery_fee(self) -> float:
        return round(self.delivery_fee_charged_paise / 100.0, 2)

    @property
    def platform_fee(self) -> float:
        return round(self.platform_fee_paise / 100.0, 2)

    @property
    def total_amount(self) -> float:
        return round(self.total_amount_paise / 100.0, 2)

    @property
    def vendor_payout(self) -> float:
        return round(self.vendor_payout_paise / 100.0, 2)

    @property
    def runner_payout(self) -> float:
        return round(self.runner_payout_paise / 100.0, 2)

    @property
    def admin_profit(self) -> float:
        return round(self.platform_total_revenue_paise / 100.0, 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subtotal": self.subtotal,
            "base_delivery_fee": self.base_delivery_fee,
            "delivery_discount": self.delivery_discount,
            "delivery_fee": self.delivery_fee,
            "platform_fee": self.platform_fee,
            "total_amount": self.total_amount,
            "vendor_payout": self.vendor_payout,
            "runner_payout": self.runner_payout,
            "admin_profit": self.admin_profit,
            "distance_km": self.distance_km,
            "eta_mins": self.eta_mins,
            "discount_funded_by": self.discount_funded_by,
            "tier_id": self.tier_id,
            "paise": {
                "subtotal": self.subtotal_paise,
                "delivery_fee": self.delivery_fee_charged_paise,
                "platform_fee": self.platform_fee_paise,
                "total_amount": self.total_amount_paise,
                "vendor_payout": self.vendor_payout_paise,
                "runner_payout": self.runner_payout_paise,
                "platform_revenue": self.platform_total_revenue_paise
            }
        }


def calculate_order_pricing(
    subtotal_in_rupees: float,
    distance_km: float,
    bypass_geofence: bool = False
) -> OrderPricingResult:
    """
    Centralized pricing calculation function.
    
    Tiers:
    - 0-2 km: ₹15 delivery charge (Platform ₹10, Runner ₹5)
    - Above 2-4 km: ₹20 delivery charge (Platform ₹10, Runner ₹10)
    - Above 4-5 km: ₹25 delivery charge (Platform ₹10, Runner ₹15)
    - Above 5-8 km: ₹35 delivery charge (Platform ₹10, Runner ₹25)
    - Platform handling fee: ₹3 flat per order
    - Vendor product settlement: 100% of product subtotal (0% commission)
    - ₹299 Promotion: Flat ₹10 discount on delivery if subtotal >= ₹299 and distance <= 5 km,
      strictly funded by platform margin.
    """
    # Convert subtotal to exact integer paise
    subtotal_paise = int(Decimal(str(subtotal_in_rupees)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) * 100)

    # Validate distance boundaries
    dist = max(0.0, round(float(distance_km), 2))
    if dist > MAX_DELIVERY_RADIUS_KM and not bypass_geofence:
        raise ValueError(f"Distance {dist} km exceeds the maximum delivery radius of {MAX_DELIVERY_RADIUS_KM} km")

    # Match tier
    selected_tier: Optional[PricingTier] = None
    for tier in DELIVERY_TIERS:
        if tier.min_dist_exclusive <= dist <= tier.max_dist_inclusive:
            selected_tier = tier
            break

    if not selected_tier:
        if dist > MAX_DELIVERY_RADIUS_KM:
            # If bypass is enabled, use top tier as baseline
            selected_tier = DELIVERY_TIERS[-1]
        else:
            # Distance is exactly 0.0 or between 0 and 2.0
            selected_tier = DELIVERY_TIERS[0]

    base_delivery_fee_paise = selected_tier.delivery_charge_paise
    platform_delivery_share_paise = selected_tier.platform_delivery_share_paise
    runner_payout_paise = selected_tier.runner_payout_paise
    eta_mins = selected_tier.eta_mins

    # Evaluate ₹299 Promotion
    # Condition: Subtotal >= ₹299 AND distance <= 5.0 km
    if subtotal_paise >= DELIVERY_DISCOUNT_THRESHOLD_PAISE and dist <= DELIVERY_DISCOUNT_MAX_DISTANCE_KM:
        delivery_discount_paise = min(DELIVERY_DISCOUNT_AMOUNT_PAISE, base_delivery_fee_paise)
        discount_funded_by = "platform_promotion_budget"
    else:
        delivery_discount_paise = 0
        discount_funded_by = None

    # Delivery fee charged to customer
    delivery_fee_charged_paise = base_delivery_fee_paise - delivery_discount_paise

    # Platform handling fee
    platform_fee_paise = PLATFORM_HANDLING_FEE_PAISE

    # Total customer charge
    total_amount_paise = subtotal_paise + delivery_fee_charged_paise + platform_fee_paise

    # Vendor payout (100% of product subtotal)
    vendor_payout_paise = subtotal_paise

    # Runner payout (Full distance payout preserved, NEVER reduced by promotions)
    # Runner payout remains exactly runner_payout_paise

    # Net platform revenue:
    # Platform absorbs delivery discount from its delivery share
    platform_net_delivery_share_paise = platform_delivery_share_paise - delivery_discount_paise
    platform_total_revenue_paise = platform_net_delivery_share_paise + platform_fee_paise

    return OrderPricingResult(
        subtotal_paise=subtotal_paise,
        base_delivery_fee_paise=base_delivery_fee_paise,
        delivery_discount_paise=delivery_discount_paise,
        delivery_fee_charged_paise=delivery_fee_charged_paise,
        platform_fee_paise=platform_fee_paise,
        total_amount_paise=total_amount_paise,
        vendor_payout_paise=vendor_payout_paise,
        runner_payout_paise=runner_payout_paise,
        platform_delivery_share_paise=platform_delivery_share_paise,
        platform_net_delivery_share_paise=platform_net_delivery_share_paise,
        platform_total_revenue_paise=platform_total_revenue_paise,
        discount_funded_by=discount_funded_by,
        tier_id=selected_tier.tier_id,
        distance_km=dist,
        eta_mins=eta_mins
    )


def compute_dynamic_eta(distance_km: float, timeline_stage: int) -> str:
    """
    Computes realistic, operationally grounded ETA:
    - Stage 1 (Order Placed): initial estimate based on distance
    - Stage 2 (Accepted by Shop): 35-45 Mins
    - Stage 3 (Packed & Ready): 25-35 Mins
    - Stage 4 (Out for Delivery): 15-25 Mins
    - Stage 5 (Delivered): Delivered
    """
    if timeline_stage == 5:
        return "Delivered"
    elif timeline_stage == 4:
        return "15-25 Mins"
    elif timeline_stage == 3:
        return "25-35 Mins"
    elif timeline_stage == 2:
        return "35-45 Mins"
    else:
        dist = max(0.0, float(distance_km))
        if dist <= 2.0:
            return "35-45 Mins"
        elif dist <= 4.0:
            return "40-50 Mins"
        elif dist <= 5.0:
            return "45-55 Mins"
        else:
            return "50-60 Mins"
