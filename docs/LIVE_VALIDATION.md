# Live validation

Status: **CONTRACT DEPLOYMENT, LIVE PROOF, AND PRODUCTION FRONTEND VERIFIED**

## Contract release

Network: GenLayer Studionet, chain `61999`. CLI `0.39.1`; GenVM `v0.2.12`. The deployed contract sources match commit `a092268bdeca39ac494297b3b87c6171ff61a31c`; exact Git blob IDs are recorded in `deployments/studionet.json`.

| Component | Address | Finalized transaction |
| --- | --- | --- |
| DriftRegistry | `0xC9c0E633f8c7c5d516376dCd3bFd8B4dE52Fe02C` | `0x959450ea93b9c7a707eee2c5f51e52b202f38332396e26d7f2d2ba1a0b725dab` |
| SourceInspector | `0x61BFdBDd25130B7C718964D9538cBCE92Dcc6057` | `0xe3a097dba29de5717b8e95dfb0ea1f8284e49d47749b66b3507b67e7bb71ffdf` |
| BreachJudge | `0x2a7f6617b3c018327aA3344A85A91455550E757C` | `0xcfab190339a4a134093ebdf897b427d424bbeb1ebbb162dd162abf38906a2133` |
| One-time component binding | — | `0x23b39318a4320d756c1ebcf881d9cb69d50f988fe2b99359bba5789b88f2db33` |

All four receipts returned `FINALIZED`. Registry reads confirmed configured component addresses and balanced accounting.

## Three-wallet covenant proof

Full chain readbacks and results are in [`deployments/live-proof.json`](../deployments/live-proof.json). Public addresses only are recorded there; private keys are not included.

- Covenant `dl-1` was created in `0xc9deb0042c63e7a5dec4dc7b6b650fdc90d81ef46e52fd843e5cf6ac7266c305`. Baseline verification finalized as `BASELINE_VERIFIED`, with SHA-256 `cb713d95689489779a48b35cd0dce6117a0316821948ce055639fd96c0a98f25`.
- Challenge `dc-1` (`0xef8dc1cb7b364b8a448581d22987fc37d9bd2abb66d9300f390968542dcea88e`) fetched identical bytes from the canonical URL and finalized as `NO_RELEVANT_CHANGE`.
- The same raw GitHub URL changed from commit `a092268bdeca39ac494297b3b87c6171ff61a31c` / blob `73946f78a813567ad0046e3faa1f70671e1c6426` to commit `7048cefa430fbde3fbfca8f125ec58d94a540eb8` / blob `ac0f56792333be4ca41e2a93641424079602bde0`.
- Challenge `dc-2` (`0x13b0189e39dbf85be3cb20523f2ebdd811f7645acbdb2452e713d8d96d7047d2`) finalized as `MATERIAL_CHANGE`; independent judgment finalized as `BREACH`; the covenant settled as `BREACHED`.
- Finalized withdrawals: owner `0x37e1380573cb72450e953da4d1f9c5bb1e639dd28baf5f80690e8c270f7a7836`, challenger/finder `0x15933479adb560d9ca104e230f301e78da063da4057964a54d761d52d69248dd`, beneficiary `0x6d1290756e9a5cdf56826071c72c47f64126357cbe02bcb29ed2bfc12e48bb44`.
- Final stats: `accounting_balanced=true`; claimable, stake escrow, and bond escrow are zero; deposited and withdrawn both equal `10200000000000000` attoGEN.

## Production frontend

Vercel deployment `dpl_ECcrqpiusSWAvvT72YBnnoM68Dda` reached `READY` at [https://driftlock-nine.vercel.app](https://driftlock-nine.vercel.app). The covenant index and detail were manually opened. The detail showed the on-chain verified baseline and current inspection. Browser console had no errors or warnings. The in-app browser had no injected wallet, so browser transaction flows and responsive wallet interactions were not exercised; contract execution was checked independently with three distinct local test wallets.

## CI and local verification

GitHub Actions quality run `36928565791` passed for commit `7048cefa430fbde3fbfca8f125ec58d94a540eb8`: [workflow run](https://github.com/Ifem1/Driftlock/actions/runs/36928565791). Local evidence and exact test commands are in [`LOCAL_VALIDATION.md`](LOCAL_VALIDATION.md).
