# Driftlock

**Stake a public promise. Prove when it changes.**

Driftlock is a GenLayer-native covenant protocol for changing public information. An owner stakes test GEN behind a precise promise at one canonical HTTPS source. GenLayer first verifies that the promise actually exists. Later, a challenger can ask the protocol to re-fetch that same frozen URL. `SourceInspector` determines whether a material relevant change occurred; only then does a separate `BreachJudge` decide whether the current wording violates the immutable covenant. `DriftRegistry` settles stake and challenge bonds from the finalized result.

This repository is intentionally locked to **GenLayer Studionet**:

- chain ID: `61999`
- RPC: `https://studio.genlayer.com/api`
- explorer: `https://explorer-studio.genlayer.com`
- GenLayer CLI release line: `0.39.1`
- Direct Mode GenVM pin: `v0.2.12`
- browser wallet: injected EIP-1193 only

## Why GenLayer is consequential

A deterministic contract cannot independently fetch a live public policy and semantically decide whether its current wording materially changed or breached a natural-language rule. Driftlock deliberately splits those two nondeterministic questions:

1. **SourceInspector** — did the immutable canonical source materially change in a relevant way?
2. **BreachJudge** — does that verified change violate the frozen covenant?

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

The UI reads live protocol state from the deployed Registry. Production contract addresses are configured through frontend environment variables and recorded with deployment transactions in [`deployments/studionet.json`](deployments/studionet.json).

## Contract invariants

- a covenant cannot become `ACTIVE` without a finalized verified baseline;
- canonical URL, promise, breach rule, permitted changes, beneficiary and finder reward cannot be edited after creation;
- covenant owner cannot challenge their own covenant;
- challengers cannot supply alternate evidence URLs;
- only one challenge may be pending per covenant;
- a covenant has a hard lifetime challenge cap;
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

## Deployment

The current release is deployed to Studionet `61999`. Its Registry, SourceInspector, BreachJudge, deployment transactions and one-time binding transaction are recorded in [`deployments/studionet.json`](deployments/studionet.json). `deploy/deployDriftlock.ts` is retained for reproducibility; it is not part of frontend operation.

The intended bootstrap order is:

1. deploy unbound `DriftRegistry`;
2. deploy `SourceInspector` bound to the Registry;
3. deploy `BreachJudge` bound to the Registry;
4. bind the Inspector/Judge into Registry exactly once;
5. verify schemas/stats and only then configure the production frontend.

Do not treat a transaction hash as proof of finality. Submission evidence must distinguish submitted, accepted and finalized state.

## Evidence and validation

Submission-readiness commit `93a4434f52fb62be04c1c4c606cfdd83198d020c` passed GitHub Actions run [`37244901884`](https://github.com/Ifem1/Driftlock/actions/runs/37244901884): all three GenVM checks, 30 Direct Mode tests, 14 frontend tests, typecheck, lint, production build and CLI version check. The project owner reports manually verifying injected-wallet browser paths, including wallet transactions, account and chain changes, rejection behavior and responsive wallet behavior. Manual checks are separate from CI.

Deployment receipts, read-back evidence and evidence limits are documented in [`docs/LIVE_VALIDATION.md`](docs/LIVE_VALIDATION.md). GenLayer validators independently re-evaluate a covenant against the same frozen canonical URL. The protocol does not claim to archive a permanent historical snapshot or diff of each later fetched page. This repository does not present a complete canonical demo-covenant lifecycle transaction set.
