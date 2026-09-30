from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.store import STORE as S
from backend.gemini import copilot
app = FastAPI(title="SwasthyaGrid AI (prototype, synthetic data)")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])
class Chat(BaseModel): message: str
def _phc(pid):
    p = dict(S.phcs[pid]); p["risk"] = S.phc_risk(pid); return p
@app.get("/api/health")
def health(): return dict(status="ok", gemini_configured=copilot.settings().gemini_configured())
@app.get("/api/dashboard")
def dashboard():
    ph = [_phc(p) for p in S.phcs]; tb = sum(p["beds"] for p in ph)
    return dict(total_phcs=len(ph), high_risk_phcs=sum(p["risk"] in ("HIGH", "CRITICAL") for p in ph),
        available_beds=S.metrics()["available_beds"], total_beds=tb, avg_attendance=round(sum(p["attendance_pct"] for p in ph)/len(ph), 1),
        medicine_coverage_pct=round(100*sum(r["risk"] in ("LOW", "STABLE") for r in S.risks)/len(S.risks), 1),
        phcs=ph, risks=[r for r in S.risks if r["risk"] in ("CRITICAL", "HIGH")], recommendations=S.recs[:5], simulation=S.sim)
@app.get("/api/phcs")
def phcs(): return [_phc(p) for p in S.phcs]
@app.get("/api/phcs/{pid}")
def phc(pid: str):
    if pid not in S.phcs: raise HTTPException(404, "PHC not found")
    return dict(phc=_phc(pid), inventory=[dict(r, **S.inv[(pid, r["medicine"])]) for r in S.risks if r["phc_id"] == pid])
@app.get("/api/inventory")
def inventory(): return list(S.inv.values())
@app.get("/api/inventory/{mid}")
def inventory_med(mid: str):
    rows = [r for r in S.risks if r["medicine"] == mid.upper()]
    if not rows: raise HTTPException(404, "Medicine not found")
    return rows
@app.get("/api/forecasts")
def forecasts(): return [dict(phc_id=p, medicine=m, forecast=v) for (p, m), v in S.fc.items()]
@app.get("/api/risks")
def risks(): return S.risks
@app.get("/api/redistribution")
def redistribution(): return S.recs
@app.post("/api/simulation/outbreak")
def outbreak(): return S.outbreak()
@app.post("/api/simulation/reset")
def reset(): S.reset(); return dict(status="reset")
@app.post("/api/copilot/chat")
def chat(c: Chat): return copilot.chat(c.message)
@app.get("/api/alerts")
def alerts(): return [dict(severity=r["risk"], phc_id=r["phc_id"], message=f"{r['medicine']}: {r['reason']}") for r in S.risks if r["risk"] in ("CRITICAL", "HIGH")]
@app.get("/api/history")
def history():
    out = {}
    for (p, m), g in S.hist.sort_values("date").groupby(["phc_id", "medicine_id"]): out[f"{p}|{m}"] = [round(float(x), 1) for x in g.consumed.tail(14)]
    return out
