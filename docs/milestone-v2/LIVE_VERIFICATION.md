# V2 verification record

Updated 2026-10-23. Active contract source revision: `f9793cc67ad11ebcf89b420c624e9e8ad537dced` on `milestone/driftlock-v2-assurance-appeals`. The work is local; nothing was pushed to GitHub.

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

A separate live test used the final V2 Registry's retained `create_covenant` single-source compatibility path. It did not claim a V2 multi-source breach or breach-appeal result. The test source is Driftlock-owned at [`https://driftlock-nine.vercel.app/driftlock-test-covenant.txt`](https://driftlock-nine.vercel.app/driftlock-test-covenant.txt); it is explicitly a controlled fixture, not the official MIT publisher. Baseline text stated the MIT grant and notice conditions. Its deployed baseline SHA-256 was `3e1945888f5570241f81cb8fb6f0e92980b1bdef21f0ff8aab53e9a67bdd9a94` (560 bytes). The live test then changed that same URL to add a current fee and prior-approval requirement before publish, distribution, sublicensing or sale. The changed text SHA-256 was `7d2ecdf07b4a226c7c7597bf6ca26562922bc30fa948f48ecc49c33ad0241189` (900 bytes); Vercel served the changed text successfully before the challenge. The production source has since been restored to the 560-byte baseline.

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

The V2 multi-source tests on this Registry (`dl-2` and `dl-3`) returned `AMBIGUOUS` because the corroborator contradicted the primary's policy result. Their 0.0001 GEN challenge bonds were refunded and withdrawn; neither test paid a breach reward. The payout above therefore demonstrates a real changed-source breach and stake settlement through the compatibility method on the final V2 Registry, while the V2 multi-source breach and breach-appeal path remains unverified. After the withdrawals, claimable credit, bond escrow and appeal escrow were zero, `accounting_balanced=true`, and stake escrow was 0.003 GEN for the three unexpired active covenants.

## Superseded test deployments

Several earlier live attempts diagnosed and fixed production issues. On the first V2 Registry, the baseline model emitted an invalid status; timeout recovery/retry ended without a verified baseline. On the next deployment, the policy model returned a classification shape the Inspector did not accept; its timeout recovery returned the covenant to `BASELINE_RETRYABLE`. On the policy-shape deployment, baseline and unchanged inspection succeeded, but a non-payable appeal ABI rejected the required appeal value. The payable fix is live in the final deployment above.

The first two superseded covenants each retain `0.001 GEN` in stake escrow and are `BASELINE_RETRYABLE`; their covenant expiries are 2026-10-26 15:42:27 UTC and 2026-10-26 16:30:36 UTC. On policy-shape Registry `0x6193d49a295B3670949Bc5866BCcaAbe48848957`, `dl-1` retained `0.001 GEN` stake and had a `0.0001 GEN` challenge bond. Its challenge window was permissionlessly finalized as `NO_RELEVANT_CHANGE` / `NOT_APPEALED` in [`0xabc24ea929744c9378a418a0586026b44399f3343d5a5294029074255e38ac18`](https://explorer-studio.genlayer.com/tx/0xabc24ea929744c9378a418a0586026b44399f3343d5a5294029074255e38ac18); the owner withdrew the returned bond in [`0x17bf3d235fe002e2c0d467bf285d9dcbee80ee1d4c8103a1066f0fc9ebfae7a6`](https://explorer-studio.genlayer.com/tx/0x17bf3d235fe002e2c0d467bf285d9dcbee80ee1d4c8103a1066f0fc9ebfae7a6). Its remaining 0.001 GEN stake expires 2026-10-26 16:44:12 UTC. The recorded timeout-recovery transactions for the first two remain [`0xe9bb9851a7afc5f45239200a99d22ed774f9c42d58b92a1bf9288974b9e8dab6`](https://explorer-studio.genlayer.com/tx/0xe9bb9851a7afc5f45239200a99d22ed774f9c42d58b92a1bf9288974b9e8dab6) and [`0x7f8db29959383f6b5dd9ccff6bfa154d3bf8808c4cc69cecb5857df0c4d48aaa`](https://explorer-studio.genlayer.com/tx/0x7f8db29959383f6b5dd9ccff6bfa154d3bf8808c4cc69cecb5857df0c4d48aaa); both show accepted majority results and retryable readback. All three retained stakes are to be recovered via their immutable Registry expiry process after the recorded dates.

The final Registry also has three unexpired active test stakes: `dl-1` 0.001 GEN expires 2026-10-26 16:55:18 UTC; ambiguous V2 test `dl-2` 0.001 GEN expires 2026-10-24 05:58:17 UTC; ambiguous V2 test `dl-3` 0.001 GEN expires 2026-10-24 06:06:58 UTC. An active recovery check is scheduled at 07:15 and 18:15 Lagos time each day. It recovers matured groups, withdraws their credits and keeps later-expiring covenants untouched; after all targets mature, it verifies final accounting, updates this record with receipts and deactivates itself. This is a scheduled follow-up, not a completed recovery.

Live coverage includes the controlled compatibility-path source change, breach judgment, settlement and payout above. It does not include an upheld V2 multi-source breach appeal. User-declared publisher names also do not prove ownership or editorial independence.

## Production frontend

The final production deployment after restoring the test fixture baseline is [`dpl_ABEmiqSHoXgfWvTyPD6nuHaPw722`](https://vercel.com/ifem1s-projects/driftlock/dpl_ABEmiqSHoXgfWvTyPD6nuHaPw722), aliased to [`https://driftlock-nine.vercel.app`](https://driftlock-nine.vercel.app). The controlled source was changed during the live breach test and restored afterward. Route and deployment status should be rechecked at closeout; prior HTTP checks returned **200** for `/`, `/create`, `/covenants`, `/activity`, `/protocol`, and `/demo`.

Work settings disabled local browser use and the Chrome browser inventory was empty. No Chrome or Brave UI was used. Injected-wallet connection, network switching, signing, rejection and interactive transaction UI paths remain unverified. These HTTP/bundle checks are not browser tests. No hosted GitHub Actions run is claimed.

