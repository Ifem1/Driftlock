# Consensus model

V2 separates deterministic checks from semantic interpretation. Registry policy validation, request IDs, callback sender checks, SHA-256 recomputation, evidence bounds, appeal deadlines and payouts are deterministic. Inspector and Judge use GenLayer nondeterministic execution for source interpretation.

Inspector validators independently render every frozen URL and compare the complete evidence records, source classifications, primary status and all outcome booleans. Judge validators independently interpret the **committed incident artifacts** and compare outcome, semantic booleans, corroboration classes and evidence digest. Explanatory `basis` text is bounded but not compared, so it is not claimed as validator-agreed wording.

The policy can only reduce certainty: a corroborator cannot override an unavailable or noncompliant primary. Contradiction or failure to meet the threshold prevents definitive baseline activation or material-change detection. An unavailable or oversized corroborator cannot count as support. `INCONCLUSIVE` and timeouts cannot pay a breach reward.

Direct Mode confirms the local leader/validator disagreement paths. GitHub Actions release-head run 40015269612 and post-merge run 40015703424 passed contracts, frontend and CLI jobs. Live Studionet finality is recorded for V2 deployment/binding, baseline and unchanged-source appeal lifecycle, V2 ambiguous outcomes, and the separate `dl-5`/`dc-5` multi-source source-change breach, bonded appeal, upheld judgment, settlement and withdrawal. The earlier breach and payout lifecycle through the retained single-source compatibility method remains documented separately.
