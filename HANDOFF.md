# Development handoff

The requested product is an AP Chemistry chatbot that covers the entire course, creates valid questions, and guides students without giving final answers. The breadth target is 200 distinct question types per numbered topic and at least 100 variations within each type. This branch does not meet that target; do not relabel numerical variants to make the numbers appear complete.

## Implemented in this branch

`server.py` serves a loopback-only React frontend from `web/dist`. `chat_engine.py` manages practice and conversation context and calls the OpenAI Responses API using environment credentials. `tutor.py` grades stored numerical answers and gates authored hints. `chemistry_tools.py` checks bounded arithmetic and atom/charge conservation. `units.py` handles explicit common-unit conversions. `launch.py` prepares assets and starts the app.

`corpus/rebuild_all.py` produces 12,202 original records and 2,400 graph datasets. `audit.py` generates per-family/per-topic evidence and executes 41 tests. The 121 families with 100 cases consist of 25 numerical chemistry families and 96 graph-task labels; only four graph-literacy operations are involved. The other 100 family labels remain below 100 cases. No expert validation or full course coverage is claimed.

Browser QA uses local Playwright because the cloud browser refused localhost with `ERR_BLOCKED_BY_CLIENT`. The regular Chromium download timed out; a Chromium package from npm was used for local QA, unpacked without archive ownership restoration. The app and browser were launched in the same process environment because standalone command sessions do not share loopback networking here. Do not commit this runtime bundle. See `evidence/QA.md` for actual observed results.

## Remaining work, in priority order

1. Configure the server model externally and run the live evaluation harness. No API key was available during implementation. Fake-provider tests verify contract and tool flow only.
2. Audit the entire course at objective/essential-knowledge level. Author and independently review genuinely distinct reasoning types; the existing 91 topic labels are only a framework.
3. Add validated mechanisms for molecular structures, diagrams, coupled and polyprotic equilibria, experimental design, and chemistry-aware written reasoning. Avoid presenting model text as deterministic verification.
4. Evaluate multi-turn tutoring with real chemistry examples and adversarial prompts. The API never reads the answer store, but model instructions alone cannot guarantee no answer disclosure.
5. Implement a controlled question-authoring pipeline: domain specification, solver, separate checker, uniqueness/validity checks, and editorial review. Current generation is deterministic finite parameter families, not unrestricted trustworthy authoring.
6. Extend the official exam/form catalog only from verified public sources. Existing 28 item references do not constitute all past exams. Do not copy protected exam text or ingest secure AP Classroom materials.
7. Validate PhET runtime links and decide product licensing before any embedding or bundling. Current references point to official projects; no state instrumentation exists.
8. For public hosting, add user authentication, persistent progress with retention controls, production serving, and robust user/cost limits. The current ephemeral token sessions and loopback server are for local use.

## Verification discipline

Rebuild first, then run `python audit.py`. Tests must reject zero for small nonzero photon energies; an earlier absolute-tolerance bug was fixed. pH uses a dedicated absolute tolerance. Formula checks use explicit ion syntax (`Fe^3+`, `e^-`) and do not guess ambiguous charges. Reactions require spaced plus separators. Unsupported formulas and units must be rejected with an explanation.

The `--require-full-coverage` audit gate is intentionally failing until the breadth target is actually reached and reviewed. Preserve that distinction in future reports. Source hashes and CSV inventories make skipped or underdeveloped families visible.

Use isolated branches and non-force ref updates. Never commit credentials, student conversations, or restricted exam content. Generated corpus exports, frontend dependencies/build assets, and live evaluation logs remain ignored.
