# Data Schema (MVP) — Facts & Source Reliability

- video_id: str
- title: str
- channel: str
- published_at: ISO8601

- transcript:
  - { start: float, end: float, text: str, speaker?: str }

- predictions:
  - reliability_score: float [0,1]  # confidence in factual reliability for this video (MVP)

- claims:
  - { timecode: float, text: str, entities: [str], quantities: [str] }

- evidence:
  - { claim_idx: int, url: str, stance: {supports, refutes, neutral}, date: ISO8601 }