# LLM Wiki Agent — Schema & Workflow Instructions

This wiki is maintained entirely by Claude Code. No API key or Python scripts needed — just open this repo in Claude Code and talk to it.

## Slash Commands (Claude Code)

| Command | What to say |
|---|---|
| `/wiki-ingest` | `ingest raw/my-article.md` |
| `/wiki-query` | `query: what are the main themes?` |
| `/wiki-lint` | `lint the wiki` |
| `/wiki-graph` | `build the knowledge graph` |

Or just describe what you want in plain English:
- *"Ingest this file: raw/papers/attention-is-all-you-need.md"*
- *"What does the wiki say about transformer models?"*
- *"Check the wiki for orphan pages and contradictions"*
- *"Build the graph and show me what's connected to RAG"*

Claude Code reads this file automatically and follows the workflows below.

---

## Directory Layout

```
raw/          # Immutable source documents — never modify these
wiki/         # Claude owns this layer entirely
  index.md    # Catalog of all pages — update on every ingest
  log.md      # Append-only chronological record
  overview.md # Living synthesis across all sources
  sources/    # One summary page per source document
  entities/   # People, companies, projects, products
  concepts/   # Ideas, frameworks, methods, theories
  syntheses/  # Saved query answers
graph/        # Auto-generated graph data
tools/        # Optional standalone Python scripts (require ANTHROPIC_API_KEY)
```

---

## Ingestion Queue — Raw Files To Process

> **Rule: ingest ONE file per session. Check it off when done (`- [x]`). Never skip the Ingest Workflow steps.**
> Source: all files were copied from `netzkontrast/dual-kernel/Markdown-docs` on 2026-04-10.
> Progress: **0 / 94 ingested**

- [ ] `raw/40ChapterPlotModule.md`
- [ ] `raw/AegisAnalyseUndPromptOptimierung.md`
- [ ] `raw/AegisEmergenzAusDerLeere.md`
- [ ] `raw/AegisGenesisKrise20prosaAuftrag20formulieren.md`
- [ ] `raw/AegisPhilosophieUndManifestEntwicklung.md`
- [ ] `raw/AegisPhilosophieUndSystemtheorie.md`
- [ ] `raw/AegisPhilosophischeUndSystemtheoretischeAnalyse.md`
- [ ] `raw/AegisProtokolleKritischeEvaluationNeukonzeption.md`
- [ ] `raw/AnIntroductionToTheConceptsOfCoherenceProtocol.md`
- [ ] `raw/AngereichertesPlotkonzeptKapitelthemenKoharenzProtokoll.md`
- [ ] `raw/Blueprint.md`
- [ ] `raw/BridgingNarrativeTheoryAndAiAuthorship.md`
- [ ] `raw/CharakterarchitekturFurNarrativesRomanprojekt.md`
- [ ] `raw/DialetheismusImKoharenzProtokoll.md`
- [ ] `raw/DramaticaTheoryOverviewAndResources.md`
- [ ] `raw/DramaturgicalPrecisionDeconstructingTheIrreversibleConflictInKoharenzProtokoll.md`
- [ ] `raw/DualKernelAiAndNarrativeCollapse.md`
- [ ] `raw/EinleitungGenesisDerExistenz.md`
- [ ] `raw/EmergenzAutonomerSystemeAegisForschung.md`
- [ ] `raw/ErkenntnistheorieFurNarrativeProjektgestaltung.md`
- [ ] `raw/ExistenzKosmosSeinUndBewusstsein.md`
- [ ] `raw/ForschungsprojektKoharenzProtokollAnalyse.md`
- [ ] `raw/GrenzenDerExistenzEineUmfassendeAnalyse.md`
- [ ] `raw/GuardiansUndKernWeltenKonzept.md`
- [ ] `raw/HolographischesPrinzipFurKoharenzProtokoll.md`
- [ ] `raw/IdentitatGrenzenUndWandel.md`
- [ ] `raw/InterdisziplinareRechercheFurKoharenzProtokoll.md`
- [ ] `raw/KaelsDissociativeArchitectureAnalysis.md`
- [ ] `raw/KernweltenFurKoharenzProtokoll.md`
- [ ] `raw/KoharenzProtokoll39KapitelMatrix.md`
- [ ] `raw/KoharenzProtokollKapitelstrukturMitKonzepten39Kapitel.md`
- [ ] `raw/KoharenzProtokollKonzept.md`
- [ ] `raw/KoharenzProtokollKonzeptionelleAusarbeitung.md`
- [ ] `raw/KoharenzProtokollKonzeptionelleThemenStruktur.md`
- [ ] `raw/KoharenzProtokollMetaForeshadowingBeobachterLogik.md`
- [ ] `raw/KoharenzProtokollPlotBlueprintErstellung.md`
- [ ] `raw/KoharenzProtokollPlotEntwicklungUndWahrheitsdualitat.md`
- [ ] `raw/KopieVonNarrativeLosungenFurRomanprojekt.md`
- [ ] `raw/LogiksystemAegisEntwicklungsszenarien.md`
- [ ] `raw/MonstergruppeAlsDenkmodellDerKomplexitat.md`
- [ ] `raw/MonstergruppeBabymonstergruppeFragmentierungErzahlung.md`
- [ ] `raw/MonstergruppeNarrativeClusterUndMetaphern.md`
- [ ] `raw/NarrativExistenziellerKoharenzNztProtokoll.md`
- [ ] `raw/NarrativePlotExplorationExistenzielleKoharenz.md`
- [ ] `raw/NarrativeRekombinationPotenzialExplorationPlotSynopsen.md`
- [ ] `raw/NarrativeVertiefungKoharenzProtokoll.md`
- [ ] `raw/OrteKonzeptFurKoharenzProtokoll.md`
- [ ] `raw/PVsNpUndKoharenz.md`
- [ ] `raw/ParadoxienDerKoharenzProtokollEntwicklung.md`
- [ ] `raw/ParakonsistenteLogikFurKoharenzProtokoll.md`
- [ ] `raw/ParakonsistenzAegisUndNichtExistenz.md`
- [ ] `raw/PhilosophieGrenzenUndZukunft.md`
- [ ] `raw/PhysikGrenzenUndRatselDesUniversums.md`
- [ ] `raw/PlotBlueprintMethodikKoharenzProtokoll.md`
- [ ] `raw/PlotExplorationKoharenzProtokollkonzepte.md`
- [ ] `raw/PlotKonzepteKoharenzProtokollGenerierung.md`
- [ ] `raw/PlotkonzeptKoharenzProtokollHeldinnenreiseStruktur.md`
- [ ] `raw/ProjektKoharenzProtokollTiefenanalyse.md`
- [ ] `raw/README.md`
- [ ] `raw/RomanBlueprintSeelenKoharenzProtokoll.md`
- [ ] `raw/RomanEntwicklungKoharenzUndLeitfragen.md`
- [ ] `raw/RomanFundamentTheoretischeRecherche.md`
- [ ] `raw/RomanKapitelAusformulierungKoharenzProtokoll.md`
- [ ] `raw/RomanKoharenzProtokoll.md`
- [ ] `raw/RomanKoharenzProtokoll2.md`
- [ ] `raw/RomanKonzeptDualitatKoharenzSpannung.md`
- [ ] `raw/RomanKonzeptentwicklungKoharenzProtokoll.md`
- [ ] `raw/RomanLokalitatenKonzeptUndAusarbeitung.md`
- [ ] `raw/RomanRefactoringKoharenzUndCharakterentwicklung.md`
- [ ] `raw/RomanSyntheseMitDualKernelTheorie.md`
- [ ] `raw/RomanUrvertrauenLiebeTranszendenz.md`
- [ ] `raw/RomanWorldbuildingFragmentierteIdentitatMetaRealitat.md`
- [ ] `raw/RomanentwurfKoharenzProtokollTeil1.md`
- [ ] `raw/Romanstruktur3Teile39Kapitel1Anfang.md`
- [ ] `raw/RomanstrukturUndPhilosophischeEinleitung.md`
- [ ] `raw/SpannungsfelderUndAegisMetaFrameworkAnalyse.md`
- [ ] `raw/StorytellingCommandmentsExplained.md`
- [ ] `raw/SymmetrieParadoxieExistenzJenseitsSimulation.md`
- [ ] `raw/SymmetrienClusterungUberWissensgebieteHinweg.md`
- [ ] `raw/TheCoherenceProtocolADefinitiveGuideToTheNarrativeArchitecture.md`
- [ ] `raw/TheCoherenceProtocolANarrativeDesignWorldArchitectureDocument.md`
- [ ] `raw/TheFoundationProtocolAMetaphysicalThesisOnTheReAnchoringOfReality.md`
- [ ] `raw/TheKoharenzProtokollADefinitiveGuideToNarrativeArchitecture.md`
- [ ] `raw/TheThematicArchitectureOfKoharenzProtokollAConceptualLexiconOfCoreDualities.md`
- [ ] `raw/TheTrueCoherenceProtocolArchitectingKaelsJourneyFromTsdpFragmentationToFunctionalMultiplicity.md`
- [ ] `raw/Top13ForschungsfragenZurRealitat.md`
- [ ] `raw/TranszendenzLogischerSystemeEntropie.md`
- [ ] `raw/TranszendenzUndParadoxienVerbindungslinien.md`
- [ ] `raw/TsdpAnalyseKaelsInnereWelt.md`
- [ ] `raw/UmfassendesLokalitatenKonzeptFurRoman.md`
- [ ] `raw/VTheFoundationAndKaelsIntegrationArc.md`
- [ ] `raw/WahrheitstheorienKoharenzVsKorrespondenz.md`
- [ ] `raw/ZeitGrenzenWahrnehmungUndTheorien.md`
- [ ] `raw/test-kael-konflikt.md`

---

## Page Format

Every wiki page uses this frontmatter:

```yaml
---
title: "Page Title"
type: source | entity | concept | synthesis
tags: []
sources: []       # list of source slugs that inform this page
last_updated: YYYY-MM-DD
---
```

Use `[[PageName]]` wikilinks to link to other wiki pages.

---

## Ingest Workflow

Triggered by: *"ingest <file>"* or `/wiki-ingest`

Steps (in order):
1. Read the source document fully using the Read tool
2. Read `wiki/index.md` and `wiki/overview.md` for current wiki context
3. Write `wiki/sources/<slug>.md` — use the source page format below
4. Update `wiki/index.md` — add entry under Sources section
5. Update `wiki/overview.md` — revise synthesis if warranted
6. Update/create entity pages for key people, companies, projects mentioned
7. Update/create concept pages for key ideas and frameworks discussed
8. Flag any contradictions with existing wiki content
9. Append to `wiki/log.md`: `## [YYYY-MM-DD] ingest | <Title>`

### Source Page Format

```markdown
---
title: "Source Title"
type: source
tags: []
date: YYYY-MM-DD
source_file: raw/...
---

## Summary
2–4 sentence summary.

## Key Claims
- Claim 1
- Claim 2

## Key Quotes
> "Quote here" — context

## Connections
- [[EntityName]] — how they relate
- [[ConceptName]] — how it connects

## Contradictions
- Contradicts [[OtherPage]] on: ...
```

---

## Query Workflow

Triggered by: *"query: <question>"* or `/wiki-query`

Steps:
1. Read `wiki/index.md` to identify relevant pages
2. Read those pages with the Read tool
3. Synthesize an answer with inline citations as `[[PageName]]` wikilinks
4. Ask the user if they want the answer filed as `wiki/syntheses/<slug>.md`

---

## Lint Workflow

Triggered by: *"lint the wiki"* or `/wiki-lint`

Use Grep and Read tools to check for:
- **Orphan pages** — wiki pages with no inbound `[[links]]` from other pages
- **Broken links** — `[[WikiLinks]]` pointing to pages that don't exist
- **Contradictions** — claims that conflict across pages
- **Stale summaries** — pages not updated after newer sources
- **Missing entity pages** — entities mentioned in 3+ pages but lacking their own page
- **Data gaps** — questions the wiki can't answer; suggest new sources

Output a lint report and ask if the user wants it saved to `wiki/lint-report.md`.

---

## Graph Workflow

Triggered by: *"build the knowledge graph"* or `/wiki-graph`

When the user asks to build the graph, run `tools/build_graph.py` which:
- Pass 1: Parses all `[[wikilinks]]` → deterministic `EXTRACTED` edges
- Pass 2: Infers implicit relationships → `INFERRED` edges with confidence scores
- Runs Louvain community detection
- Outputs `graph/graph.json` + `graph/graph.html`

If the user doesn't have Python/dependencies set up, instead generate the graph data manually:
1. Use Grep to find all `[[wikilinks]]` across wiki pages
2. Build a node/edge list
3. Write `graph/graph.json` directly
4. Write `graph/graph.html` using the vis.js template

---

## Naming Conventions

- Source slugs: `kebab-case` matching source filename
- Entity pages: `TitleCase.md` (e.g. `OpenAI.md`, `SamAltman.md`)
- Concept pages: `TitleCase.md` (e.g. `ReinforcementLearning.md`, `RAG.md`)
- Source pages: `kebab-case.md`

## Index Format

```markdown
# Wiki Index

## Overview
- [Overview](overview.md) — living synthesis

## Sources
- [Source Title](sources/slug.md) — one-line summary

## Entities
- [Entity Name](entities/EntityName.md) — one-line description

## Concepts
- [Concept Name](concepts/ConceptName.md) — one-line description

## Syntheses
- [Analysis Title](syntheses/slug.md) — what question it answers
```

## Log Format

Each entry starts with `## [YYYY-MM-DD] <operation> | <title>` so it's grep-parseable:

```
grep "^## \[" wiki/log.md | tail -10
```

Operations: `ingest`, `query`, `lint`, `graph`
