> Historical research snapshot from the initial corpus release. Counts and software-status statements below describe that snapshot. See the repository root README and evidence/coverage.json for the current application, expanded corpus, and remaining gaps.

# AP Chemistry teaching database — research prototype

Prepared September 10, 2026. This package is a reusable foundation for a later chemistry tutor. It is **not a complete collection of past AP Chemistry exams** and is **not a fully validated teaching system**.

It contains 91 topic records, 4,567 original practice items with answers or explanations, 9,159 staged hints, and 28 official question references across the four public FRQ sets verified for 2023–2026. The bank includes 3,840 graph-reading drills. Of the remaining original items, 628 are numerical variants across 26 families, 91 are conceptual seeds, and eight address laboratory/data/representation reasoning. Numerical diversity is much smaller than the item count: most families have 25 parameter variants, and formal-charge bookkeeping has three distinct cases.

Official exam questions and scoring documents remain on College Board's website. This package stores links and metadata, not copies of their text, figures, or worked solutions. The 2023–2025 scoring PDFs were opened; the inspected archive did not link a 2026 scoring guide. Older resource access is logged as unresolved, failed, redirected, or unexamined; it is never silently counted as acquired.

The visual extension adds 960 model datasets (192,960 points), an offline graph explorer, and 17 PhET references. See `VISUALS_AND_COVERAGE.md`. The required 200 distinct types per topic is **not yet achieved**.

## Files

| File | Purpose |
|---|---|
| `chemistry.sqlite` | Queryable database with related tables and a student question view |
| `chemistry_database.json` | Core question-data export, including backend answers; graph/PhET exports are separate |
| `questions.jsonl`, `solutions.jsonl`, `hints.jsonl` | Separate streams for retrieval and controlled solution access |
| `topics.jsonl` | All 91 numbered topic mappings with original short labels |
| `exam_sets.jsonl`, `exam_items.jsonl` | Official source references, not copied exams |
| `archive_audit.jsonl` | Explicit archive gaps and failed older URL checks |
| `sources.jsonl` | Research provenance and check dates |
| `RESEARCH_AND_TUTOR_DESIGN.md` | Findings, content gaps, and future tutor architecture |
| `CURRICULUM_MAP.md` | Human-readable topic map with concept explanations |
| `WORKED_EXAMPLES.md` | One worked numerical example from each family |
| `build_database.py`, `concepts.txt` | Reproducible generator and original conceptual source data |
| `validate_database.py`, `validation_report.json` | Validation logic and numerical/structural results |

## Rebuild and inspect

Requires Python 3, with no additional packages or network access:

```sh
python rebuild_all.py
```

Example SQLite queries:

```sql
SELECT id, topic_id, prompt FROM student_questions WHERE topic_id='8.3';
SELECT level, text FROM hints WHERE question_id='weak_acid-01' ORDER BY level;
SELECT year, questions_url, scoring_url FROM exam_sets ORDER BY year DESC;
```

The student view helps select safe fields but is **not an access-control mechanism**. Never ship the full SQLite file, JSON master, solutions, or conceptual source file to an untrusted student frontend. The server should expose only the current prompt and one allowed hint. The future tutor must enforce the chosen no-answer policy server-side.

## What validation means here

All 628 numerical records pass a governing-relation or inverse-substitution check. The database also passes relational integrity and topic-coverage checks. These checks do not establish expert-reviewed explanations, complete essential-knowledge coverage, AP-calibrated difficulty, realistic experimental datasets, robust grading, or reliable multi-turn tutoring. Numerical values are teaching models with stated assumptions; hypothetical constants are not represented as measured constants for real substances.

Full precision is stored for calculation. Students should receive suitable rounding. Numeric tolerances are provisional and are not a complete significant-figure grading policy. The explanatory items and eight data/representation items have not received independent subject-expert review.

## Reuse boundary

All practice prompts and explanations here were newly authored; they are not College Board items and are not endorsed by College Board. Links do not confer permission to redistribute, scrape secure exams, or train on third-party text. Do not ingest AP Classroom or unreleased forms. Recheck third-party permissions before adding any licensed material. This package contains no student personal data and no hazardous experiment instructions.
