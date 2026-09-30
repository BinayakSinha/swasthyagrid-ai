from datetime import timedelta
THRESHOLDS = [("CRITICAL", 3), ("HIGH", 5), ("MEDIUM", 8), ("LOW", 14)]   # days of stock; configurable
ORDER = ["STABLE", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
def classify(days):
    for level, limit in THRESHOLDS:
        if days <= limit: return level
    return "STABLE"
def assess(phc_id, medicine, stock, demand, today):
    days = stock / max(demand, 1e-6); risk = classify(days)
    return dict(phc_id=phc_id, medicine=medicine, current_stock=stock, predicted_daily_demand=round(demand, 1),
        days_remaining=round(days, 1), risk=risk, predicted_stockout_date=str(today + timedelta(days=int(days))),
        reason=f"{stock} units at {demand:.0f}/day forecast demand = {days:.1f} days of stock -> {risk}")
