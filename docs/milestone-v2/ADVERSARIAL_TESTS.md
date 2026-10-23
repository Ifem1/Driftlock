# Adversarial verification

`tests/direct/test_v2_registry.py` covers forged artifact hash rejection, duplicate declared publisher rejection, owner and challenger reversals, upheld appeal bond disposition, deadline finalization, duplicate appeal rejection, replay after timeout and escrow conservation. `tests/direct/test_v2_consensus.py` covers complete artifact replay, validator disagreement after evidence mutation, contradiction blocking baseline, oversized corroborator exclusion and Judge outcome disagreement. Existing 52 V1 Direct Mode regressions remain in the suite.

These are GenVM Direct Mode tests with controlled web and LLM mocks. They prove local state transitions and validator predicates, not live finality or real-world source independence. The exact final check results are recorded in `LIVE_VERIFICATION.md`.
