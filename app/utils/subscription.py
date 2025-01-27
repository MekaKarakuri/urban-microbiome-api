from datetime import datetime, timedelta
from ..models import UserSubscription, SubscriptionUsage, PlanTier

def check_subscription_limits(subscription: UserSubscription) -> bool:
    plan_limits = {
        PlanTier.BASIC: 1000,
        PlanTier.PRO: 5000,
        PlanTier.ENTERPRISE: 50000
    }
    return subscription.requests_used < plan_limits[subscription.plan]

def get_subscription_usage(subscription: UserSubscription) -> SubscriptionUsage:
    plan_limits = {
        PlanTier.BASIC: 1000,
        PlanTier.PRO: 5000,
        PlanTier.ENTERPRISE: 50000
    }
    limit = plan_limits[subscription.plan]
    remaining = limit - subscription.requests_used
    days_until = (subscription.current_period_end - datetime.utcnow()).days
    
    return SubscriptionUsage(
        requests_used=subscription.requests_used,
        requests_limit=limit,
        remaining_requests=remaining,
        days_until_renewal=days_until
    )