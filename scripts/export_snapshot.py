import sys, pathlib, json; sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from fastapi.testclient import TestClient
from backend.main import app
c = TestClient(app); g = lambda p: c.get(p).json()
json.dump(dict(phcs=g("/api/phcs"), risks=g("/api/risks"), recs=g("/api/redistribution"), forecasts=g("/api/forecasts"), history=g("/api/history")),
          open(pathlib.Path(__file__).parent.parent / "frontend/src/data/snapshot.json", "w"))
