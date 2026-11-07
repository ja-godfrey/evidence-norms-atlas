# Camera-ready release notes — November 6, 2026

Jason Godfrey, University of Michigan, jgod@umich.edu.

Kaggle version 4 is the current data-and-code release for *Auditing Evidence Framing at NeurIPS: A Decade-Scale Study of Accepted Papers*. Versions 1–3 remain historical versions and are superseded for reproduction. Code, documentation, download preparation and presentation links are corrected here; the measured data, anchors, ratings, embeddings and reported results are unchanged.

## Measurement guidance

| Topic | Current interpretation and evidence |
| --- | --- |
| Axis design | Concept-led, researcher-specified, non-exhaustive axes; no systematic search over candidate sets. `ANCHORS.md` gives the rationale and all 56 exact anchor sentences. |
| Construction and freeze | Sentences synthesize facets across examples; the author recalls LLM assistance and reviewing wording. The retained checksum and self-reported timeline establish the retained instrument, not preregistration or absence of prior inspection. See `PROVENANCE.md`. |
| Validation | Blinded LLM ratings assess construct recognizability, not a human gold standard. D&B track membership is an external positive control. Lexical/LDA checks and alternate-encoder checks answer different questions. See `RATERS.md` and the paper's measurement section. |
| Shared bias | GPT–GPT mean QWK 0.893 versus GPT–Claude 0.868 does not rule out shared bias. Per-axis agreement varies. There were no human annotators; legacy `human_*` identifiers refer to Claude agents. |
| Sensitivity | Empirical-performance changes from 0.750 to 0.313 with neutral negatives; scale/capability is 0.154 under SPECTER versus 0.606 under MiniLM. Artifact-release leave-one-out shifts span −0.070 to 0.413. Only the four core longitudinal axes retain signs across those anchor checks. |
| Scope | 19,361 accepted NeurIPS title-and-abstract records from 2015–2024, including 174 separate 2021 D&B records. No full-paper, rejected-submission, review-process or other-venue evidence. Abstracts supply a consistent public genre across this corpus. |
| Interpretation | Topic controls are descriptive adjustments. Residual endpoint differences are not regression slopes or causal effects. Accepted-paper trends cannot separate authorial changes from selection and capacity. |
| Policy and transfer | No claim about meeting the field's goals, no identified intervention or predicted policy effect. An annual report illustrates monitoring. AISTATS/COLT specialization is a possible untested explanation. Full-paper and cross-venue studies remain future work. |
| Reuse | Pinned software, measured CPU timings, tested subsets and missing historical costs are in `REPRODUCE.md`. `EXTENDING.md` documents executable alternative-anchor analysis; old ratings do not validate a new instrument. |
| Presentation | Title/author search, animation and projections are presentation additions. Their examples are illustrative, projections distort distances, and per-paper scores must not rank paper or author quality. They add no new scientific validation. |

## Frozen historical artifacts

The 111 reviewed data files remain available to make the scientific record inspectable. Twenty-two CSVs and processed metadata restore titles; the other 88 are byte-identical. The added data explorer is separate. Historical README files, reports, manifests and the original aggregate HTML preserve their reviewed wording, including anonymous packaging, legacy rater labels and earlier interpretations. They are historical evidence, not the current release's instructions or interpretation. This note, the release README, data card, scope document and rater documentation supersede those statements. The original aggregate's plotted values are unchanged; the code's aggregate copy adds a visible current-scope notice.

All derived values and the 56 frozen anchor sentences are unchanged. `CHANGELOG.md` and `release_manifest.json` enumerate data differences and hashes; `SHA256SUMS.txt` and `SOURCE_SNAPSHOT.json` identify the current public files. Titles and public bylines are third-party bibliographic metadata outside the CC BY grant. Abstracts, excerpts, raw HTML, model weights and private reviews are absent.

## Packaging corrections

Version 4 supplies a complete working copy of code and data, so setup and tests need not alter a verified download. README and citation links point to the public Kaggle distribution. Every code explorer has its aggregate target. Current metadata tooling handles Kaggle's unnamed CSV index without changing data, uses isolated validation caches, and supports the hosted checker's current client. Internal publication plans and obsolete preflight reports are omitted from the public source snapshot. Final Croissant metadata and its validation report are generated separately from the published version to avoid an archive-checksum cycle.
