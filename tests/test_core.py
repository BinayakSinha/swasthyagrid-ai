import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.risk import classify
from backend.gemini import copilot
c = TestClient(app)
def test_risk(): assert [classify(d) for d in (2, 4, 7, 12, 30)] == ["CRITICAL", "HIGH", "MEDIUM", "LOW", "STABLE"]
def test_demo_scenario():
    c.post("/api/simulation/reset"); r = c.get("/api/risks").json()
    hr = next(x for x in r if x["phc_id"] == "HR-07" and x["medicine"] == "ORS")
    assert hr["risk"] in ("HIGH", "CRITICAL") and 3 <= hr["days_remaining"] <= 5.5
    assert any(x["risk"] == "CRITICAL" for x in r)
    rec = [x for x in c.get("/api/redistribution").json() if x["destination"] == "HR-07" and x["resource"] == "ORS"]
    assert {x["source"] for x in rec} & {"MED-03", "NAL-04"} and rec[0]["quantity"] > 0
def test_simulation_and_reset():
    c.post("/api/simulation/reset"); s = c.post("/api/simulation/outbreak").json()
    assert s["after"]["footfall"] > s["before"]["footfall"] and s["after"]["available_beds"] < s["before"]["available_beds"]
    assert s["after"]["critical_phcs"] >= s["before"]["critical_phcs"]
    c.post("/api/simulation/reset"); assert c.get("/api/dashboard").json()["simulation"] is None
def test_endpoints():
    assert c.get("/api/health").status_code == 200 and c.get("/api/phcs/HR-07").status_code == 200
    assert c.get("/api/phcs/XX").status_code == 404 and len(c.get("/api/phcs").json()) == 20
def test_copilot_mock():
    m = MagicMock(); m.models.generate_content.return_value.text = "ok"
    assert copilot.chat("hi", client=m)["ok"]
    m.models.generate_content.side_effect = RuntimeError("x"); assert not copilot.chat("hi", client=m)["ok"]
