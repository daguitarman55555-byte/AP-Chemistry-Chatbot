# Development handoff

## User requirements

Build an AP Chemistry tutor that guides students toward answers without revealing them, generates scientifically valid questions, and creates useful interactive graphs and visuals. Include PhET references where relevant. Track a goal of 200 genuinely distinct question types for each of the 91 numbered topics; do not count numerical variants as new types. Research past exams while respecting copyright and secure exam access boundaries.

## What exists

The reproducible corpus builds 4,567 question records, 221 authored families, 9,159 hints, 960 graph datasets, and an offline graph explorer. The original numerical subset has 628 items; 3,840 additional items are graph-reading drills, so the counts overstate conceptual breadth if interpreted as distinct skills. The remaining 99 items are conceptual or experimental-reasoning seeds.

The terminal tutor can expose a prompt, reveal one authored hint at a time between attempts, and check a numeric answer with its stated unit. It cannot evaluate arbitrary intermediate algebra, chemical explanations, alternative units, or general conversation. It is a deterministic backend seed, not an AI chatbot.

## Outstanding requirements

1. Full objective/essential-knowledge audit and substantial independent question authorship. No topic meets the 200 validated-type target.
2. Expert chemistry review, semantic-deduplication review, calibrated difficulty, and better precision policies.
3. Structured step validators for charge/atom balance, equation setup, reasoning, and equivalent units.
4. A server and user interface that never ship the answer store or hidden solution graphs to students.
5. A language-model integration with strict tool boundaries and no-answer conversation tests.
6. Browser testing of the graph explorer and new renderers for molecules, particle pictures, and energy/cell diagrams.
7. PhET integration appropriate to the actual product's license; ordinary embeddings do not automatically expose simulation state.
8. A verified exam/form catalog beyond the limited public references. Do not present copied exams as original work or assume every past exam is public.

## Validation and constraints

Run `python corpus/rebuild_all.py` and `python -m unittest discover -s tests -v`. Use the coverage data to report real progress. Keep generated outputs out of source control; edit generators and rebuild. The corpus is intentionally hypothetical where constants are not tied to measured substances. Educational calculation models are not instructions for home chemistry experiments.

The current hint counter only prevents consecutive hint calls without a valid numeric attempt; it is not a robust pedagogy or anti-abuse system. Existing hint text has not undergone an independent leakage audit. The public source repository contains answer-generating code, so it cannot enforce secrecy against someone inspecting the source. The future hosted student interface must enforce separation server-side.

Use isolated branches for later changes and avoid force-pushing over concurrent work. Never commit API credentials, student records, or restricted exam content.
