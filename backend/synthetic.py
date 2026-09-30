"""Deterministic SYNTHETIC data. No real patient data."""
import numpy as np, pandas as pd
from datetime import date, timedelta
DISTRICTS = {"Hyderabad Rural": ("HR", 17.25, 78.40, 7), "Medak": ("MED", 18.04, 78.26, 7), "Nalgonda": ("NAL", 17.05, 79.27, 6)}
MEDS = {"ORS": .5, "PARACETAMOL": .8, "AZITHROMYCIN": .15, "AMOXICILLIN": .2, "IV_FLUIDS": .05}
STOCK = {("HR-07", "ORS"): 1240, ("MED-03", "ORS"): 6500, ("NAL-04", "ORS"): 4500}   # demo scenario
COVER = {("NAL-01", "IV_FLUIDS"): 2.0, ("MED-06", "PARACETAMOL"): 3.5}              # forced shortages (days)
TODAY = date(2026, 9, 30)

def generate(seed=7, days=30):
    r = np.random.default_rng(seed); phcs, rows, inv = [], [], []
    ds = [TODAY - timedelta(d) for d in range(days, 0, -1)]
    for dn, (p, la, lo, n) in DISTRICTS.items():
        for i in range(1, n + 1):
            pid = f"{p}-{i:02d}"; base = 560 if pid == "HR-07" else r.uniform(150, 320)
            beds = int(r.integers(8, 31))
            phcs.append(dict(id=pid, name=f"{dn} PHC {i:02d}", district=dn, state="Telangana", lat=la + r.uniform(-.12, .12),
                lon=lo + r.uniform(-.12, .12), population_served=int(base * 180), beds=beds, occupied_beds=int(beds * r.uniform(.4, .8)),
                staff_count=int(r.integers(6, 16)), doctors=int(r.integers(1, 4)), nurses=int(r.integers(2, 7)),
                pharmacists=1, attendance_pct=round(float(r.uniform(70, 98)), 1)))
            series = {m: [] for m in MEDS}
            for d in ds:
                vis = base * (1 + .1 * np.sin(d.weekday())) * r.uniform(.93, 1.07); em = base * .04 * r.uniform(.8, 1.2)
                sg = float(np.clip(.15 + r.normal(0, .04), 0, 1))
                for m, rate in MEDS.items():
                    c = rate * (vis + 3 * em) * (1 + .6 * sg) * r.uniform(.93, 1.07)
                    rows.append((d, pid, m, c, vis, em, sg)); series[m].append(c)
            for m in MEDS:
                avg = float(np.mean(series[m][-7:]))
                stock = STOCK.get((pid, m)) or avg * COVER.get((pid, m), r.uniform(9, 25))
                inv.append(dict(phc_id=pid, medicine_id=m, current_stock=int(stock), daily_consumption=int(avg),
                    minimum_stock=int(avg * 5), reorder_level=int(avg * 8), expiry_risk=str(r.choice(["LOW", "LOW", "MEDIUM", "HIGH"]))))
    hist = pd.DataFrame(rows, columns=["date", "phc_id", "medicine_id", "consumed", "visits", "emerg", "signal"])
    return dict(phcs=phcs, hist=hist, inventory=inv)
