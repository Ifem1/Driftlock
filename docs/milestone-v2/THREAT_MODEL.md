# Threat model and limits

| Threat | Enforced control | Remaining limit |
|---|---|---|
| Forged leader outcome | Validators independently reproduce semantic fields, classes and evidence | GenLayer consensus behavior still requires live verification |
| Mutable page substitution | Complete incident rendered text and digest stored before judgment and appeal | This is not a raw HTTP snapshot or publisher signature |
| Oversized/truncated evidence | 6,000-byte bound; empty/oversized entries have no artifact and cannot corroborate | Rendering itself is subject to GenLayer web-tool behavior |
| Fake independent publisher | Distinct site suffixes and declared publisher names; primary remains mandatory | Declared ownership can be false; no cryptographic publisher proof |
| Prompt injection | Prompts mark source/rebuttal text untrusted; validators independently replay | Semantic model robustness is empirical, not a formal proof |
| Forged callback or replay | Fixed child sender, request IDs, stage checks, policy/evidence digests | Child finality must be verified on live network |
| Premature payout | Provisional state holds all escrow; permissionless finalization follows deadline | Live breach settlement and withdrawal were demonstrated on the Registry compatibility path; V2 multi-source breach appeal finality remains unverified |
| Double withdrawal | Credit zeroed and aggregate counters updated before transfer emission | Failed transfer semantics need live fault testing |
| Expiry while appealed | Covenant expiry rejects pending provisional/appeal stages; challenge recovery is explicit | A live delayed-child sequence remains untested |

There is no privileged verdict override. The current source cannot by itself prove that a corroborator is editorially independent. This limits the assurance strength and should be reviewed before a release claim.
