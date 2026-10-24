# V2 verification record

Updated 2026-10-24. Active contract source revision recorded at deployment: `f9793cc67ad11ebcf89b420c624e9e8ad537dced`. This local revision is not resolvable on GitHub. Byte-identical contract source is present in public snapshot commit `8e947566aab947aee951f0a91122902a670fa733`, on milestone head `048c86ed6ec516d1711b06f19c3f3d9b8f023a4a`; V2 was merged to `main` at `d83575698c1c3fa78c73c9b5adc1b3094d14b25a` by [PR #4](https://github.com/Ifem1/Driftlock/pull/4). The V1→V2 comparison contains 47 files from baseline `4987c25a726e2ff8db0fb5bf8f76daa750c970bb`.

## Current Studionet deployment

Target: GenLayer Studionet, chain `61999`, RPC `https://studio.genlayer.com/api`. The final corrected contract set was deployed and bound with CLI `0.39.1` and GenVM `v0.2.12`. Every deployment and binding transaction reached `FINALIZED`, `MAJORITY_AGREE`, and successful leader execution. Registry readback confirms V2, chain 61999, the component addresses below, one-time configuration, and balanced accounting.

| Component/action | Address | Transaction | Source SHA-256 |
|---|---|---|---|
| Registry | `0xf8ccE1A56C69129ff32d822af5BAa0b3081CF6F4` | [`0x7ba6afbfc8d53666881131369243644498bc723550ace5ae4b8ecd20923ae80c`](https://explorer-studio.genlayer.com/tx/0x7ba6afbfc8d53666881131369243644498bc723550ace5ae4b8ecd20923ae80c) | `23ba7c224c974451db47e999be93cf16eed6ebe73dd1a3ca1f0b2eef9aab47d7` |
| Inspector | `0x2d14C4eF96D3B61e22F34abA232628380fa00c51` | [`0x717531b2be54fe5ab7a7b202057cb264291482c927cacc538e25e4221f80a30b`](https://explorer-studio.genlayer.com/tx/0x717531b2be54fe5ab7a7b202057cb264291482c927cacc538e25e4221f80a30b) | `1e507a1483536cf4e996bfb1d6040035ecf1514dad0f73ce14d8fc14f064ddd7` |
| Judge | `0x9144eb009DAc03e3C653bC1E5b50793B66A2Ef89` | [`0xe47513b3e5fd43382684690fb59c6c5b2a37837132429aeddb769c9ce00e81d7`](https://explorer-studio.genlayer.com/tx/0xe47513b3e5fd43382684690fb59c6c5b2a37837132429aeddb769c9ce00e81d7) | `e1a63d5d2e49a4cc80c740776178f18522a9a64b6d8a1daaf039d9663bfa9d77` |
| Registry component binding | — | [`0x3e6eaf6e792af4415b5f7faa38c65c874b5dd6fcd124849bb64e71860a6efb36`](https://explorer-studio.genlayer.com/tx/0x3e6eaf6e792af4415b5f7faa38c65c874b5dd6fcd124849bb64e71860a6efb36) | — |

`deployments/studionet.json` and `deployments/studionet-v2.json` select this set. Earlier immutable V2 sets and their manifests are preserved as `studionet-v2-initial.json`, `studionet-v2-enum-prompt.json`, and `studionet-v2-policy-shape.json`. V1 remains at `deployments/studionet-v1.json`.

The final Inspector prompt gives an exact example of the required policy response shape and status enums. A single corroborator returned as a valid scalar classification is normalized to the one-element array and then validated normally. The final Registry declares `appeal_challenge` payable, matching its exact-bond escrow behavior.

## Local verification

`powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1` passed after the final source revision and manifest update:

- Direct Mode contract tests: **69 passed**.
- Frontend Vitest: **21 passed**.
- TypeScript typecheck, ESLint, and Next.js production build: **passed**.
- Python compile, Studionet/source digest preflight, and secret scan: **passed** (77 repository files scanned).
- GenVM `v0.2.12` lint and ABI: Registry 24 methods, Inspector 6, Judge 4; all passed.
- Offline dependency audits: zero known vulnerabilities. Separate fresh online `npm audit` runs for root and frontend also reported **0 vulnerabilities**.

## Final deployment live lifecycle

On the final Registry, wallet `0x5516488131150CCBe76341E5ABD472013ECaa666` created a test covenant for the MIT license with the official SPDX page as primary, Choose a License as corroborator, `min_corroborations=1`, and `0.001 GEN` stake. The primary and corroborator rendered artifacts were 2,298 and 2,529 bytes, with SHA-256 digests `f3f1e84918bca501db1e2663ade1d4ca0d08ea918da89013a62da9d926768a64` and `65eefe4f3bce34eb0ff0bd27dcf26a347388c6392e5fba772ddc318017951b81`. The frozen policy digest is `f557830acaa8ad2b9c7c7398c4e80f2107e13b83b8688dace31c466616c6442e`.

| Stage | Transaction | Final observed result |
|---|---|---|
| `create_covenant_v2` (`dl-1`) | [`0xcb6473277ff505ad52c3df5037cc18d42d7bd89cddb160f740f40e8592986924`](https://explorer-studio.genlayer.com/tx/0xcb6473277ff505ad52c3df5037cc18d42d7bd89cddb160f740f40e8592986924) | `FINALIZED`, majority agree; 0.001 GEN committed. |
| Inspector baseline callback | [`0x36dcb1d9d2cacd903615de36cc6fdf7d9bc44aa47bc7d4e71ca2e5d799135d01`](https://explorer-studio.genlayer.com/tx/0x36dcb1d9d2cacd903615de36cc6fdf7d9bc44aa47bc7d4e71ca2e5d799135d01) | `FINALIZED`, majority agree. Primary and corroborator available; corroboration `SUPPORTS`; `BASELINE_VERIFIED`, baseline compliant. |
| Registry baseline callback | [`0xd92d2bfa9e09e3348b58c5e82ed91cc28ea44cd0068fdfdd2d6873c7b9f72cac`](https://explorer-studio.genlayer.com/tx/0xd92d2bfa9e09e3348b58c5e82ed91cc28ea44cd0068fdfdd2d6873c7b9f72cac) | `FINALIZED`; Registry state `ACTIVE`. |
| Independent wallet unchanged-source challenge (`dc-1`) | [`0xc6585a4e1a2e8e3a5bcb388f99348e567efae6cf85efcd4a465ca0372197becd`](https://explorer-studio.genlayer.com/tx/0xc6585a4e1a2e8e3a5bcb388f99348e567efae6cf85efcd4a465ca0372197becd) | `FINALIZED`; challenger `0x4dcD388DaaCC30A6A427b92c6001cd31a2Eb2576` bonded `0.0001 GEN`. |
| Inspector current-source callback | [`0x7c673530da8fb2104bf12d8e1f670348dd08eb1f5aac082653febe84099cd091`](https://explorer-studio.genlayer.com/tx/0x7c673530da8fb2104bf12d8e1f670348dd08eb1f5aac082653febe84099cd091) | `FINALIZED`; status `NO_RELEVANT_CHANGE`, source remains compliant, one corroborator supports. |
| Registry inspection callback | [`0xf7208fd0cf67bc0b6e803e53316fbcb150310ccc1814c22dd7df7e24aa022aa8`](https://explorer-studio.genlayer.com/tx/0xf7208fd0cf67bc0b6e803e53316fbcb150310ccc1814c22dd7df7e24aa022aa8) | `FINALIZED`; challenge became `PROVISIONAL_NO_RELEVANT_CHANGE`. |
| Challenger bonded appeal | [`0x22878cc94aaa46dc17739d95b6dcc54a1c6d7ce59d6e6e22c1dfed614a4f0109`](https://explorer-studio.genlayer.com/tx/0x22878cc94aaa46dc17739d95b6dcc54a1c6d7ce59d6e6e22c1dfed614a4f0109) | `FINALIZED`, leader execution successful; payable appeal bond `0.0001 GEN` escrowed and Judge callback emitted. |
| Judge appeal callback | [`0x888244310ac0da9fd896a4da6de4e7b86e08f01da131e3281ea352fe8eacd7c0`](https://explorer-studio.genlayer.com/tx/0x888244310ac0da9fd896a4da6de4e7b86e08f01da131e3281ea352fe8eacd7c0) | `FINALIZED`; independent committed-evidence judgment `PERMITTED_CHANGE`. |
| Registry appeal settlement | [`0x9c72e334a8a382093de29c995278bd925763dea36f330cf9e940abe8ec7e81ad`](https://explorer-studio.genlayer.com/tx/0x9c72e334a8a382093de29c995278bd925763dea36f330cf9e940abe8ec7e81ad) | `FINALIZED`; appeal `UPHELD`, challenge `PERMITTED_CHANGE`; both bonds returned to owner credit, with no breach or stake payout. |
| Owner pull-credit withdrawal | [`0xd79731f6fb8392a855f915e2a733c80026465ad3b2386f8eddc6dff7479bf8a8`](https://explorer-studio.genlayer.com/tx/0xd79731f6fb8392a855f915e2a733c80026465ad3b2386f8eddc6dff7479bf8a8) | `FINALIZED`; owner withdrew `0.0002 GEN`. |

After withdrawal, Registry reports `accounting_balanced=true`, stake escrow `0.001 GEN`, bond and appeal escrow zero, claimable zero, withdrawn `0.0002 GEN`. Covenant `dl-1` remains `ACTIVE` until its scheduled expiry; no breach was alleged or manufactured. This live run exercises creation, multi-source baseline, corroborated unchanged inspection, a bonded appeal, final settlement and withdrawal.

## Controlled source change, breach judgment and payout

A separate earlier live test used the final V2 Registry's retained `create_covenant` single-source compatibility path (`dl-4`). That historical run established a changed-source breach and payout through the compatibility API. Its fixture is Driftlock-owned, not the official MIT publisher. The later `dl-5`/`dc-5` section records the completed V2 multi-source breach and upheld appeal. The earlier test's source hashes and receipts below remain as historical evidence; they are not the source hashes for `dl-5`.

| Stage | Transaction | Final observed result |
|---|---|---|
| `create_covenant` compatibility-path creation (`dl-4`) | [`0x042ba78cec0590421ce155779c47fdd7f608fb090c03ad5e0f8d9541fc1032b8`](https://explorer-studio.genlayer.com/tx/0x042ba78cec0590421ce155779c47fdd7f608fb090c03ad5e0f8d9541fc1032b8) | `FINALIZED`, majority agree; 0.001 GEN committed, owner and beneficiary `0x5516488131150CCBe76341E5ABD472013ECaa666`; 2,500 bps finder reward. |
| Inspector baseline callback | [`0xe7cc57cd04564679b34ea6f0195a1e1223e17263ea46b20e33ed76941882c763`](https://explorer-studio.genlayer.com/tx/0xe7cc57cd04564679b34ea6f0195a1e1223e17263ea46b20e33ed76941882c763) | `FINALIZED`; baseline verified. |
| Registry baseline callback | [`0x2af47784fa5390accf83fe4de3c73e18562994c1108ea5c9e7dd872938ad2690`](https://explorer-studio.genlayer.com/tx/0x2af47784fa5390accf83fe4de3c73e18562994c1108ea5c9e7dd872938ad2690) | `FINALIZED`; covenant active at baseline. |
| Independent challenger bond and challenge (`dc-4`) | [`0xd3722d80941ebda8a32cf7f45400198044f679f07c2d15893d7c3d1c13350d58`](https://explorer-studio.genlayer.com/tx/0xd3722d80941ebda8a32cf7f45400198044f679f07c2d15893d7c3d1c13350d58) | `FINALIZED`; challenger `0x4dcd388DaaCC30A6A427b92c6001cd31a2Eb2576` bonded `0.0001 GEN`. |
| Inspector changed-source callback | [`0x9759a08543beec8f7fc1c5dc6801964af91f0847bfe3d538b9598848609427af`](https://explorer-studio.genlayer.com/tx/0x9759a08543beec8f7fc1c5dc6801964af91f0847bfe3d538b9598848609427af) | `FINALIZED`; `MATERIAL_CHANGE`, same subject, current compliance false, breach condition supported and effective. |
| Registry inspection callback | [`0x0604d3a49f143013e4783dd800e4bf819ec7dbbf354d9fdbaf4ad9124234f9a1`](https://explorer-studio.genlayer.com/tx/0x0604d3a49f143013e4783dd800e4bf819ec7dbbf354d9fdbaf4ad9124234f9a1) | `FINALIZED`; breach judgment requested. |
| Independent Judge callback | [`0x3983e334cdb8083e971ca0ebaa1dd44ccac99800ad25d0ab41346899395099ac`](https://explorer-studio.genlayer.com/tx/0x3983e334cdb8083e971ca0ebaa1dd44ccac99800ad25d0ab41346899395099ac) | `FINALIZED`; outcome `BREACH`. |
| Registry breach settlement | [`0x256c7746914a543f213c340db257784301e7f46a6e8042257286ebeebdf287dc`](https://explorer-studio.genlayer.com/tx/0x256c7746914a543f213c340db257784301e7f46a6e8042257286ebeebdf287dc) | `FINALIZED`; covenant `BREACHED`; 0.00025 GEN finder reward credited to challenger and 0.00075 GEN stake remainder to beneficiary; 0.0001 GEN challenge bond returned to challenger. |
| Owner credit withdrawal | [`0xe5b01f9463b928833120624f52729cf82d3b7983de5ffe91ac0d9c4d549c60cd`](https://explorer-studio.genlayer.com/tx/0xe5b01f9463b928833120624f52729cf82d3b7983de5ffe91ac0d9c4d549c60cd) | `FINALIZED`; owner withdrew 0.00075 GEN. |
| Challenger credit withdrawal | [`0xcd981f3bc53b76156f5db8d0e7f94c61605181d16f89885e8b4fbace6e9eda25`](https://explorer-studio.genlayer.com/tx/0xcd981f3bc53b76156f5db8d0e7f94c61605181d16f89885e8b4fbace6e9eda25) | `FINALIZED`; challenger withdrew 0.00055 GEN, including the 0.00025 finder reward, 0.0001 bond return and 0.0002 in prior ambiguous-attempt bond refunds. |

The earlier V2 multi-source tests on this Registry (`dl-2` and `dl-3`) returned `AMBIGUOUS` because the corroborator contradicted the primary's policy result. Neither paid a breach reward. The later `dl-5`/`dc-5` run below separately demonstrates a V2 multi-source breach and upheld appeal. The current read-only escrow status is recorded below; no recovery transaction is claimed by this closeout.

## Superseded test deployments

Several earlier live attempts diagnosed and fixed production issues. On the first V2 Registry, the baseline model emitted an invalid status; timeout recovery/retry ended without a verified baseline. On the next deployment, the policy model returned a classification shape the Inspector did not accept; its timeout recovery returned the covenant to `BASELINE_RETRYABLE`. On the policy-shape deployment, baseline and unchanged inspection succeeded, but a non-payable appeal ABI rejected the required appeal value. The payable fix is live in the final deployment above.

The first two superseded covenants remain `BASELINE_RETRYABLE` with `0.001 GEN` each; their expiries are 2026-10-26 15:42:27 UTC and 2026-10-26 16:30:36 UTC. On policy-shape Registry `0x6193d49a295B3670949Bc5866BCcaAbe48848957`, `dl-1` remains `ACTIVE` with `0.001 GEN` stake until 2026-10-26 16:44:12 UTC. Its challenge window had already finalized as `NO_RELEVANT_CHANGE` / `NOT_APPEALED` in [`0xabc24ea929744c9378a418a0586026b44399f3343d5a5294029074255e38ac18`](https://explorer-studio.genlayer.com/tx/0xabc24ea929744c9378a418a0586026b44399f3343d5a5294029074255e38ac18), and the returned bond was withdrawn in [`0x17bf3d235fe002e2c0d467bf285d9dcbee80ee1d4c8103a1066f0fc9ebfae7a6`](https://explorer-studio.genlayer.com/tx/0x17bf3d235fe002e2c0d467bf285d9dcbee80ee1d4c8103a1066f0fc9ebfae7a6). Prior timeout-recovery attempts for the first two are recorded at [`0xe9bb9851a7afc5f45239200a99d22ed774f9c42d58b92a1bf9288974b9e8dab6`](https://explorer-studio.genlayer.com/tx/0xe9bb9851a7afc5f45239200a99d22ed774f9c42d58b92a1bf9288974b9e8dab6) and [`0x7f8db29959383f6b5dd9ccff6bfa154d3bf8808c4cc69cecb5857df0c4d48aaa`](https://explorer-studio.genlayer.com/tx/0x7f8db29959383f6b5dd9ccff6bfa154d3bf8808c4cc69cecb5857df0c4d48aaa); both ended retryable.

### Read-only escrow check — 2026-10-24 10:06 Lagos time

No expiry or withdrawal transaction was sent. On the current Registry, `dl-2` and `dl-3` each still hold `0.001 GEN`; both are past expiry and report `can_expire=true`. Current `dl-1` still holds `0.001 GEN` until 2026-10-26 16:55:18 UTC. Its `dc-6` challenge is `PROVISIONAL_NO_RELEVANT_CHANGE`; its `0.0001 GEN` bond remains escrowed. Across current V2 accounting, stake escrow is `0.003 GEN`, bond escrow `0.0001 GEN`, claimable and appeal escrow are zero, and `accounting_balanced=true`. The two superseded retryable stakes and the policy-shape `dl-1` are also still locked until their Oct 26 expiries. The scheduled recovery heartbeat was stopped at the user's request; these funds remain available for later permissionless expiry and withdrawal if separately authorized.

Live coverage includes both the earlier compatibility-path breach and payout, and the later V2 multi-source `dl-5`/`dc-5` breach, bonded appeal, upheld judgment, settlement and withdrawal. User-declared publisher names do not prove ownership or editorial independence.

## Production frontend

The final production deployment after restoring the test fixture baseline is [`dpl_ABEmiqSHoXgfWvTyPD6nuHaPw722`](https://vercel.com/ifem1s-projects/driftlock/dpl_ABEmiqSHoXgfWvTyPD6nuHaPw722), aliased to [`https://driftlock-nine.vercel.app`](https://driftlock-nine.vercel.app). The controlled source was changed during the live breach test and restored afterward. Route and deployment status should be rechecked at closeout; prior HTTP checks returned **200** for `/`, `/create`, `/covenants`, `/activity`, `/protocol`, and `/demo`.

Chrome interactive QA was completed for the live run below. Account switching, refresh recovery and wrong-network handling passed. Explicit rejection of a transaction was not completed. GitHub Actions runs [40013174145](https://github.com/Ifem1/Driftlock/actions/runs/40013174145), [40015269612](https://github.com/Ifem1/Driftlock/actions/runs/40015269612), and [40015703424](https://github.com/Ifem1/Driftlock/actions/runs/40015703424) passed on the release head, PR head, and merged main respectively; no Actions run is claimed for the later documentation-only closeout commits.

## Local closeout refresh — 2026-10-23

The local verification gate was rerun on repository HEAD `110f966f66e23a4b94e0cb942d42eb75c77f0e97` (`docs: reconcile V2 release evidence`). It passed Python compilation, deployment/source preflight, secret scan (78 files), GenVM lint and ABI validation (Registry 24 methods, Inspector 6, Judge 4), Direct Mode (**69 passed**), frontend tests (**21 passed**), TypeScript typecheck, ESLint, frontend offline dependency audit (**0 vulnerabilities**) and Next.js production build. The build warned that both root and frontend lockfiles exist; compilation and build completed successfully. This is local evidence for this SHA; it is not a GitHub Actions result. Later closeout commits are present on the remote milestone branch; GitHub Actions evidence remains the earlier release and main runs listed above.

An additional source review of the V2 path found the implemented guardrails consistent with the documented model: the policy digest freezes the ordered source list; the first URL must be the canonical primary; the Inspector evaluates the primary as authority and only counts corroborators toward the threshold; a contradiction prevents a definitive outcome; rendered artifacts are bounded and rehashed; the Judge checks the same incident evidence digest for initial judgment and appeal; Registry callbacks are restricted to the configured components and stage/request IDs; and payouts occur only from finalized judgment/appeal or expiry transitions. Direct Mode regressions cover forged artifact commitments, duplicate appeals, timeout/replay behavior, source identity constraints and settlement. This review did not establish cryptographic source ownership: distinct DNS sites and publisher strings are policy declarations, and the two controlled test endpoints are operated by the same Driftlock project. No publisher independence claim should be made from this test.

## Completed V2 multi-source breach-and-appeal run

The completed `dl-5`/`dc-5` live run used the Vercel primary and Driftlock-controlled Linktree page. It reached finalized baseline, source-change inspection, bonded appeal, upheld breach judgment over the same committed evidence digest, settlement and credit withdrawal. The GitHub raw mirror was not used, and this run does not establish independent publisher ownership. Full receipts and remaining evidence limits follow.

## Chrome wallet multi-source run: dl-5 / dc-5 (2026-10-23)

Observed in Chrome with owner 0xD6423aE82a975d55C6CeaC222827A727325e0459, then account-change event to challenger 0x7d1170bc98624f98183972FabD69418Bb7D5d541. UI displayed Studionet 61999. User signed transactions. Covenant `dl-5` and challenge `dc-5` completed the V2 multi-source breach-and-appeal lifecycle using Vercel plus Linktree; they did not use the GitHub raw mirror.

Create transaction: 0x9dd5476da30268031fd9d060fa1fdc47757ee76008c88b64805872676daff02a. Explorer showed create_covenant_v2, correct active-manifest Registry 0xf8ccE1A56C69129ff32d822af5BAa0b3081CF6F4, 0.001 GEN, return dl-5. Finalized Registry UI readback after refresh showed ACTIVE and BASELINE VERIFIED. Finder reward 2500 bps; expiry 2026-10-30 22:11:30 UTC; beneficiary is challenger.

Frozen policy digest: 4688499d88b2eed975ce75ab175d25348ab41cd9fa1d33b3fd25e90af94cf732. Sources: Vercel PRIMARY (declared Driftlock project); https://linktr.ee/Marymmm CORROBORATING (declared Driftlock Linktree test fixture); threshold 1. Both are user/project controlled, not evidence of independent ownership. The GitHub mirror was not used in this covenant.

Challenge transaction: 0x766b3da7ed08e57e423235b732ba6e75b19527b11e40dcd54f695318e6de6664. UI reported finalized challenge dc-5. Inspector MATERIAL_CHANGE; both artifacts AVAILABLE. Primary rendered SHA-256 d27867bf597a3338aac8eccfe7911c72f55a1c4c3e7322a9e27ee2e11a62fd31 (304 bytes); Linktree rendered SHA-256 c4cb4746f56f37ca9003c3c47479eb5dd0902d4ac89944c30417b7d6e5f8f837 (1741 bytes). Both committed texts state a fee and prior approval requirement effective now. These are GenLayer rendered-text hashes, not raw HTTP hashes.

Judge first returned `PROVISIONAL_BREACH`: current fee and approval requirements contradicted the protected promise and satisfied the breach rule. The owner then appealed before the recorded deadline; the appeal was upheld after the Judge reassessed the same committed evidence digest. Finalized settlement and withdrawal details follow.

Form preparation issue: subject retained earlier wording requiring prior approval before a charge, while protected promise permits demo software activity without current fee or prior approval. This inconsistency must remain in evidence; it was not edited after creation. Proposed owner appeal asks Judge to reassess this actual inconsistency using the same committed incident evidence.

Controlled Vercel mutation deployment: dpl_3kzTVVgmypnfFDo2bEhpXcievaa4, aliased driftlock-nine.vercel.app, READY. Sources were restored in deployment dpl_Ax6nHtcRvhQ5uPGpUBiW5Y2QHc4C. Wrong-chain handling passed; explicit transaction rejection remains unverified.

### Finalized appeal, settlement and withdrawal readback

Appeal transaction 0xf3ec3b1cd8eda173a33f36efe4c83a28e495e1fda6ea032bccf0fd12985d2dff reached FINALIZED / SUCCESS with 0.0001 GEN from the owner. Triggered Judge transaction 0xa25e22fe1a0ffd334aa6b624673b71764e2842c5b50a4e0f8815009f3dd86476 reached FINALIZED / SUCCESS. The outcome was BREACH, appeal result UPHELD. The Judge explicitly addressed the subject inconsistency and found it did not negate the current fee requirement. Both initial judgment and appeal judgment carry evidence digest cdc2cc142b9a7cfc850f7bac0504862a2fc8e86a8d289af9851e14aedec33251. Both report corroboration SUPPORTS and no permission under the rule.

Finalized Registry readback saved in `.qa-live/final-readback.json` confirms `dl-5` BREACHED, `dc-5` BREACH, UPHELD; bond and appeal bond released to challenger. Finder reward is 0.00025 GEN; the beneficiary is also the challenger, so the stake portion totals 0.001 GEN to that address. Returned challenge bond plus forfeited appeal bond add 0.0002 GEN. Chrome showed 0.0012 GEN available credit; the user signed withdrawal; after finality Chrome and LATEST_FINAL RPC both show credit zero. Global `accounting_balanced=true`, claimable=0, bond escrow=0, appeal escrow=0, withdrawn=0.0027 GEN, stake escrow=0.003 GEN. The remaining global stake belongs to other unexpired covenants and is not claimed recovered. Withdrawal transaction [`0xf605b55bc849cc6008b6787b76c8f6d4ec1cd20e527e72dfb2b9149af366d8a5`](https://explorer-studio.genlayer.com/tx/0xf605b55bc849cc6008b6787b76c8f6d4ec1cd20e527e72dfb2b9149af366d8a5) is the finalized `withdraw_credit` transaction shown on the Registry history. Settlement and credit recovery are verified by finalized Registry readback.

Restoration deployment dpl_Ax6nHtcRvhQ5uPGpUBiW5Y2QHc4C is READY and aliased to driftlock-nine.vercel.app. The live primary was restored to the pre-test no-fee/no-prior-approval policy, rather than the older local MIT fixture. Linktree was visibly restored to the same baseline policy; its final bio omits the original final period, so exact byte restoration is not claimed. Both HTTP endpoints return 200. Post-restoration raw HTTP-body hashes (not GenLayer rendered-text hashes): primary 3a404a6d4b23187efe6f0d5284388c7aa0ee91e97951d81ff3e9dcc9908ed6eb (402 bytes); Linktree c2fb175eee36e5fe214aaafd6d87757e07047ca5fb12b24881ef25ff55cb2092 (160116 bytes, dynamic HTML). Saved in .qa-live/restored-source-hashes.json. Linktree dynamic HTML hashes should not be compared with committed rendered artifacts.

This establishes the controlled V2 multi-source baseline, source mutation, material-change inspection, provisional breach, bonded appeal reassessment against the same committed incident evidence, upheld breach, settlement, credit withdrawal and restored sources. It does not establish publisher independence. Chrome account changes, refresh recovery and wrong-chain handling were observed; explicit rejected-transaction behavior remains unverified. Hosted CI on the finalized release-closeout commit is recorded below after the GitHub PR workflow completes.

