# Live validation

## Studionet deployment

The semantic transition hardening was deployed to GenLayer Studionet `61999` from source commit `eb7a1860e215b86dee4cc3fe241fbb9ebb2c80a6` using the repository-local GenLayer CLI `0.39.1` and GenVM `v0.2.12`.

| Component | Address | Finalized deployment transaction |
| --- | --- | --- |
| DriftRegistry | `0xb5c8117DC80Dc9d84ECc95dFa139a4f06CD8d299` | [`0xe5f08d7a560b42782bcc6dae0b1c69ea7e7359d49593e18d49ba9c7bf90353fe`](https://explorer-studio.genlayer.com/tx/0xe5f08d7a560b42782bcc6dae0b1c69ea7e7359d49593e18d49ba9c7bf90353fe) |
| SourceInspector | `0x3DEB5a5B75d7ef6fc0DEd87bC4FB8Bc1E4E57326` | [`0xc5bd08ac5692bfadbe3f2e7c5c5ec6c227f3a0a5e3710cfabf6c1626f695d4e8`](https://explorer-studio.genlayer.com/tx/0xc5bd08ac5692bfadbe3f2e7c5c5ec6c227f3a0a5e3710cfabf6c1626f695d4e8) |
| BreachJudge | `0x4e2ab474ebcD75C768ba07b66062D3D187280A97` | [`0x46187b3dab8869ee3d9e255d06ca6cd490f04e42ac44751ee61146c7cc0c80c0`](https://explorer-studio.genlayer.com/tx/0x46187b3dab8869ee3d9e255d06ca6cd490f04e42ac44751ee61146c7cc0c80c0) |

The one-time component binding finalized in [`0x0010a466482c61a74fef61dd8cb9f8d8ee08239ae5bb67ac4e69783e60771388`](https://explorer-studio.genlayer.com/tx/0x0010a466482c61a74fef61dd8cb9f8d8ee08239ae5bb67ac4e69783e60771388). All four receipts reported `FINALIZED`, `MAJORITY_AGREE`, and successful leader execution. Live read-back of all three schemas confirmed the deployed methods, including `inspect_current(..., baseline_packet_json)`. Registry `get_stats` returned the configured Inspector and Judge addresses, `components_configured: true`, `chain_id: 61999`, zero covenants/challenges, zero stake/bond escrow, zero claimable/withdrawn value, and `accounting_balanced: true`.

The current deployment manifest is [`deployments/studionet.json`](../deployments/studionet.json). The frontend imports its Registry address from this manifest.

## Production app

The production app remains [`https://driftlock-nine.vercel.app`](https://driftlock-nine.vercel.app). After the main update, `/covenants`, `/create`, and `/activity` each returned HTTP 200, and their referenced JavaScript bundles contained the fresh Registry address `0xb5c8117DC80Dc9d84ECc95dFa139a4f06CD8d299`.

## Browser verification and live lifecycle evidence

The project owner previously reported manually verifying injected-wallet browser paths and transactions. Those manual checks are distinct from automated CI.

This repository does not include a new canonical full lifecycle transaction set for the fresh deployment. No complete Wallet A creation → clean baseline → Wallet B unchanged challenge → same-source breach update → independent BREACH settlement sequence is claimed here.

## Source evidence limits

Driftlock stores only a bounded semantic baseline result and its basis. It does not store fetched source text, a source digest, or an exact historical page snapshot. Current inspection evaluates the present source relative to the verified compliant semantic baseline. GenLayer validators re-fetch the same frozen canonical URL, and BreachJudge independently re-fetches it before economic settlement. This is not a historical byte-for-byte page comparison.
