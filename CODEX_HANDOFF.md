# Project handoff

The contract audit, corrected Studionet deployment, three-wallet end-to-end proof, and production frontend deployment are complete. Read [`docs/LIVE_VALIDATION.md`](docs/LIVE_VALIDATION.md) for verified transactions and [`docs/LOCAL_VALIDATION.md`](docs/LOCAL_VALIDATION.md) for the local test matrix.

## Release state

- Branch: `codex/audit-fix`.
- Contract source deployed from commit `a092268bdeca39ac494297b3b87c6171ff61a31c`; final source policy change is in `7048cefa430fbde3fbfca8f125ec58d94a540eb8`.
- Corrected contracts are deployed and bound on Studionet chain `61999`.
- Live covenant `dl-1` reached `BREACHED`; three wallets withdrew credits; final accounting balances.
- Frontend is deployed at `https://driftlock-nine.vercel.app`.

## Remaining verification boundary

The Codex in-app browser did not expose an injected EIP-1193 wallet. It verified the public index/detail read paths and browser console only. Wallet rejection, account/network switching, wallet-driven challenge actions, and responsive behavior still need manual testing in a browser with an injected wallet. The on-chain writes themselves were exercised with three distinct local CLI test wallets.

Do not repeat the irreversible live proof against `dl-1`; it has settled and all credits have been withdrawn. Use a fresh test covenant for any future live transaction sequence.
