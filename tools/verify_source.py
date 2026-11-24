#!/usr/bin/env python3
"""Document trust check for LLM Wiki sources — optional Stipple add-on.

Before a source document is ingested into the wiki, verify it: forensic
authenticity (tamper risk band + per-signal evidence) and AI-written-prose
probability via the Stipple API (https://www.stipple.sh, free anonymous tier,
no API key needed; STIPPLE_API_KEY for your own metering).

Why: the wiki treats ingested sources as ground truth. A tampered PDF or an
AI-generated fake paper gets summarized into entities, concepts, and the
overview exactly like a real one — poisoning every downstream synthesis.
Checking trust at ingest time flags those sources on their wiki page
(a banner + the warrant id) instead of silently trusting them.

Usage:
    python tools/verify_source.py raw/papers/paper.pdf
    python tools/verify_source.py raw/papers/*.pdf          # batch
    python tools/verify_source.py report.pdf --fail-on high  # exit 1 if band >= high

Output is also written to wiki/trust/<slug>.json so the ingest step (and the
agent) can attach it to the source's wiki page.

All checks are best-effort: API unreachable -> recorded as an error, never
raised. This tool is standalone; ingest works unchanged without it.
"""

import argparse
import json
import os
import sys
import urllib.request
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools._utils import REPO_ROOT, sha256  # noqa: E402

STIPPLE_BASE_URL = os.getenv("STIPPLE_BASE_URL", "https://www.stipple.sh")
TRUST_DIR = REPO_ROOT / "wiki" / "trust"
TIMEOUT = 300

BANDS = {"low": 0, "medium": 1, "high": 2}


def _headers() -> dict:
    headers = {"User-Agent": "llm-wiki-agent-verify/1.0", "Accept": "application/json"}
    key = os.getenv("STIPPLE_API_KEY", "").strip()
    if key:
        headers["Authorization"] = "Bearer " + key
    return headers


def _post_file(endpoint: str, path: Path):
    """POST a document as multipart. Returns parsed JSON or None (best-effort)."""
    try:
        path = Path(path)
        boundary = "----wikiverify" + uuid.uuid4().hex
        with open(path, "rb") as f:
            content = f.read()
        body = b"".join(
            [
                (
                    f"--{boundary}\r\n"
                    f'Content-Disposition: form-data; name="file"; '
                    f'filename="{path.name}"\r\n'
                    "Content-Type: application/octet-stream\r\n\r\n"
                ).encode(),
                content,
                b"\r\n",
                f"--{boundary}--\r\n".encode(),
            ]
        )
        req = urllib.request.Request(
            STIPPLE_BASE_URL + endpoint,
            data=body,
            method="POST",
            headers={
                **_headers(),
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            },
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:  # noqa: BLE001 - verification is best-effort
        print(f"  verification unavailable: {e}", file=sys.stderr)
        return None


def verify_source(path: Path) -> dict:
    """Verify one document. Returns the document_trust record."""
    import hashlib
    record = {
        "source": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "authenticity": None,
        "ai_text": None,
    }
    warrant = _post_file("/v1/warrants", path)
    if warrant:
        record["authenticity"] = {
            "warrant_id": warrant.get("warrant_id"),
            "risk_band": warrant.get("risk_band"),
            "risk_score": warrant.get("risk_score"),
            "inspection_quality": warrant.get("inspection_quality"),
            "recommended_action": warrant.get("recommended_action"),
            "summary": warrant.get("summary"),
        }
    else:
        record["authenticity"] = {"error": "verification unavailable"}
    ai = _post_file("/v1/detect-ai-text", path)
    if ai:
        record["ai_text"] = (
            {"applicable": False}
            if ai.get("applicable") is False
            else {
                "applicable": True,
                "probability": ai.get("probability"),
                "lean": ai.get("lean"),
                "tells": ai.get("tells"),
            }
        )
    return record


def save_record(record: dict) -> Path:
    TRUST_DIR.mkdir(parents=True, exist_ok=True)
    slug = Path(record["source"]).stem.lower().replace(" ", "-")[:60]
    out = TRUST_DIR / f"{slug}.json"
    out.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return out


def main():
    ap = argparse.ArgumentParser(description="Verify source-document trust (Stipple, free tier).")
    ap.add_argument("sources", nargs="+", help="source document paths")
    ap.add_argument("--fail-on", default=None, choices=["medium", "high"],
                    help="exit 1 if any source's risk band is at or above this")
    args = ap.parse_args()

    worst = None
    for src in args.sources:
        p = Path(src)
        if not p.is_file():
            print(f"[skip] {src}: not a file")
            continue
        print(f"Verifying {p.name} ...")
        record = verify_source(p)
        out = save_record(record)
        auth = record.get("authenticity") or {}
        band = auth.get("risk_band")
        warrant = auth.get("warrant_id", "?")
        if band:
            print(f"  risk_band: {band}  warrant: {warrant}")
            print(f"  saved: {out}")
            if worst is None or BANDS.get(band, 0) > BANDS.get(worst, 0):
                worst = band
        else:
            print(f"  error: {auth.get('error')}  (recorded in {out})")

    if args.fail_on and worst and BANDS.get(worst, 0) >= BANDS.get(args.fail_on, 99):
        print(f"\nPOLICY: worst risk band '{worst}' >= '{args.fail_on}' — review before ingesting.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
