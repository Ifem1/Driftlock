# Codex handoff

This repository is a working Driftlock implementation starter, not a claim of completed live deployment.

## Product decisions are closed

Do not redesign the product. Keep:

- Studionet `61999` only;
- repository-local GenLayer CLI `0.39.1`;
- GenVM Direct Mode pin `v0.2.12`;
- Next.js frontend + the three Intelligent Contracts only;
- injected EIP-1193 wallet only;
- no application backend;
- immutable same-URL covenant model;
- separate source-inspection and breach-judgment consensus stages;
- pull-accounting settlement;
- Noir-inspired dark editorial frontend and cinematic motion already implemented here.

## First job

Do not trust this handoff. Audit the actual source before changing anything.

1. install exact dependencies;
2. run all three `genvm-lint` checks;
3. run the full Direct Mode suite on Ubuntu if native Windows gltest cleanup interferes;
4. run frontend tests, typecheck, lint and production build;
5. inspect every failing path rather than weakening tests;
6. perform a hostile security review of state races, callbacks, bounds and accounting;
7. add/fix regression tests until final CI is green.

The current suite is a substantial foundation but the final target should be at least 30 meaningful Direct Mode/adversarial tests. Add missing coverage rather than padding count.

## Frontend

Preserve the final design direction. Do not replace it with a generic dashboard.

Reference quality: `https://www.motionsite.ai/templates/noir`

Keep the original Driftlock visual translation already in `frontend/app/globals.css` and `HomeExperience.tsx`:

- near-black editorial palette;
- warm ivory typography;
- rare vermilion breach signal;
- large type;
- Motion-driven scroll narrative;
- baseline/current document choreography;
- premium multi-step composer;
- restrained protocol-state motion;
- reduced-motion support.

Improve polish where needed after real browser verification, but do not clone the reference template.

## Deployment and proof

After source/CI is genuinely clean:

1. verify local CLI is `0.39.1` and network is `studionet` chain `61999`;
2. deploy Registry -> Inspector -> Judge and perform one-time component binding;
3. verify schemas, component addresses and Registry stats;
4. commit `deployments/studionet.json` and configure frontend env;
5. deploy production frontend to Vercel;
6. create the live demo covenant using the stable raw GitHub URL for `demo-source/public-promise.txt`;
7. perform an unchanged challenge and preserve finalized proof;
8. commit the planned semantic source change at the same path/URL;
9. perform the second challenge and preserve `MATERIAL_CHANGE` + `BREACH` proof;
10. withdraw finder/beneficiary credits and verify accounting;
11. manually browser-test wallet rejection, account switch, wrong network, refresh recovery, challenge flow, transaction finality and responsive motion;
12. populate `docs/LIVE_VALIDATION.md`, `docs/REVIEW_EVIDENCE.md` and `/demo` with only verified data.

## GitHub / Vercel finish

When complete, push the audited clean project to the user's GitHub repository and deploy the frontend to Vercel. Record final commit, green CI run and production deployment ID/URL.

Never claim a transaction, test, deployment or browser path is verified unless you actually checked it.
