# Repository validation

GitHub Actions quality run [`36902874013`](https://github.com/Ifem1/Driftlock/actions/runs/36902874013) passed for canonical `main` commit `8a8a805364cfc9ede797732af88fa51627fd6c89`. CI passed all three GenVM lint/validation checks, 30 Direct Mode tests, 9 frontend tests, TypeScript typecheck, ESLint, Next.js production build and the GenLayer CLI version check.

The project owner also reports manually verifying the injected-wallet browser experience, including real wallet interaction and transactions, account and chain changes, rejection handling and responsive wallet behavior. These are manual browser checks, not automated CI coverage.

Deployment receipts, schemas and live contract reads are summarized separately in [`LIVE_VALIDATION.md`](LIVE_VALIDATION.md).

## Final submission cleanup checks

On the canonical-main-based cleanup checkout, all three `genvm-lint check` commands passed with GenVM `v0.2.12`; Direct Mode passed **30 tests**; frontend Vitest passed **14 tests**; TypeScript typecheck, ESLint, Next.js production build and `git diff --check` passed. The frontend tests include transaction execution-result and chain-switch confirmation regressions. The production build emits a Next.js warning that it inferred the repository root from the root lockfile while also finding the frontend lockfile.
