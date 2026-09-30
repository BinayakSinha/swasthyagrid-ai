import os
from dataclasses import dataclass
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError: pass
@dataclass
class Settings:
    api_key: str = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    model: str = os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"
    vertex: bool = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "false").lower() == "true"
    project: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    location: str = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
    def gemini_configured(self): return bool(self.api_key) if not self.vertex else bool(self.project)
def settings(): return Settings()
