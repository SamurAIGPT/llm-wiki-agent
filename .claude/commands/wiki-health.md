Check the wiki for structural problems and fix them:

1. **Empty/stub files**: Find any files under 10 lines in wiki/sources/, wiki/entities/, wiki/concepts/. List them. If the source material exists elsewhere in the wiki (referenced by other pages), reconstruct the page from those references. If not reconstructable, flag for manual re-ingest.

2. **Missing entity pages**: Scan all wiki pages for [[wikilinks]] that point to non-existent files. For each broken link, create the missing entity or concept page using context from the pages that reference it.

3. **Orphaned pages**: Find any wiki pages with zero incoming links from other pages. Flag them — they may need cross-references added.

4. **Index sync**: Verify wiki/index.md lists every page in wiki/sources/, wiki/entities/, wiki/concepts/. Add any missing entries. Remove any entries pointing to non-existent files.

5. **Log sync**: Verify wiki/log.md has entries for all ingested sources. Add missing entries with [auto-recovered] tag.

6. **Report**: Summarize what was broken and what was fixed. Do not ask for permission — fix everything automatically and report after.
