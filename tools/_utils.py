"""
Shared utilities for LLM Wiki tools.

Centralizes functions that were previously copy-pasted across tool files:
read_file, write_file, call_llm, sha256, extract_wikilinks, all_wiki_pages, append_log.
"""

from __future__ import annotations

import hashlib
import os
import re
import sys
from pathlib import Path

ATLAS_CLOUD_BASE_URL = "https://api.atlascloud.ai/v1"
ATLAS_CLOUD_DEFAULT_MODEL = "qwen/qwen3.5-flash"
_ATLAS_CLOUD_MODEL_PREFIXES = ("atlascloud", "atlas-cloud", "atlas")
_ATLAS_CLOUD_KEY_ENVS = ("ATLASCLOUD_API_KEY", "ATLAS_CLOUD_API_KEY")
_ATLAS_CLOUD_BASE_URL_ENVS = (
    "ATLASCLOUD_BASE_URL",
    "ATLAS_CLOUD_BASE_URL",
    "ATLAS_BASE_URL",
)

# ── Paths ──────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent.parent
WIKI_DIR = REPO_ROOT / "wiki"
RAW_DIR = REPO_ROOT / "raw"
INDEX_FILE = WIKI_DIR / "index.md"
LOG_FILE = WIKI_DIR / "log.md"
OVERVIEW_FILE = WIKI_DIR / "overview.md"
GRAPH_DIR = REPO_ROOT / "graph"
SCHEMA_FILE = REPO_ROOT / "CLAUDE.md"

# Default metadata files to exclude from wiki page listings.
_META_EXCLUDE = {"index.md", "log.md", "lint-report.md"}


def _first_env(names: tuple[str, ...]) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return None


def _split_atlas_cloud_model(model: str) -> str | None:
    normalized = model.strip()
    lower = normalized.lower()
    for prefix in _ATLAS_CLOUD_MODEL_PREFIXES:
        if lower == prefix:
            return ATLAS_CLOUD_DEFAULT_MODEL
        for separator in (":", "/"):
            marker = prefix + separator
            if lower.startswith(marker):
                atlas_model = normalized[len(marker):].strip()
                return atlas_model or ATLAS_CLOUD_DEFAULT_MODEL
    return None


def _llm_completion_kwargs(model: str) -> dict:
    atlas_model = _split_atlas_cloud_model(model)
    if not atlas_model:
        return {"model": model}

    kwargs = {
        "model": f"openai/{atlas_model}",
        "api_base": (
            _first_env(_ATLAS_CLOUD_BASE_URL_ENVS) or ATLAS_CLOUD_BASE_URL
        ).rstrip("/"),
    }
    api_key = _first_env(_ATLAS_CLOUD_KEY_ENVS)
    if api_key:
        kwargs["api_key"] = api_key
    return kwargs


# ── File I/O ───────────────────────────────────────────────────────────

def read_file(path: Path) -> str:
    """Read file contents as UTF-8. Returns empty string if file doesn't exist."""
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_file(path: Path, content: str):
    """Write UTF-8 content to file, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  wrote: {path.relative_to(REPO_ROOT)}")


# ── LLM ────────────────────────────────────────────────────────────────

def call_llm(
    prompt: str,
    model_env: str = "LLM_MODEL",
    default_model: str = "claude-3-5-sonnet-latest",
    max_tokens: int = 4096,
) -> str:
    """Call an LLM via litellm.

    Args:
        prompt: The user prompt.
        model_env: Environment variable name for model selection.
        default_model: Fallback model if env var is unset.
        max_tokens: Maximum response tokens.  0 or None to omit the limit.
    """
    try:
        from litellm import completion
    except ImportError:
        print("Error: litellm not installed. Run: pip install litellm")
        sys.exit(1)

    model = os.getenv(model_env, default_model)

    kwargs: dict = {
        "messages": [{"role": "user", "content": prompt}],
    }
    kwargs.update(_llm_completion_kwargs(model))
    if max_tokens:
        kwargs["max_tokens"] = max_tokens

    response = completion(**kwargs)
    return response.choices[0].message.content


# ── Hashing ────────────────────────────────────────────────────────────

def sha256(text: str, truncate: int = 0) -> str:
    """SHA-256 hex digest of *text*, optionally truncated to *truncate* chars.

    Default is the full 64-char hash.  Pass truncate=16 for the short form
    used by ingest.py and refresh.py.
    """
    h = hashlib.sha256(text.encode()).hexdigest()
    return h[:truncate] if truncate else h


# ── Wiki helpers ───────────────────────────────────────────────────────

def extract_wikilinks(content: str, unique: bool = False) -> list[str]:
    """Extract all [[WikiLink]] targets from page content.

    Args:
        unique: Deduplicate results (used by build_graph.py).
    """
    links = re.findall(r"\[\[([^\]]+)\]\]", content)
    return list(set(links)) if unique else links


def all_wiki_pages(extra_exclude: set[str] | None = None) -> list[Path]:
    """Return all .md files in wiki/, excluding metadata files.

    Args:
        extra_exclude: Additional filenames to skip (e.g. {"health-report.md"}).
    """
    exclude = _META_EXCLUDE | (extra_exclude or set())
    return [p for p in WIKI_DIR.rglob("*.md") if p.name not in exclude]


def append_log(entry: str):
    """Prepend a log entry to wiki/log.md (newest-first).

    Creates the file with a standard header if it doesn't exist.
    Preserves the prepend semantics used by ingest.py, query.py, and lint.py.
    """
    entry_text = entry.strip()

    if not LOG_FILE.exists():
        LOG_FILE.write_text(
            "# Wiki Log\n\n"
            "> Records important additions, revisions, and clarifications in the "
            "project knowledge layer. Maintained in append-only mode for agent and "
            "human traceability.\n\n"
            f"{entry_text}\n",
            encoding="utf-8",
        )
        return

    existing = read_file(LOG_FILE).rstrip()
    if not existing:
        existing = (
            "# Wiki Log\n\n"
            "> Records important additions, revisions, and clarifications in the "
            "project knowledge layer. Maintained in append-only mode for agent and "
            "human traceability."
        )
    LOG_FILE.write_text(existing + "\n\n" + entry_text + "\n", encoding="utf-8")
