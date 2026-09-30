"""Transparent weighted scoring (NOT an optimizer): urgency 40 + surplus coverage 30 + proximity 20 + demand 10."""
import math
URGENT = {"CRITICAL": 1.0, "HIGH": .75, "MEDIUM": .5}
TARGET_DAYS, SAFE_DAYS = 10, 10
def km(a, b):
    p = math.pi / 180; h = math.sin((b["lat"]-a["lat"])*p/2)**2 + math.cos(a["lat"]*p)*math.cos(b["lat"]*p)*math.sin((b["lon"]-a["lon"])*p/2)**2
    return 12742 * math.asin(math.sqrt(h))
def recommend(risks, inv, phcs):
    by = {(r["phc_id"], r["medicine"]): r for r in risks}; recs = []
    for r in risks:
        if r["risk"] not in URGENT: continue
        need = TARGET_DAYS * r["predicted_daily_demand"] - r["current_stock"]; dst = phcs[r["phc_id"]]
        for (pid, med), s in by.items():
            if med != r["medicine"] or pid == r["phc_id"]: continue
            surplus = s["current_stock"] - SAFE_DAYS * s["predicted_daily_demand"]
            if surplus <= 0: continue
            qty = int(min(need, surplus)); d = km(phcs[pid], dst)
            score = 40*URGENT[r["risk"]] + 30*min(surplus/need, 1) + 20*max(0, 1-d/200) + 10*min(r["predicted_daily_demand"]/500, 1)
            recs.append(dict(source=pid, source_name=phcs[pid]["name"], destination=r["phc_id"], destination_name=dst["name"],
                resource=med, quantity=qty, distance_km=round(d, 1), score=round(score, 1), reasons=[
                f"Destination projected to stock out in {r['days_remaining']} days ({r['risk']})",
                f"Source keeps {SAFE_DAYS} days of safety stock and still has {int(surplus)} units surplus",
                f"Distance {d:.0f} km", f"Transfer of {qty} units restores destination toward {TARGET_DAYS} days cover"]))
    return sorted(recs, key=lambda x: -x["score"])
