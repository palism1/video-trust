# Video-Trust (MVP)

**Goal:** Classify video news for political lean & reliability; extract claims and check evidence.

## Quickstart
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
make ingest     # downloads raw videos (stub)
make asr        # runs Whisper to get transcripts
make train      # trains text-only baseline
make serve      # starts FastAPI at http://localhost:8000