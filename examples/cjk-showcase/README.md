# CJK Showcase (Chinese Language Example)

This directory demonstrates how LLM Wiki Agent performs with Non-English (CJK) languages.

The agent naturally supports processing Chinese content. With the CJK query bug fixed, you can ingest, query, and linguistically search across Chinese entries without any language-specific configuration. 

## Files included in this showcase:

- `raw/2026-04-13-reflection.md`: A sample source document (a personal reflection on career transition).

Only the source document is included; the wiki pages derived from it are not.

Try running `python tools/query.py "关于AI转型的建议"` from the root directory after
ingesting this source into your main knowledge base to see how semantic extraction
and keyword matching behave in non-English contexts.
