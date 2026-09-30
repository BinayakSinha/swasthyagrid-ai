"""Forecaster interface + local Ridge+GradientBoosting model (swap for Vertex AI behind Forecaster)."""
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.ensemble import GradientBoostingRegressor
class Forecaster:
    def forecast_all(self, hist, horizon=7): raise NotImplementedError
def _feat(vals, vis, em, sg, dow, vsc, esc):
    sc = max(np.mean(vals[-7:]), 1e-6)
    return sc, [vals[-1] / sc, vals[-3] / sc, np.mean(vals[-3:]) / sc, vis / vsc, em / esc, sg, dow]
class LocalForecaster(Forecaster):
    def forecast_all(self, hist, horizon=7):
        out = {}
        for med, mdf in hist.groupby("medicine_id"):
            X, y, groups = [], [], {}
            for pid, g in mdf.sort_values("date").groupby("phc_id"):
                c, v, e, s = (g[k].to_numpy(float) for k in ("consumed", "visits", "emerg", "signal")); dow = [d.weekday() for d in g["date"]]
                groups[pid] = (c, v, e, s, dow[-1])
                for t in range(7, len(c)):
                    sc, f = _feat(c[:t], v[t], e[t], s[t], dow[t], v[t-7:t].mean(), e[t-7:t].mean()); X.append(f); y.append(c[t] / sc)
            X, y = np.array(X), np.array(y); lin = Ridge(1.0).fit(X, y)
            gbr = GradientBoostingRegressor(n_estimators=60, max_depth=2, random_state=0).fit(X, y - lin.predict(X))
            for pid, (c, v, e, s, ld) in groups.items():
                vals, res = list(c), []; ev, ee, es = v[-3:].mean(), e[-3:].mean(), s[-3:].mean()
                for h in range(horizon):
                    sc, f = _feat(vals, ev, ee, es, (ld + h + 1) % 7, v[-7:].mean(), e[-7:].mean())
                    p = float(sc * (lin.predict([f])[0] + gbr.predict([f])[0])); vals.append(p); res.append(round(max(p, 0), 1))
                out[(pid, med)] = res
        return out
