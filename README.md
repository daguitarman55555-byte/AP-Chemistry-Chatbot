# Chemistry Studio — AP Chemistry tutor

A working local web application for guided practice, chemistry step checking, and interactive graphs, with an OpenAI Responses integration for open-ended conversation. **The complete coverage requirement is not yet met, and live AI tutoring has not been verified.**

## Start

Install Python 3.10+ and Node.js 22+. Download or clone this branch, then run:

```sh
python launch.py
```

On Windows, double-click `Start.bat` after installing the prerequisites. The launcher builds the question bank and interface, runs the audit, and opens the app. Keep its terminal window open. On later runs the generated assets are reused; use `python launch.py --rebuild` after updating the generators or frontend.

Practice, authored hints, arithmetic checks, atom/charge conservation checks, common-unit conversions, and graph exploration work without a model key. Open-ended chat supports OpenAI or Groq. OpenAI remains the default (`OPENAI_API_KEY`, optionally `OPENAI_MODEL`); for Groq set `AI_PROVIDER=groq`, `GROQ_API_KEY`, and optionally `GROQ_MODEL` (default `openai/gpt-oss-120b`). Do not paste credentials into chat, expose them to browser code, or commit them. The app displays an explicit unconfigured state when the selected provider's key is absent; it does not simulate an AI reply.

For a teen-facing deployment, the API account, billing, consent, retention settings, and usage limits should be administered by a parent/guardian, school, or other authorized adult organization. Hosted APIs are metered rather than unlimited. Set a small project budget and alert in the provider dashboard before public testing. The server already keeps the key off the client, disables provider-side response storage for requests, bounds tool calls and output length, and withholds solution keys from the model.

This server binds to your computer's loopback address. It is not a public classroom deployment. A production deployment needs authenticated accounts, durable data controls, per-user budgets, and a production web server before it is opened to other users.

## What is implemented

- React chat workspace with all nine units and 91 selectable topics, practice-family selection, staged hints, and attempts.
- Server-owned answer keys; only the selected prompt, permitted hint, grade feedback, and author-approved graph stimulus reach the interface.
- Bounded arithmetic parsing without `eval`, finite-number checks, common compatible-unit conversions, and atom/charge conservation checks for formulas and ions.
- 24 original graph models, each with 100 parameter sets, interactive coordinate inspection, labeled axes, and accessible 201-row data tables.
- LaTeX and `\ce{...}` chemical notation using KaTeX with untrusted commands disabled.
- A bounded, server-side Responses API tool loop, retained conversation context, curriculum references, error handling, and honest verification labels.
- Local-first retrieval over 91 authored curriculum chunks. Exact conceptual matches avoid a provider call; other queries send at most three compact chunks and eight recent messages to economize tokens. Active practice excludes its topic's answer chunk.
- PhET project references matched to topics. Simulations are external references; they are not bundled, embedded, or instrumented.
- A coverage panel backed by the same reproducible evidence files included here.

## Exact content counts

| Measure | Count |
|---|---:|
| Original practice records | 12,202 |
| Numerical chemistry items | 2,503 |
| Graph-reading drills | 9,600 |
| Conceptual / laboratory seeds | 99 |
| Authored family labels | 221 |
| Families with at least 100 variants | 121 |
| Families below 100 variants | 100 |
| Graph datasets / points | 2,400 / 482,400 |
| Staged hints | 24,504 |
| Topics meeting 200 validated distinct types | **0** |
| Expert-reviewed items | **0** |

The 121 families reaching 100 variants are 25 numerical chemistry families plus four graph-literacy operations for each of 24 graph models. The remaining families are 91 conceptual seeds, eight laboratory/data seeds, and formal-charge bookkeeping with three cases. **A different number, wording, or graph-model label is not proof of a genuinely different chemistry reasoning type.** The item count must not be interpreted as exhaustive mastery coverage.

The exam catalog holds source links for 28 official FRQ references across four verified public sets; no complete past-exam archive or official worked-solution corpus is claimed. See the research and archive audit under `corpus/`.

## Inspect the proof

- [Every family and variant count](evidence/families.csv)
- [Every topic and its gaps](evidence/topics.csv)
- [Machine-readable checks and source hashes](evidence/coverage.json)
- [Rendered-interface QA and limits](evidence/QA.md)
- [Development handoff and remaining work](HANDOFF.md)

Reproduce the checks:

```sh
python corpus/rebuild_all.py
python audit.py
npm ci --prefix web --ignore-scripts
npm run build --prefix web
```

The audit exercises all **12,103 numerical records**: correct results are accepted, deliberate wrong results are rejected, and nonfinite/code-like input is rejected. It also runs **41 unit/integration tests** covering parsing, conservation, units, server routes, session isolation, answer separation, and the provider contract. The corpus rebuild runs inverse/substitution checks and a separate graph/conservation validator. These checks establish their stated mathematical/software properties; they do not certify every explanation or model choice as correct chemistry.

The breadth release gate deliberately exits with failure:

```sh
python audit.py --require-full-coverage
```

To test an actually configured model, explicitly run `python live_evaluation.py --limit 9`. It incurs API usage, records results locally, and leaves chemistry and answer-leakage review marked **pending**. It is not run in CI and has not been run successfully in this environment.

## Important remaining limits

Written explanations receive provisional AI feedback or a human-review notice, not an AP score. The arithmetic checker cannot validate the chemical setup; the conservation checker cannot determine whether a reaction occurs. No general Lewis-structure, particle-diagram, polyprotic-equilibrium, or experimental-design validator exists yet. Images and file uploads are not supported.

The model is instructed to guide without giving final answers, and never receives the stored solution key. That is **not a proof that an LLM cannot independently solve and reveal a result**, particularly under adversarial prompts. Live multi-turn pedagogy and leakage evaluations remain required. Public source code necessarily allows someone to reproduce the answer bank; the student web routes enforce separation, not secrecy from repository readers.

PhET licensing and source provenance are recorded in the catalog; ordinary simulation links do not provide state access. Course references and official exam links are listed in [the research report](corpus/RESEARCH_AND_TUTOR_DESIGN.md). No restricted AP Classroom content, copied exam prompts, or student records are included.

Technical references: [OpenAI function calling](https://developers.openai.com/api/docs/guides/function-calling), [KaTeX API](https://katex.org/docs/api.html), [KaTeX security options](https://katex.org/docs/options.html).
