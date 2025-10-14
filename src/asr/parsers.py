# src/asr/parsers.py
from __future__ import annotations

import logging
import re
from typing import List, Optional, TypedDict

log = logging.getLogger(__name__)  # inherit project logging config

# ---------- Types -----------------------------------------------------------
class Segment(TypedDict):
    start: float                 # seconds from media start
    end: Optional[float]         # None if unknown (e.g., plain .txt)
    text: str                    # normalized caption text

# ---------- Precompiled regexes --------------------------------------------
# Split caption blocks by blank lines (SRT & VTT both do this)
BLOCK_SPLIT_RE = re.compile(r"\n\s*\n", flags=re.M)

# Time fragments: SRT (comma) vs VTT (dot)
HMS_SRT = r"(?P<{h}h>\d{{2}}):(?P<{m}m>\d{{2}}):(?P<{s}s>\d{{2}}),(?P<{ms}ms>\d{{3}})"
HMS_VTT = r"(?P<{h}h>\d{{2}}):(?P<{m}m>\d{{2}}):(?P<{s}s>\d{{2}})\.(?P<{ms}ms>\d{{3}})"
MS_VTT  = r"(?P<{m}m>\d{{2}}):(?P<{s}s>\d{{2}})\.(?P<{ms}ms>\d{{3}})"

SRT_TIME_RE = re.compile(
    rf"{HMS_SRT.format(h='sh', m='sm', s='ss', ms='sms')}\s*-->\s*"
    rf"{HMS_SRT.format(h='eh', m='em', s='es', ms='ems')}"
)

VTT_TIME_HH_RE = re.compile(  # hh:mm:ss.mmm --> hh:mm:ss.mmm
    rf"{HMS_VTT.format(h='sh', m='sm', s='ss', ms='sms')}\s*-->\s*"
    rf"{HMS_VTT.format(h='eh', m='em', s='es', ms='ems')}"
)

VTT_TIME_MM_RE = re.compile(  # mm:ss.mmm --> mm:ss.mmm
    rf"{MS_VTT.format(m='sm', s='ss', ms='sms')}\s*-->\s*"
    rf"{MS_VTT.format(m='em', s='es', ms='ems')}"
)

# ---------- Helpers ---------------------------------------------------------
def _to_seconds(h: int, m: int, s: int, ms: int) -> float:
    return h * 3600 + m * 60 + s + ms / 1000.0

def _strip_bom(s: str) -> str:
    return s.replace("\ufeff", "").strip()

# ---------- Public parsers --------------------------------------------------
def parse_txt(text: str) -> List[Segment]:
    """Plain text with no timestamps -> single segment at t=0."""
    clean = " ".join(ln.strip() for ln in text.splitlines() if ln.strip())
    return [{"start": 0.0, "end": None, "text": clean}] if clean else []

def parse_srt(text: str) -> List[Segment]:
    """Minimal SRT parser; skips malformed blocks rather than failing."""
    segments: List[Segment] = []
    for block in BLOCK_SPLIT_RE.split(text.strip()):
        lines = [_strip_bom(ln) for ln in block.splitlines() if ln.strip()]
        if len(lines) < 2:
            continue
        # time is usually in one of the first two lines
        m = None
        for cand in lines[:2]:
            m = SRT_TIME_RE.match(cand)
            if m:
                break
        if not m:
            log.debug("SRT block lacks valid timecode; skipped: %r", lines[:3])
            continue

        sh, sm, ss, sms = int(m["sh"]), int(m["sm"]), int(m["ss"]), int(m["sms"])
        eh, em, es, ems = int(m["eh"]), int(m["em"]), int(m["es"]), int(m["ems"])
        start = _to_seconds(sh, sm, ss, sms)
        end = _to_seconds(eh, em, es, ems)

        # drop index & time lines; keep caption text
        text_lines = [ln for ln in lines if "-->" not in ln and not ln.isdigit()]
        if text_lines:
            segments.append({"start": float(start), "end": float(end), "text": " ".join(text_lines)})
    return segments

def parse_vtt(text: str) -> List[Segment]:
    """Minimal VTT parser; supports WEBVTT header, HH and MM formats."""
    segments: List[Segment] = []
    norm = re.sub(r"^WEBVTT.*\n", "", text, flags=re.IGNORECASE).strip()

    def _match_times(line: str) -> Optional[tuple[float, float]]:
        """Return (start_sec, end_sec) if the line has a valid VTT time range."""
        m = VTT_TIME_HH_RE.match(line)
        if m:
            sh, sm, ss, sms = int(m["sh"]), int(m["sm"]), int(m["ss"]), int(m["sms"])
            eh, em, es, ems = int(m["eh"]), int(m["em"]), int(m["es"]), int(m["ems"])
            return _to_seconds(sh, sm, ss, sms), _to_seconds(eh, em, es, ems)
        m = VTT_TIME_MM_RE.match(line)
        if m:
            sm, ss, sms = int(m["sm"]), int(m["ss"]), int(m["sms"])
            em, es, ems = int(m["em"]), int(m["es"]), int(m["ems"])
            return _to_seconds(0, sm, ss, sms), _to_seconds(0, em, es, ems)
        return None

    def _body(lines: list[str]) -> str:
        """Join caption lines after the timing line."""
        return " ".join(lines[1:]) if len(lines) > 1 else ""

    for block in BLOCK_SPLIT_RE.split(norm):
        lines = [_strip_bom(ln) for ln in block.splitlines() if ln.strip()]
        if not lines:
            continue

        times = _match_times(lines[0])
        if not times:
            log.debug("VTT block lacks valid timecode; skipped: %r", lines[:2])
            continue

        start, end = times
        body = _body(lines)
        if body:
            segments.append({"start": float(start), "end": float(end), "text": body})

    return segments