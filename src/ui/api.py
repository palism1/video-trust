# src/ui/api.py
from fastapi import FastAPI

from src.common.logging_utils import get_logger

app = FastAPI(title="Video-Trust API")  # <-- this name must be `app`
log = get_logger("api", "INFO")

@app.get("/health")
def health():
    return {"status": "ok"}
