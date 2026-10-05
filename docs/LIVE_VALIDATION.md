# Live validation

Status: **STUDIONET DEPLOYMENT VERIFIED; OWNER-REPORTED BROWSER WALLET VERIFICATION COMPLETE**

## Verified deployment on Studionet 61999

Deployed 2026-10-01 with repository-local GenLayer CLI `0.39.1` and GenVM pin `v0.2.12`:

| Component | Address | Finalized deployment transaction |
| --- | --- | --- |
| DriftRegistry | `0xDc1bDE6d262baAa6084a474570b73E724De12ddA` | `0xa61bcf245944be3c2bb5be42d847f0f53e9292c3f04390f00c2414c811d23c73` |
| SourceInspector | `0xBb19613948808a9323594C0945118F10C7979585` | `0x2050636fe00199dabffbe07419651bd42cb4f9b5104051b2662feca7bb5a6945` |
| BreachJudge | `0xbb3acd8a549A3Ab5c18deC6762f9876B1E13bfaf` | `0x20c9798fe26b2a7d9ee79a53e4d3b6e25a0dd0be269a360869141df70f9c23a0` |

One-time component binding finalized in `0xd3498a192d0548cbc4e695657a22a4f338b1deb72051b0af9104d81dbf153d3c`. All four receipts independently returned `status_name: FINALIZED`. The three deployed schemas were read back. Registry `get_stats` returned the exact Inspector/Judge addresses, `components_configured: true`, and `accounting_balanced: true` with zero covenants.

The production frontend is READY at `https://driftlock-nine.vercel.app/`; Vercel reported success for submission-readiness commit `93a4434f52fb62be04c1c4c606cfdd83198d020c`. The project owner reports manually verifying injected-wallet browser paths, including wallet interaction and transactions. This is manual verification, separate from automated CI.

## Evidence scope

The deployment receipts, component binding, schema reads and zero-covenant accounting state above are recorded verification evidence. Owner-reported browser wallet checks are manual and are not automated CI results. This repository does not include a canonical complete demo-covenant lifecycle transaction record, so this document makes no claim that it does.

GenLayer validators independently re-evaluate the covenant against the same frozen canonical URL. The protocol stores bounded verified baseline text and its digest; it does not archive a permanent historical snapshot or diff of every later fetched page.
