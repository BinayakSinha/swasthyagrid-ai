import numpy as np
from backend import synthetic
from backend.forecasting.model import LocalForecaster
from backend.services import risk as R
from backend.redistribution import engine
class Store:
    forecaster = LocalForecaster()
    def __init__(s): s.reset()
    def reset(s):
        d = synthetic.generate(); s.phcs = {p["id"]: p for p in d["phcs"]}; s.hist = d["hist"]
        s.inv = {(i["phc_id"], i["medicine_id"]): i for i in d["inventory"]}; s.sim = None; s._calc()
    def _calc(s):
        s.fc = s.forecaster.forecast_all(s.hist)
        s.risks = [R.assess(p, m, s.inv[(p, m)]["current_stock"], float(np.mean(v)), synthetic.TODAY) for (p, m), v in s.fc.items()]
        s.recs = engine.recommend(s.risks, s.inv, s.phcs)
    def phc_risk(s, pid):
        return max((r["risk"] for r in s.risks if r["phc_id"] == pid), key=R.ORDER.index)
    def metrics(s):
        h = s.hist; last = h[h.date >= h.date.max() - __import__("datetime").timedelta(2)]
        return dict(footfall=round(float(last.groupby("phc_id").visits.mean().sum()), 1),
            ors_demand=round(sum(float(np.mean(v)) for (p, m), v in s.fc.items() if m == "ORS"), 1),
            available_beds=sum(p["beds"] - p["occupied_beds"] for p in s.phcs.values()),
            critical_phcs=sum(s.phc_risk(p) == "CRITICAL" for p in s.phcs))
    def outbreak(s, district="Hyderabad Rural"):
        if s.sim: return s.sim
        before = s.metrics(); ids = [p for p, v in s.phcs.items() if v["district"] == district]
        m = s.hist.phc_id.isin(ids) & (s.hist.date >= s.hist.date.max() - __import__("datetime").timedelta(2))
        s.hist.loc[m, "visits"] *= 1.62; s.hist.loc[m, "emerg"] *= 1.8; s.hist.loc[m, "signal"] = .9
        s.hist.loc[m, "consumed"] *= np.where(s.hist.loc[m, "medicine_id"] == "ORS", 1.81, 1.5)
        for p in ids: s.phcs[p]["occupied_beds"] = min(s.phcs[p]["beds"], int(s.phcs[p]["occupied_beds"] * 1.3) + 2)
        s._calc(); after = s.metrics()
        s.sim = dict(district=district, before=before, after=after, change_pct={k: round(100*(after[k]-before[k])/max(before[k], 1), 1) for k in before})
        return s.sim
STORE = Store()
