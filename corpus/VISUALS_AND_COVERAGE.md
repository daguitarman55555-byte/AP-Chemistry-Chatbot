# Interactive visuals, PhET, and question breadth

## Implemented artifacts

The offline `graph_explorer.html` contains 960 selectable parameter datasets across 24 model families and 192,960 sampled points. It has a family selector, a parameter-set slider, point inspection, labeled axes, model assumptions, and accessible data tables. No network connection is required for that file. It is an exploration prototype, not a deployed chatbot feature.

The data are original calculations from declared models, not experimental observations or extracted PhET measurements. Forty parameter cases of one graph model remain one model family. Synthetic spectra and pair potentials are explicitly schematic. Arrhenius and temperature-dependent equilibrium calculations are identified as quantitative enrichment models rather than a guarantee of AP-required calculation scope.

The question bank adds 3,840 graph-reading drills: four operations for each dataset. These cover an ordinate, a signed change, an average slope, and a comparison of changes. Together with the original 727 items, the package contains 4,567 question records. It has 221 authored families across the course, not 221 rigorously proven independent skills. Expert and semantic-duplicate audits remain outstanding.

Database and numerical checks pass. Browser inspection of the standalone viewer was attempted, but the available remote browser rejected the local preview address with `ERR_BLOCKED_BY_CLIENT`. Its rendered layout and interactions therefore remain unverified; the package records this limitation rather than calling it browser-tested.

## PhET integration findings

Seventeen relevant PhET source repositories were verified, with proposed topic mappings in `phet_catalog.json`. They include atomic structure, isotope mass, particle interactions, molecular polarity, phases, gas behavior, concentration, pH, acid/base solutions, optical absorption, balancing, limiting reactants, and energy transfer. These mappings are author recommendations, not official AP alignments.

The current PhET licensing page says regular HTML simulations use CC BY-NC 4.0 and require attribution; commercial use needs a separate license. PhET-iO provides programmable interaction and data-streaming capabilities under separate licensing. Source repositories can have different code licenses, so a repository's license must not be mistaken for the license of a branded distributed simulation. [PhET licensing](https://phet.colorado.edu/en/licensing), [PhET-iO](https://phet-io.colorado.edu/).

This release catalogs references only. It does not bundle PhET binaries, establish embedding rights for a particular product, acquire PhET-iO access, or claim to read a simulation's internal state. Ordinary iframe display alone does not grant such access. The catalog links verified official repositories, which provide their published-simulation links. Runtime interactions were not tested.

## Future visual tools for the chatbot

The tutor should select a structured visualization type instead of generating unrestricted executable code. An allowlist should include Cartesian curves, scatterplots, error bars, particle diagrams, energy diagrams, spectra, titration curves, molecular geometry, and cell schematics. This release supplies Cartesian datasets and a viewer; the other renderers remain design requirements.

Each request should declare its topic, learning objective, model, units, parameter bounds, data provenance, interaction controls, accessibility alternative, and whether the curve is a question stimulus or a hidden solution. Permit bounded sliders, point selection, axis transformations, and student prediction overlays. Validate numeric ranges, finite values, charge and matter conservation when applicable, and model assumptions before rendering.

In guided mode, reveal only task-author-approved visuals. A curve can give away a root, endpoint, equivalence volume, or ranking even without printing an answer. Keep hidden solution curves and fit parameters server-side. For PhET simulations that display answer-relevant values, use a different exploratory setup or withhold the simulation until the student has completed the step; do not obscure PhET's required branding.

Support keyboard operation, a data-table alternative, readable axis labels, clear units, touch targets, and reduced motion. Do not require hover. Never use decorative image generation for scientific plots or precise molecule structures.

## The 200-types-per-topic requirement

The requested target is tracked for each of the 91 numbered topics: **18,200 distinct question types in total**, before variants. It has not been met. No topic is marked complete.

The coverage file reports both authored families and expert-validated types. It currently records zero expert-validated types, because no independent chemistry review has been performed. Numerical variants, cosmetic rewording, and empty placeholder rows are not counted as new types. The existing graph tasks improve practice volume but do not close the breadth gap by themselves.

A new type should change the chemistry reasoning structure or the evidence the student must interpret. Possible distinctions include forward versus inverse inference, competing models, particle-to-symbol translation, data-derived parameters, coupled constraints, experimental design, systematic-error diagnosis, mechanism discrimination, and written argument evaluation. Not all distinctions are meaningful for every narrow topic.

For each candidate type, require: a concrete example, a worked solution, a defined domain, targeted misconception, staged hints, prerequisite mapping, semantic-duplicate review, and a verifier. Then test at least boundary and interior instances. Review visual tasks with the actual stimulus attached. Only approved types should count toward the 200 target.

The remaining effort is a substantial authorship and validation project, not simply a larger download. The current package is a reproducible checkpoint with explicit gaps, not the complete requested corpus.
