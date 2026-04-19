Check the wiki for structural problems and report findings. Do not auto-fix.

1. **Empty/stub files**: Find any files under 10 lines in wiki/sources/, wiki/entities/, wiki/concepts/. List them with line counts.

2. **Broken wikilinks**: Scan all wiki pages for [[wikilinks]] that point to non-existent files. List each broken link and the page it appears in.

3. **Orphaned pages**: Find wiki pages with zero incoming links from other pages. List them.

4. **Index sync**: Check wiki/index.md against actual files. Report pages missing from index and index entries pointing to non-existent files.

5. **Log sync**: Check wiki/log.md against wiki/sources/. Report any source pages with no corresponding log entry. Tag findings as [missing-log-entry].

6. **Report**: Print a structured summary of all findings, grouped by category, with file paths. Do not create, modify, or delete any files.
