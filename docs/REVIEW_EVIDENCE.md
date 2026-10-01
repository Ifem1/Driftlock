# Review evidence

## Audited behavior

- baseline source text is bounded, hashed, and passed as evidence into same-URL current inspection;
- byte-identical source content resolves deterministically to `NO_RELEVANT_CHANGE`;
- callback identities and inspection digests are bound to covenant and challenge state;
- only substantive outcomes consume the 24-challenge cap; cooldown still applies to all attempts;
- self-only pull withdrawals and explicit accounting conservation;
- frontend rechecks Studionet chain and selected account immediately before each write;
- covenant list pagination is bounded; detail view exposes stored baseline and current evidence;
- CI runs GenVM/Direct Mode contract validation and frontend checks.

## Release evidence

- Corrected contract release is deployed to Studionet; source commit and Git blob hashes are recorded in `deployments/studionet.json`.
- GitHub Actions quality run `36928565791` passed for source commit `7048cefa430fbde3fbfca8f125ec58d94a540eb8`.
- Live three-wallet proof includes an unchanged challenge, material source change, breach judgment, finalized withdrawals, and balanced final accounting. Transaction-level evidence is in `deployments/live-proof.json` and summarized in `docs/LIVE_VALIDATION.md`.
- Vercel production deployment `dpl_ECcrqpiusSWAvvT72YBnnoM68Dda` is READY at `https://driftlock-nine.vercel.app`. The index/detail read path was browser-checked without console errors. The in-app browser had no injected wallet, so browser transaction flows remain unverified.
