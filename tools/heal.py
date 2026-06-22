#!/usr/bin/env python3
"""
Graph Self-Healing Tool

Automatically retrieves "Missing Entity Pages" from the wiki and generates
comprehensive definition pages for them using the LLM.
It resolves broken entity links by scanning existing contexts where the entity is referenced.

Usage:
    python tools/heal.py
"""

import re
import sys
from pathlib import Path

# Bootstrap shared utilities
sys.path.insert(0, str(Path(__file__).parent.parent))
from tools._utils import REPO_ROOT, WIKI_DIR, call_llm, all_wiki_pages
from tools.lint import find_missing_entities

ENTITIES_DIR = WIKI_DIR / "entities"



def sanitize_filename(name: str) -> str:
    """Strip characters that are unsafe in filenames.

    Removes path separators, null bytes, and leading dots to prevent
    directory traversal when using LLM-derived entity names as filenames.
    """
    original = name
    name = re.sub(r"[/\\:\0]", "", name)
    name = name.lstrip(".")
    name = "_".join(name.split())
    if not name:
        raise ValueError(f"Entity name became empty after sanitization: {original!r}")
    return name


def search_sources(entity: str, pages: list[Path]) -> list[Path]:
    """Find up to 15 pages where this entity is mentioned natively."""
    sources = []
    for p in pages:
        if "entities" not in str(p.parent) and "concepts" not in str(p.parent):
            content = p.read_text(encoding="utf-8")
            if entity.lower() in content.lower():
                sources.append(p)
    return sources[:15]

def heal_missing_entities():
    pages = all_wiki_pages()
    missing_entities = find_missing_entities(pages)
    
    if not missing_entities:
        print("Graph is fully connected. No missing entities found!")
        return

    ENTITIES_DIR.mkdir(exist_ok=True, parents=True)
    print(f"Found {len(missing_entities)} missing entity nodes. Commencing auto-heal...")
    
    for entity in missing_entities:
        print(f"Healing entity page for: {entity}")
        sources = search_sources(entity, pages)
        
        context = ""
        for s in sources:
            context += f"\n\n### {s.name}\n{s.read_text(encoding='utf-8')[:800]}"
        
        prompt = f"""You are filling a data gap in the Personal LLM Wiki. 
Create an Entity definition page for "{entity}".

Here is how the entity appears in the current sources:
{context}

Format:
---
title: "{entity}"
type: entity
tags: []
sources: {[s.name for s in sources]}
---

# {entity}

Write a comprehensive paragraph defining what `{entity}` means in the context of this wiki, its main significance, and any actions or associations related to it.
"""
        try:
            result = call_llm(prompt, default_model="claude-3-5-haiku-latest", max_tokens=1500)
            safe_name = sanitize_filename(entity)
            out_path = ENTITIES_DIR / f"{safe_name}.md"
            # Safety: ensure resolved path stays within entities directory
            if not str(out_path.resolve()).startswith(str(ENTITIES_DIR.resolve())):
                print(f" [!] Skipping unsafe path for entity: {entity}")
                continue
            out_path.write_text(result, encoding="utf-8")
            print(f" -> Saved to {out_path.relative_to(REPO_ROOT)}")
        except Exception as e:
            print(f" [!] Failed to generate {entity}: {e}")

if __name__ == "__main__":
    heal_missing_entities()
