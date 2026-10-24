# V2 economics

The creator deposits 0.001–10 test GEN. Challenger bond is `max(0.0001 GEN, stake / 100)` and is frozen per covenant. An eligible appellant posts the **same** bond. Finder reward is the frozen 1–25% basis-point share of remaining stake.

No provisional outcome releases stake or bonds. Unappealed finalization begins after the one-hour window. A breach returns the challenge bond and credits the finder reward to the challenger and the rest of stake to the beneficiary. A final no-change or permitted change credits the challenge bond to the owner. Inconclusive resolution refunds it to the challenger. An upheld appeal forfeits the appeal bond to the opposing party; an overturned or timed-out appeal refunds it to the appellant. The Registry determines all amounts and recipients without LLM input.

Funds move into claimable credits before pull withdrawal. The invariant is `total_deposited = stake_escrow + bond_escrow + appeal_escrow + claimable + withdrawn`. Direct Mode lifecycle tests assert this across reversal, upheld appeal, timeout and finalization. Live V2 multi-source breach-appeal payout and finalized credit withdrawal have been demonstrated; the same live record reports remaining unrelated stake and bond escrow, with accounting balanced. No recovery or withdrawal transaction is included in this closeout.
