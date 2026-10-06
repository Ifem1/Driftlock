# Repository validation

The semantic hardening passed all three GenVM lint and validation checks with GenVM `v0.2.12`, 52 Direct Mode tests, 19 frontend tests, TypeScript typecheck, ESLint, and the Next.js production build. The repository-local GenLayer CLI reports `0.39.1`. GitHub Actions records the checks for each pushed commit.

The project owner reports manually verifying the injected-wallet browser experience, including wallet interaction and transactions, account and chain changes, rejection handling, and responsive behavior. These are manual browser checks, not automated CI coverage.

The deployment receipts and current addresses are summarized in [`LIVE_VALIDATION.md`](LIVE_VALIDATION.md).
