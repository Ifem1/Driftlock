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

- Commit `fbd1f3708f6c231e982a9076f6992173ec81ca3b` passed GitHub Actions run `36881540734` (contracts, frontend and CLI jobs).
- All three Studionet deployment receipts and the one-time binding receipt returned `FINALIZED`; exact hashes and addresses are in `deployments/studionet.json` and `docs/LIVE_VALIDATION.md`.
- On-chain schemas matched the expected Registry, Inspector and Judge methods. Registry stats confirmed binding and balanced zero-state accounting.
- Vercel production deployment `dpl_oG3XX2Gd5FHkr2Hn92BPPZHUwFMy` reached READY. Public access and manual browser paths remain unverified because Vercel SSO protection is enabled.

## Live covenant evidence

**Pending.** No covenant, challenge, credit or withdrawal result is claimed here.
