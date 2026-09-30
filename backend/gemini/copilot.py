"""Gemini copilot: model calls backend tool functions; it never receives the whole database."""
from backend.config import settings
from backend.store import STORE as S
SYSTEM = ("You are SwasthyaGrid AI Operations Copilot. You assist authorized healthcare resource administrators. Analyze only data returned by your tools. "
 "Never invent inventory, patient, staffing, bed, forecast, or redistribution values. Distinguish observed data, model predictions, and recommended actions. "
 "Recommendations are decision support and do not replace qualified healthcare or government decisions. Be concise and factual. All data is synthetic.")
def get_phc_status(phc_id: str) -> dict:
    """Get PHC profile, beds, staffing and all medicine risks for a PHC id like HR-07."""
    return dict(phc=S.phcs.get(phc_id), risks=[r for r in S.risks if r["phc_id"] == phc_id])
def get_high_risk_phcs() -> list:
    """List CRITICAL/HIGH risk medicine entries across PHCs."""
    return [r for r in S.risks if r["risk"] in ("CRITICAL", "HIGH")]
def get_medicine_inventory(medicine: str) -> list:
    """Stock and days remaining for one medicine (e.g. ORS) at every PHC."""
    return [r for r in S.risks if r["medicine"] == medicine.upper()]
def get_stockout_predictions() -> list:
    """Predicted stock-outs (CRITICAL, HIGH, MEDIUM) sorted by days remaining."""
    return sorted([r for r in S.risks if r["risk"] in ("CRITICAL", "HIGH", "MEDIUM")], key=lambda r: r["days_remaining"])
def get_surplus_locations(medicine: str) -> list:
    """Redistribution sources with surplus stock for a medicine."""
    return [dict(source=r["source"], quantity=r["quantity"]) for r in S.recs if r["resource"] == medicine.upper()]
def get_redistribution_recommendation(phc_id: str, medicine: str) -> list:
    """Ranked, explainable transfer recommendations into a PHC for a medicine."""
    return [r for r in S.recs if r["destination"] == phc_id and r["resource"] == medicine.upper()][:3]
def get_emergency_status() -> dict:
    """Outbreak simulation status with before/after metrics."""
    return S.sim or dict(active=False, current=S.metrics())
def get_demand_forecast(phc_id: str, medicine: str) -> dict:
    """7-day forecast demand for a PHC and medicine."""
    return dict(phc_id=phc_id, medicine=medicine.upper(), forecast=S.fc.get((phc_id, medicine.upper())))
TOOLS = [get_phc_status, get_high_risk_phcs, get_medicine_inventory, get_stockout_predictions, get_surplus_locations,
         get_redistribution_recommendation, get_emergency_status, get_demand_forecast]
def _client(cfg):
    from google import genai
    return genai.Client(vertexai=True, project=cfg.project, location=cfg.location) if cfg.vertex else genai.Client(api_key=cfg.api_key)
def chat(question: str, client=None) -> dict:
    cfg = settings()
    if client is None and not cfg.gemini_configured():
        return dict(answer="Gemini is not configured. Set GEMINI_API_KEY or configure Vertex AI.", ok=False)
    try:
        from google.genai import types
        r = (client or _client(cfg)).models.generate_content(model=cfg.model, contents=question,
            config=types.GenerateContentConfig(system_instruction=SYSTEM, tools=TOOLS))
        return dict(answer=r.text, ok=True)
    except Exception as e:
        return dict(answer=f"Copilot unavailable ({type(e).__name__}). Dashboard data is unaffected.", ok=False)
