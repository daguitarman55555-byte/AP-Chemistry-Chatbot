# AP Chemistry Chatbot

An original AP Chemistry teaching-data foundation with a deterministic tutoring prototype. The full conversational chatbot is not implemented yet.

## Current contents

- 91 numbered curriculum topics.
- 4,567 original question records, including numerical and graph variants.
- 221 authored families across the entire course; these are not 200 types per topic.
- 9,159 staged hints and separate answer records.
- 960 synthetic graph datasets across 24 models, totaling 192,960 points.
- An offline interactive graph explorer.
- 17 PhET references and four official public FRQ set references (2023–2026).
- An offline tutoring engine with bounded hint progression and numeric checks.

## Run locally

Python 3.10+ is sufficient. No package installation, account, or API key is needed for the current prototype.

```sh
python corpus/rebuild_all.py
python -m unittest discover -s tests -v
python tutor.py --topic 8.3
```

After rebuilding, open `corpus/graph_explorer.html` in a browser. For a particular non-graph practice item, use `python tutor.py --question weak_acid-01`. The terminal runner deliberately excludes graph tasks because it cannot display their required stimulus and data table.

The repository tracks the source generators rather than committing repeated megabytes of generated data. Rebuilding creates SQLite, JSON, JSONL, readable worked examples, and the self-contained graph explorer in `corpus/`. The generated answer files are for teacher/backend use. Do not serve the whole corpus as a student-facing static directory.

## Validation and limits

The build checks 628 original numerical model calculations, 3,840 graph-answer calculations, physical bounds, weak-acid roots, dataset invariants, and database integrity. Tutoring tests cover non-finite input, hint gating, unit mismatches, and answer-field separation. These are automated checks, not expert chemistry review.

No topic yet meets the requested 200 distinct validated question types. The target is recorded in the generated `coverage_200_types_per_topic.json`; number changes and cosmetic rewording do not count as new types. Complete learning-objective coverage, question calibration, independent expert review, semantic duplicate review, and full multi-turn chemistry reasoning remain unfinished.

Official exams and PhET simulations are linked, not copied or bundled. This is not a complete archive of past exams or their worked solutions. Graphs are model-generated, not measured data. Browser rendering verification for the graph explorer remains outstanding after the remote preview environment blocked the local address.

## Project guide

- [Research and tutor design](corpus/RESEARCH_AND_TUTOR_DESIGN.md)
- [Visuals, PhET, and coverage gaps](corpus/VISUALS_AND_COVERAGE.md)
- [Development handoff](HANDOFF.md)
- [Corpus documentation](corpus/README.md)

This project is not affiliated with or endorsed by College Board or PhET.
