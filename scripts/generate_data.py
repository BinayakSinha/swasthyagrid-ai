import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
import json, pandas as pd
from backend.synthetic import generate
d = generate(); out = pathlib.Path(__file__).parent.parent / "data"
json.dump(d["phcs"], open(out / "phcs.json", "w"), indent=1); d["hist"].to_csv(out / "historical_demand.csv", index=False)
pd.DataFrame(d["inventory"]).to_csv(out / "inventory.csv", index=False); print("wrote", out)
