# Driftlock

**Stake a public promise. Prove when it changes.**

Driftlock is a GenLayer-native covenant protocol for changing public information. An owner stakes test GEN behind a precise promise at one canonical HTTPS source. GenLayer first verifies that the source supports the promise and is compliant with the frozen breach rule, with no active breach condition already present. Later, a challenger can ask the protocol to re-fetch that same frozen URL. `SourceInspector` compares the current semantic state with the verified compliant baseline; only a current covenant-relevant non-compliance proceeds to a separate `BreachJudge`, which independently re-fetches the URL before deciding whether the current wording violates the immutable covenant. `DriftRegistry` settles stake and challenge bonds from the finalized result.

This repository is intentionally locked to **GenLayer Studionet**:

- chain ID: `61999`
- RPC: `https://studio.genlayer.com/api`
- explorer: `https://explorer-studio.genlayer.com`
- GenLayer CLI release line: `0.39.1`
- Direct Mode GenVM pin: `v0.2.12`
- browser wallet: injected EIP-1193 only

## Why GenLayer is consequential

A deterministic contract cannot independently fetch a live public policy and semantically decide whether its current wording materially changed or breached a natural-language rule. Driftlock deliberately splits those two nondeterministic questions:

1. **SourceInspector** — was the initial source compliant, and is its present semantic state materially non-compliant relative to that verified baseline?
2. **BreachJudge** — does an independent re-fetch show that the current state violates the frozen covenant?

The Registry never substitutes a server verdict for either consensus result.

## Architecture

```text
OWNER / CHALLENGER
       │
       ▼
NEXT.JS FRONTEND
       │ injected EIP-1193
       ▼
GENLAYER STUDIONET 61999
       │
       ├── DriftRegistry
       │      escrow · deadlines · credits · settlement
       │
       ├── SourceInspector
       │      baseline verification + same-URL current inspection
       │
       └── BreachJudge
              independent breach decision after MATERIAL_CHANGE
```

No application backend, database, cron, queue or central AI service is part of the design.

## Frontend

The frontend is a custom dark editorial interface with Motion-driven scroll storytelling and protocol-state transitions. The visual quality reference is MotionSite Noir (`https://www.motionsite.ai/templates/noir`), but the composition, product interaction, copy and document-comparison system are original to Driftlock.

Routes:

- `/` cinematic protocol story
- `/covenants` live covenant index
- `/covenants/[id]` covenant state, comparison, lifecycle and challenge action
- `/create` multi-stage covenant composer
- `/activity` wallet credits and challenge ledger
- `/protocol` trust-boundary narrative
- `/demo` reviewer evidence surface

The UI reads live protocol state from the deployed Registry. Contract addresses come from [`deployments/studionet.json`](deployments/studionet.json), which records deployment and binding transactions.

## Contract invariants

- a covenant cannot become `ACTIVE` without a finalized verified baseline;
- a verified baseline is compliant with the covenant and contains no active breach condition;
- the bounded semantic baseline result is passed into current inspection; source text and source digests are not stored;
- `NO_RELEVANT_CHANGE` requires a currently compliant source; `MATERIAL_CHANGE` requires accessible same-subject current non-compliance;
- canonical URL, promise, breach rule, permitted changes, beneficiary and finder reward cannot be edited after creation;
- covenant owner cannot challenge their own covenant;
- challengers cannot supply alternate evidence URLs;
- only one challenge may be pending per covenant;
- challenge outcomes do not consume a lifetime quota; cooldown and covenant expiry bound when another attempt can be made;
- source failure / ambiguity / inconclusive judgment cannot create a breach;
- late callbacks cannot re-settle closed state;
- protocol settlement uses pull credits;
- `total_deposited = stake_escrow + bond_escrow + claimable + withdrawn`;
- configured semantic component addresses cannot be replaced after bootstrap;
- no protocol fee or operator verdict override exists.

## Local checks

Python 3.12+:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:GENVM_VERSION="v0.2.12"
genvm-lint check contracts/drift_registry.py --json
genvm-lint check contracts/source_inspector.py --json
genvm-lint check contracts/breach_judge.py --json
pytest tests/direct/ -v
```

Frontend:

```powershell
cd frontend
npm install
npm run test
npm run typecheck
npm run lint
npm run build
npm run dev
```

After installing the pinned Python, root Node and frontend dependencies, run the complete local release gate from the repository root with `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1`. It compiles Python, checks Studionet/source consistency, scans for secrets, runs all three pinned GenVM linter/ABI checks, runs Direct Mode and frontend tests, typechecks, lints, performs the cached offline npm audits and builds the production frontend. The 2026-10-23 release run passed; separate fresh online audits for root and frontend also reported zero vulnerabilities.

## Deployment

### V2 milestone status

The `milestone/driftlock-v2-assurance-appeals` branch contains V2 multi-source policy commitments, bounded rendered-text evidence and a bonded appeal lifecycle. Corrected V2 contracts are deployed and bound on Studionet; the active manifest and production app point to them. Local release gates pass. Live evidence includes a verified baseline, unchanged-source challenge and upheld bonded appeal, plus a controlled source change, independent breach judgment, stake payout and credit withdrawals through the V2 Registry's retained V1-compatible single-source method. V2 multi-source attempts that conflicted with corroboration correctly remained ambiguous; a V2 multi-source breach appeal is not claimed. Injected-wallet browser paths and hosted CI are not claimed. Start with [`MILESTONE_V2.md`](MILESTONE_V2.md) and [`docs/milestone-v2/LIVE_VERIFICATION.md`](docs/milestone-v2/LIVE_VERIFICATION.md). Historical V1 receipts are preserved in [`deployments/studionet-v1.json`](deployments/studionet-v1.json).

The current release is deployed to Studionet `61999`. Its Registry, SourceInspector, BreachJudge, deployment transactions and one-time binding transaction are recorded in [`deployments/studionet.json`](deployments/studionet.json). `deploy/deployDriftlock.ts` is retained for reproducibility; it is not part of frontend operation.

The intended bootstrap order is:

1. deploy unbound `DriftRegistry`;
2. deploy `SourceInspector` bound to the Registry;
3. deploy `BreachJudge` bound to the Registry;
4. bind the Inspector/Judge into Registry exactly once;
5. verify schemas/stats and only then configure the production frontend.

Do not treat a transaction hash as proof of finality. Submission evidence must distinguish submitted, accepted and finalized state.

## Evidence and validation

The V2 local gate passes all three GenVM linter/ABI checks, 69 Direct Mode contract tests, 21 frontend tests, Python compile/preflight and secret scanning, TypeScript typecheck, ESLint, cached offline dependency audits, and the Next.js production build with the active V2 manifest. Fresh online audits also report zero vulnerabilities. The production Vercel deployment is ready and its six routes and contract addresses were checked over HTTP. Hosted GitHub Actions and injected-wallet browser verification are not claimed.

Deployment receipts, read-back evidence and evidence limits are documented in [`docs/LIVE_VALIDATION.md`](docs/LIVE_VALIDATION.md). Driftlock stores a bounded semantic baseline result, not the fetched source document, a source digest, or an exact historical page snapshot. Current inspection is evaluated relative to that verified baseline, and BreachJudge independently re-fetches the same frozen canonical URL before settlement. A controlled live source-change and breach payout transaction set is documented in [`docs/milestone-v2/LIVE_VERIFICATION.md`](docs/milestone-v2/LIVE_VERIFICATION.md); the V2 multi-source breach appeal path remains unverified.
