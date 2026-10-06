# Live validation

## Studionet deployment

The updated contracts were deployed to GenLayer Studionet on 2026-10-06 from source commit `e7642875db65b8e94410c18d12c819493122a022` using GenLayer CLI `0.39.1`.

| Component | Address | Finalized deployment transaction |
| --- | --- | --- |
| DriftRegistry | `0x2f51Bbf5c41BA4E734f460A4DeE22B6227C8820D` | `0xc8732bb26bb0e250ece2d489c63719124b66c52016c8b11c7def001de9e42e90` |
| SourceInspector | `0xfBeB8719Fe4F351480bc250B495201D09cE753eD` | `0x55a7f85d6069bde832727389693eaf1e672612bbf06961dd60313e66d4723464` |
| BreachJudge | `0x311b57C0888f388a0241F4D42EFc8Da65Ca33136` | `0x491e9bfb4d30929e89c9065d03372161605152fa1e04e8933c9dbe1cedaedd3c` |

One-time component binding finalized in `0x6cd587b1e3397add31afac309cf0d3f0a8603d2e1658956e64ba38ddca413ea8`. All four receipts report `FINALIZED` with successful leader execution. The new Registry read-back returns the configured Inspector and Judge addresses, chain ID `61999`, `accounting_balanced: true`, and zero initial covenants and balances. The previous Registry also had zero covenants and zero escrow when the app was switched to the new deployment.

The deployment manifest is [`deployments/studionet.json`](../deployments/studionet.json). The production frontend update follows the merged repository configuration.

## Browser verification and evidence scope

The project owner reports manually verifying injected-wallet browser paths, including wallet interaction and transactions. These manual checks are separate from automated CI. This repository does not include a canonical complete demo-covenant lifecycle transaction record, so this document makes no claim that it does.

GenLayer validators independently re-evaluate a covenant against the same frozen canonical URL. The current contracts store only the semantic baseline result and its basis, not fetched source text or a source digest. They do not archive an exact historical page snapshot or diff.
