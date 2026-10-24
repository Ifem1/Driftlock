# Studionet V2 deployment

Target chain: `61999`; RPC: `https://studio.genlayer.com/api`; explorer: `https://explorer-studio.genlayer.com`; repository CLI: `0.39.1`; GenVM: `v0.2.12`.

## Current deployment

Corrected source revision `f9793cc67ad11ebcf89b420c624e9e8ad537dced` was deployed and bound successfully. The active manifests are `deployments/studionet.json` and `deployments/studionet-v2.json`. Addresses, transaction hashes, source digests, live lifecycle receipts and superseded test escrow are in [`LIVE_VERIFICATION.md`](LIVE_VERIFICATION.md). V1 receipts are preserved in `deployments/studionet-v1.json`; all earlier V2 deployments are retained in versioned manifests.

## Production frontend

The Vercel production deployment `dpl_ABEmiqSHoXgfWvTyPD6nuHaPw722` is the final baseline-restored deployment aliased to `https://driftlock-nine.vercel.app`. The remote Next.js build passed; the six public routes previously returned HTTP 200, and the delivered bundle includes the current Registry and Inspector addresses. See [`LIVE_VERIFICATION.md`](LIVE_VERIFICATION.md) for live source-test and browser limits.

## Local release gate

Run `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1` from the repository root. It runs Python compilation, deployment preflight, secret scan, all three GenVM lint/ABI checks, Direct Mode contract tests, frontend tests, typecheck, ESLint, cached offline npm audits, and a production build. On 2026-10-23, this gate passed with 69 Direct Mode tests and 21 frontend tests. Fresh online root and frontend npm audits also reported zero vulnerabilities.

## Remaining live evidence

The final deployment completed a live baseline, unchanged-source challenge, bonded appeal, settlement and pull-credit withdrawal. The later `dl-5`/`dc-5` multi-source run finalized a source-change breach, bonded appeal, upheld judgment, settlement and withdrawal. Chrome QA covered wallet account changes, refresh recovery, wrong-network handling and signing; explicit transaction rejection remains untested. Read-only status confirms test stakes and a challenge bond remain in escrow; no expiry or withdrawal transaction was sent during this closeout. Exact balances, expiry times, addresses and receipts are in [`LIVE_VERIFICATION.md`](LIVE_VERIFICATION.md).

Deployment is reproducible with `deploy/deployDriftlock.ts`. Keep wallet keys in the operating system credential store. Never commit key material or `.env.local`.
