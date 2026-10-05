# Repository validation

Submission-readiness commit `93a4434f52fb62be04c1c4c606cfdd83198d020c` passed GitHub Actions run [`37244901884`](https://github.com/Ifem1/Driftlock/actions/runs/37244901884). CI passed all three GenVM lint/validation checks, 30 Direct Mode tests, 14 frontend tests, TypeScript typecheck, ESLint, Next.js production build and the GenLayer CLI version check.

The project owner also reports manually verifying the injected-wallet browser experience, including real wallet interaction and transactions, account and chain changes, rejection handling and responsive wallet behavior. These are manual browser checks, not automated CI coverage.

Deployment receipts, schemas and live contract reads are summarized separately in [`LIVE_VALIDATION.md`](LIVE_VALIDATION.md).

## Final submission cleanup checks

On the submission-readiness commit, all three `genvm-lint check` commands passed with GenVM `v0.2.12`; Direct Mode passed **30 tests**; frontend Vitest passed **14 tests**; TypeScript typecheck, ESLint and the Next.js production build passed. The frontend tests include transaction execution-result and chain-switch confirmation regressions. The production build emits a Next.js warning that it inferred the repository root from the root lockfile while also finding the frontend lockfile.
