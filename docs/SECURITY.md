## Security & Privacy (MVP)
- No PII collection; store only public video metadata/transcripts.
- Secrets via `.env` only; never commit creds.
- Respect robots.txt / platform ToS.
- Input sanitization for URLs; validate schemes (https only).
- License third-party models/datasets; track at `/docs/DATASET_CARD.md`.