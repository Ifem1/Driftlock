# Driftlock V1 baseline

- Pre-milestone HEAD: `4987c25a726e2ff8db0fb5bf8f76daa750c970bb` (verified 2026-10-23).
- Milestone branch: `milestone/driftlock-v2-assurance-appeals`, created from this exact commit. The three baseline documents were already present as untracked files when implementation began.
- This is an evidenced repository baseline, not a claim of official acceptance.
- V1 components: `DriftRegistry`, `SourceInspector`, `BreachJudge`, and a Next.js injected-wallet frontend.
- V1 freezes one canonical HTTPS URL and a semantic covenant, verifies a compliant baseline, inspects that URL later, independently re-fetches it for breach judgment, then settles stake/bonds through Registry callbacks and pull credits.
- V1 contains timeout/retry/expiry recovery and no lifetime challenge quota. Baseline storage is bounded semantic data; the contracts do not store source text, source digest, or exact historical page snapshots.
- Deployment manifest at baseline identifies Studionet chain 61999 deployment; that deployment is V1 and cannot be represented as V2.
- Baseline Direct Mode suite was rerun locally before V2 edits: **52 passed**. The historical frontend test count in V1 docs was 19; the current checkout has 20 frontend tests.
- No reliable evidence identifying a formally accepted GenLayer submission commit was found. `4987c25` is a repository baseline only.
- Key limitations motivating V2: one-source assurance; no committed immutable historical artifact; no bonded appeal stage; product UI exposes only V1 lifecycle.
