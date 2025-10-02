# src/etl/ingest.py
import argparse
import hashlib
import json
import pathlib
from urllib.parse import urlparse

from src.common.logging_utils import get_logger

log = get_logger("etl.ingest", "INFO")

def hash_id(text: str) -> str:
    """Stable short ID (content-addressed) -> reproducible filenames."""
    return hashlib.sha1(text.encode()).hexdigest()[:8]

def is_valid_url(url: str) -> bool:
    """Security hygiene: accept only http(s) URLs; reject junk/empty."""
    try:
        p = urlparse(url)
        return p.scheme in {"http", "https"} and bool(p.netloc)
    except Exception:
        return False

def make_stub(vid_id: str) -> dict:
    """Minimal schema-compliant record. Downstream stages will fill fields."""
    return {
        "video_id": vid_id,
        "title": None,
        "channel": None,
        "published_at": None,
        "transcript": [],                       # ASR will populate later
        "predictions": {"reliability_score": None},
        "claims": [],                           # claim mining will populate later
        "evidence": []                          # verification will populate later
    }

def main(input_file: str, out_dir: str, force: bool = False) -> None:
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    created = skipped = invalid = 0

    for raw in pathlib.Path(input_file).read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):         # support comments / blank lines
            continue
        if not is_valid_url(line):
            log.warning("Skipping invalid URL: %s", line)
            invalid += 1
            continue

        vid_id = hash_id(line)
        path = out / f"{vid_id}.json"

        if path.exists() and not force:
            log.info("Exists, skipping: %s", path.name)
            skipped += 1
            continue

        path.write_text(json.dumps(make_stub(vid_id), indent=2) + "\n")
        log.info("Wrote: %s", path.name)
        created += 1

    log.info("Ingest summary: created=%d skipped=%d invalid=%d", created, skipped, invalid)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Scaffold schema-compliant stubs from URL list.")
    ap.add_argument("--input", required=True, help="Path to urls.txt")
    ap.add_argument("--out", required=True, help="Output folder (e.g., data/raw)")
    ap.add_argument("--force", action="store_true", help="Overwrite existing JSON files")
    args = ap.parse_args()
    main(args.input, args.out, args.force)
