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

## Scope (Day 0)
This project analyzes **facts & source reliability** in video news.
We do **not** classify political lean.
Inputs/outputs are defined in `docs/SCHEMA.md`.
Day 1 will start ETL and ASR.