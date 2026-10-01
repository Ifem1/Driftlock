# Local validation

Verified after rebasing `codex/audit-fix` onto canonical `main` (`8a8a805364cfc9ede797732af88fa51627fd6c89`) on 2026-10-01. Python was 3.12.10, the local Node.js runtime was 24.16.0, GenLayer CLI was 0.39.1, and GenVM was pinned to v0.2.12. CI separately runs Node 22 as configured in `.github/workflows/quality.yml`.

## Results

- `python -m pytest tests/direct/ -v`: **41 passed**.
- `genvm-lint check` for Registry, Inspector and Judge with `GENVM_VERSION=v0.2.12`: **all PASS**, including SDK validation.
- `npm ci`: **PASS**.
- `npm --prefix frontend ci`: **PASS**.
- Frontend Vitest: **12 passed** across 2 files.
- TypeScript typecheck: **PASS**.
- ESLint: **PASS**.
- Next.js production build: **PASS**.
- `git diff --check`: **PASS**.
- GitHub Actions quality run for pre-rebase commit `7048cefa430fbde3fbfca8f125ec58d94a540eb8`: **success** ([run 36928565791](https://github.com/Ifem1/Driftlock/actions/runs/36928565791)). CI for the rebased branch will run after it is pushed.

The tests cover bounded baseline evidence, unchanged and changed source, an already-breached baseline, evidence disagreement and tampering, callback replay, challenge-cap exhaustion resistance, withdrawal authorization, and wallet network/account preconditions. The Direct Mode lifecycle test suite manually supplies Registry callbacks in several Registry tests; it does not replace live Studionet proof. The live proof is documented separately in `LIVE_VALIDATION.md`.

## Reproduction

```powershell
$env:GENVM_VERSION="v0.2.12"
python -m pytest tests/direct/ -v
genvm-lint check contracts/drift_registry.py --json
genvm-lint check contracts/source_inspector.py --json
genvm-lint check contracts/breach_judge.py --json
npm ci
./node_modules/.bin/genlayer --version
npm --prefix frontend ci
npm --prefix frontend run test
npm --prefix frontend run typecheck
npm --prefix frontend run lint
npm --prefix frontend run build
```

Live Studionet settings: chain ID `61999`, RPC `https://studio.genlayer.com/api`, explorer `https://explorer-studio.genlayer.com`. Local checks and the CI run do not claim browser-wallet testing.
