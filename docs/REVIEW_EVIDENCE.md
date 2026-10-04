# Review evidence

This file intentionally contains no invented live evidence.

## Repository evidence

- semantic responsibilities are split across three contracts;
- source URLs are HTTPS-only and bounded;
- source render text is bounded;
- component callers are authenticated;
- covenant history is lifetime-bounded and reads are paginated;
- challenge spam is cooldown-gated;
- deterministic accounting exposes a conservation invariant;
- frontend has no application backend and uses injected EIP-1193 only;
- CI checks contracts and frontend.

## Verified release evidence

- Canonical `main` commit `8a8a805364cfc9ede797732af88fa51627fd6c89` passed [GitHub Actions run `36902874013`](https://github.com/Ifem1/Driftlock/actions/runs/36902874013), including all three GenVM checks, 30 Direct Mode tests, 9 frontend tests, typecheck, lint, build and CLI version check.
- All three Studionet deployment receipts and the one-time binding receipt returned `FINALIZED`; exact hashes and addresses are in `deployments/studionet.json` and `docs/LIVE_VALIDATION.md`.
- On-chain schemas matched the expected Registry, Inspector and Judge methods. Registry stats confirmed binding and balanced zero-state accounting.
- Production Vercel deployment `dpl_AqVWENg9KbJNHM5DkM7skMhXwWvu` reached READY. The project owner reports manually verifying injected-wallet browser interaction and transactions; these checks are separate from CI.

## Evidence limits

This release repository does not include a canonical complete demo-covenant lifecycle transaction set. Deployment and browser verification do not imply such a recorded lifecycle. GenLayer validators independently re-evaluate covenants against the same frozen canonical URL; the contracts do not archive a permanent snapshot or diff of every later fetched page.
