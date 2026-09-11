> Historical research snapshot from the initial corpus release. Counts and software-status statements below describe that snapshot. See the repository root README and evidence/coverage.json for the current application, expanded corpus, and remaining gaps.

# AP Chemistry: research findings and tutor design

Research date: September 10, 2026.

The practical foundation is a versioned curriculum map, original solver-backed practice, and a separately maintained official-exam reference catalog. A pile of past exams alone would leave gaps in explanations, prerequisites, misconception diagnosis, and safe hint delivery. This release implements the data foundation; it does not implement a chatbot or claim exhaustive exam access.

## Verified course and examination facts

The current framework is organized into nine units. Multiple-choice weight ranges are 7–9% for units 1, 2, 4, 5, 6, 7, and 9; 18–22% for unit 3; and 11–15% for unit 8. Its six practice areas cover interpreting representations, choosing investigative methods, creating representations, analyzing models, calculating, and explaining claims. These are separate axes of coverage, not interchangeable skills. [College Board course page](https://apcentral.collegeboard.org/courses/ap-chemistry).

The linked CED is effective Fall 2024. The course requires at least 25% hands-on laboratory time and at least 16 investigations, including six inquiry-based investigations. A chatbot can support conceptual and data reasoning but cannot replace that hands-on requirement. [Course and Exam Description](https://apcentral.collegeboard.org/media/pdf/ap-chemistry-course-and-exam-description.pdf).

The current exam has 60 multiple-choice questions in 90 minutes and seven free-response questions in 105 minutes, each section contributing half the score. Three FRQs carry 10 points each and four carry 4 points each. It uses Bluebook for MCQs and viewing FRQs, with handwritten FRQ responses. [Official exam description](https://apcentral.collegeboard.org/courses/ap-chemistry/exam).

The numbered topic map contains 91 entries across units 1–9. The accompanying curriculum map uses original labels and seed explanations; it is not a reproduction of all official learning objectives or essential-knowledge statements. [Course topic overview](https://apcentral.collegeboard.org/media/pdf/ap-chemistry-course-at-a-glance.pdf).

June 2026 corrections explain that many older resource links moved into AP Classroom or the teacher community, with some nonaligned materials removed. Therefore, an old PDF URL redirecting to a landing page must not count as successful retrieval. [Clarifications](https://apcentral.collegeboard.org/media/pdf/ap-chemistry-course-and-exam-description-clarifications.pdf).

## Official exam inventory and actual limits

The inspected public Chemistry page lists the 2023–2026 FRQs. Scoring PDFs are linked and verified for 2023–2025; no scoring link was present in the inspected 2026 entry. This is an observation about the page, not proof that a 2026 guide exists nowhere. The archive advertises a rolling three-year policy even while these four years appear in its current entries. [Public Chemistry archive](https://apcentral.collegeboard.org/courses/ap-chemistry/exam/past-exam-questions).

| Year | Question PDF | Scoring PDF | What is stored |
|---|---|---|---|
| 2026 | [Questions](https://apcentral.collegeboard.org/media/pdf/ap26-frq-chemistry.pdf) | Not linked on inspected index | Set metadata and seven item references |
| 2025 | [Questions](https://apcentral.collegeboard.org/media/pdf/ap25-frq-chemistry.pdf) | [Scoring](https://apcentral.collegeboard.org/media/pdf/ap25-sg-chemistry.pdf) | Set metadata and seven item references |
| 2024 | [Questions](https://apcentral.collegeboard.org/media/pdf/ap24-frq-chemistry.pdf) | [Scoring](https://apcentral.collegeboard.org/media/pdf/ap24-sg-chemistry.pdf) | Set metadata and seven item references |
| 2023 | [Questions](https://apcentral.collegeboard.org/media/pdf/ap23-frq-chemistry.pdf) | [Scoring](https://apcentral.collegeboard.org/media/pdf/ap23-sg-chemistry.pdf) | Set metadata and seven item references |

Checks of candidate official URLs for 2019, 2021, and 2022 did not retrieve the intended documents. Other years from 1999–2022 are explicitly unexamined inventory gaps. Pre-1999 exams, alternate forms, international administrations, and comprehensive MCQ history were not acquired. No year is inferred to be complete merely because one FRQ set is accessible. Scoring guidelines are source references, not necessarily full pedagogical worked solutions.

Beginning with 2027, College Board says FRQs will be released together in early June, with two sets for most subjects. Not all administered content will be released. A future catalog should record both year and form, and ingest only verified public references. [Release update](https://apcentral.collegeboard.org/courses/past-exam-questions/release-update).

## What the teaching system must cover

The following are design recommendations for expanding this seed corpus; they are not claims that those capabilities already exist.

| Layer | Required teaching capabilities | Present release |
|---|---|---|
| Prerequisites | Algebra, ratios, scientific notation, logs, units, measurement precision | Used in solutions; not a separate remediation course |
| Atoms and bonding | Isotopes, configurations, binding spectra, periodic comparisons, ionic formulas, dot structures, resonance, geometry | Topic seeds plus limited numerical families |
| Matter | Particle pictures, attractions, phases, gas models, mixtures, separation, spectra | Seeds and gas/optics/concentration families |
| Reactions | Atom/charge conservation, ionic equations, limiting amounts, proton/electron transfer | Seeds and quantitative reaction families |
| Rates | Data-derived rate laws, integrated laws, mechanisms, energy barriers, catalysts | Seeds and first/second-order families |
| Energy | Calorimetry, phase heat, enthalpy bookkeeping, bonds, formation references | Seeds and heat/enthalpy families |
| Equilibria | Q versus K, constraints, perturbations, solubility | Seeds and bounded ideal-equilibrium families |
| Acidity | Strong/weak systems, buffers, titration regions, molecular explanations, coupled dissolution | Seeds and acid/buffer families |
| Electrical chemistry | Entropy, Gibbs energy, K, electron accounting, cells, concentration effects, charge | Seeds and thermodynamic/electrical families |
| Experimental reasoning | Controls, uncertainty, calibration, graph construction, error propagation | Eight explicit data/representation seeds; substantial expansion needed |

`CURRICULUM_MAP.md` lists every mapped topic. One item per topic does not prove mastery coverage. Expand each topic into individual objectives, prerequisite edges, alternative representations, misconception-specific feedback, and multi-step applications. Audit these against the current CED before labeling the course complete.

The current practice distribution is deliberately a prototype, not an AP mock exam. Numerical variants dominate. Do not assemble a supposedly representative timed exam by sampling uniformly across all records. Sample against an explicit unit-by-practice blueprint and validate difficulty with student response evidence.

## Answer reliability: recommended architecture

Use the language model to interpret and explain a problem, then use deterministic chemistry and numerical routines to establish the answer. Separate the roles of author, solver, checker, and tutor. A second wording pass by the same model is not independent validation.

Each future quantitative family should carry a structured equation, declared units, parameter domain, physical assumptions, exact or numerical solution method, residual calculation, acceptable equivalent answers, and precision rules. Store coefficients and ion charges explicitly. Do not infer an ion's charge by stripping characters from a display string.

Reject invalid candidates before presenting them. Checks should include element and charge balance, nonnegative amounts, limiting-reagent bounds, activity/concentration assumptions, consistent standard states, temperatures in Kelvin where required, root selection, and uniqueness. Choose a model appropriate to the problem before solving it; an accurate solution to the wrong model is still wrong chemistry.

The prototype checks all numerical items by substitution or inverse relationships. It does not yet have a general reaction balancer, dimensional-analysis engine, activity model, molecular-structure validator, polyprotic solver, or chemistry-aware written-response grader.

Examples of model conditions that need explicit handling:

- The usual pH concentration formula assumes a suitable dilute-solution model. Neutrality means equal hydronium and hydroxide; neutral pH is temperature dependent. [OpenStax pH reference](https://openstax.org/books/chemistry-2e/pages/14-2-ph-and-poh).
- Integrated rate laws must match reaction order. A first-order half-life is concentration independent; the same expression is not universal. [OpenStax kinetics reference](https://openstax.org/books/chemistry-2e/pages/12-4-integrated-rate-laws).
- Distinguish actual reaction Gibbs energy from standard Gibbs energy. A thermodynamic direction is not a rate prediction. [OpenStax free-energy reference](https://openstax.org/books/chemistry-2e/pages/16-4-free-energy).
- The Nernst equation uses the electron count of the balanced reaction and a dimensionless reaction quotient. Match the logarithm base to its coefficient. [OpenStax cell reference](https://openstax.org/books/chemistry-2e/pages/17-4-potential-free-energy-and-equilibrium).

These references support chemistry relationships. No OpenStax exercises or solution passages were copied into the practice bank.

## Teaching without giving the answer

The default policy should be strict guided mode, matching the requested behavior. Do not reveal the final numerical answer, completed derivation, multiple-choice choice, or equivalent near-answer merely because the student says they are stuck. A separate teacher-authorized review mode can be designed later; it should not be unlocked by instructions embedded in a student message or retrieved document.

Recommended turn sequence:

1. Retrieve the current item, its topic, and the student's latest attempt. Ask what they have tried when no attempt is available.
2. Identify the earliest uncertain or incorrect step, rather than replacing their entire approach.
3. Give one narrow question or cue. Wait for an attempt before giving the next cue.
4. Check the submitted step with the relevant mathematical or chemical constraints.
5. Acknowledge a correct step specifically and ask for the next decision.
6. If repeatedly stuck, teach the missing prerequisite using a different example, then return to the original task.
7. Once the student supplies a correct result, confirm it and ask for units, justification, or a reasonableness check as appropriate.

Hints should progress from identifying the relevant principle to setting up the relationship, then to diagnosing a specific algebra or chemistry mistake. A hint can leak the answer even without printing its number, so automated leakage checks and human review are both needed. The current `reveals_final_answer=false` labels are author judgments, not proof of a successful leakage audit.

The student-facing generation context should not receive the entire answer record by default. A backend checker can return a structured result such as `step_valid`, `error_type`, `allowed_next_hint`, and `missing_units`. The answer store stays server-side. SQLite views alone do not protect answers if the full database is delivered to the browser.

For example, a student who multiplies grams by molar mass should receive a units question about canceling grams, not the correct mole count. A student who inserts initial concentrations into K should be asked whether the values describe equilibrium. A student who makes an arithmetic slip after a valid setup should receive an arithmetic cue rather than a lesson that wrongly treats their chemistry as mistaken.

## Recommended data expansion

Add tables for learning objectives, concept prerequisites, validated equation ASTs, chemical species, problem subparts, step dependencies, original scoring rubrics, misconception detectors, validation runs, reviewers, and anonymized skill evidence. Version the chemistry model and each record so a corrected answer can be traced to the affected practice history.

Official references need document-level metadata including release/form identity, retrieval result, rights status, edition, and whether the linked scoring material matches that exact question set. Never treat guessed URLs as verified sources. Annotating public questions is a separate task from acquiring rights to reproduce them.

For original MCQs, generate distractors from known mistakes, solve all options, and reject duplicates or multiple valid answers. For FRQs, create multiple dependent subparts with explicit local scoring criteria and error-carried-forward rules. For visual questions, validate both the underlying data and the rendered diagram; text extraction can lose charges, superscripts, bonds, and graph labels.

Do not train and test on different numeric variants of the same template. Hold out complete families, then separately evaluate transfer to unfamiliar combinations and representations. Measure answer accuracy, invalid-question frequency, unit/charge errors, valid-alternative rejection, answer leakage, and improvement on independently written assessments. No AP score guarantee follows from database size.

## Remaining work before a dependable chatbot

The priority is expert review and broader question structure, rather than multiplying more numeric variants. Expand lab and representation tasks, develop robust step checkers, add cross-topic FRQs and MCQ distractors, and audit every learning objective. Then evaluate the actual multi-turn tutor for hint quality and leakage. The database in this package is ready to inspect and extend, but those production capabilities remain unimplemented.
