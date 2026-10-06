# Review evidence

This file intentionally contains no invented live evidence.

## Repository evidence

- semantic responsibilities are split across three contracts;
- source URLs are HTTPS-only and bounded;
- source render text is bounded;
- component callers are authenticated;
- challenge history reads are paginated, and cooldown plus covenant expiry bound attempts in time;
- challenge spam is cooldown-gated;
- deterministic accounting exposes a conservation invariant;
- frontend has no application backend and uses injected EIP-1193 only;
- CI checks contracts and frontend.

## Verified release evidence

- Challenge-recovery commit `e7642875db65b8e94410c18d12c819493122a022` passed [GitHub Actions run `37520947317`](https://github.com/Ifem1/Driftlock/actions/runs/37520947317), including all three GenVM checks, 31 Direct Mode tests, 17 frontend tests, typecheck, lint, build and CLI version check.
- All three current Studionet deployment receipts and the one-time binding receipt finalized with successful leader execution; addresses and hashes are in `deployments/studionet.json` and `docs/LIVE_VALIDATION.md`.
- Registry read-back confirmed the configured component addresses, chain ID 61999, and balanced zero-state accounting.
- The project owner reports manually verifying injected-wallet browser interaction and transactions; these checks are separate from CI.

## Evidence limits

This repository does not include a canonical complete demo-covenant lifecycle transaction set. Deployment and browser verification do not imply such a recorded lifecycle. GenLayer validators independently re-evaluate covenants against the same frozen canonical URL; the contracts store the semantic baseline result and its basis, not fetched source text or a source digest.
