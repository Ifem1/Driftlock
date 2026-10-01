# Live validation

Status: **DEPLOYMENT VERIFIED; TWO-WALLET PROOF PENDING**

## Verified deployment on Studionet 61999

Deployed 2026-10-01 with repository-local GenLayer CLI `0.39.1` and GenVM pin `v0.2.12`:

| Component | Address | Finalized deployment transaction |
| --- | --- | --- |
| DriftRegistry | `0xDc1bDE6d262baAa6084a474570b73E724De12ddA` | `0xa61bcf245944be3c2bb5be42d847f0f53e9292c3f04390f00c2414c811d23c73` |
| SourceInspector | `0xBb19613948808a9323594C0945118F10C7979585` | `0x2050636fe00199dabffbe07419651bd42cb4f9b5104051b2662feca7bb5a6945` |
| BreachJudge | `0xbb3acd8a549A3Ab5c18deC6762f9876B1E13bfaf` | `0x20c9798fe26b2a7d9ee79a53e4d3b6e25a0dd0be269a360869141df70f9c23a0` |

One-time component binding finalized in `0xd3498a192d0548cbc4e695657a22a4f338b1deb72051b0af9104d81dbf153d3c`. All four receipts independently returned `status_name: FINALIZED`. The three deployed schemas were read back. Registry `get_stats` returned the exact Inspector/Judge addresses, `components_configured: true`, and `accounting_balanced: true` with zero covenants.

Production Vercel deployment `dpl_oG3XX2Gd5FHkr2Hn92BPPZHUwFMy` reached READY at `https://driftlock-ruby.vercel.app`. The project currently has Vercel SSO protection, so public browser validation is pending a specific access decision.

## Pending live proof

The following items have not yet been verified. Do not infer them from the deployment above.

Required evidence:

- final deployed source commit;
- Registry / SourceInspector / BreachJudge addresses;
- deployment and one-time binding transaction hashes;
- baseline covenant creation + finalized baseline result;
- unchanged challenge + finalized `NO_RELEVANT_CHANGE`;
- demo source BEFORE commit SHA;
- demo source AFTER commit SHA at the same canonical raw URL;
- second challenge + finalized `MATERIAL_CHANGE`;
- finalized `BREACH` judgment;
- finder reward and beneficiary credit reads;
- withdrawal transactions;
- final `get_stats` with `accounting_balanced=true`;
- production frontend manual browser run.
