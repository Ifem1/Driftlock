import { readFileSync, writeFileSync } from "node:fs";
import { createClient, createAccount } from "genlayer-js";
import { studionet } from "genlayer-js/chains";
import { TransactionHashVariant, TransactionStatus } from "genlayer-js/types";
import keytar from "keytar";

const rpc = "https://studio.genlayer.com/api";
const sourceUrl = "https://raw.githubusercontent.com/Ifem1/Driftlock/codex/audit-fix/demo-source/public-promise.txt";
const registry = JSON.parse(readFileSync("deployments/studionet.json", "utf8")).contracts.registry.address;
const proofPath = "deployments/live-proof.json";
const phase = process.argv[2];
const ownerName = "cutover-live-owner-20260930";
const challengerName = "cutover-challenger-1-20260930";
const beneficiaryName = "cutover-challenger-2-20260930";

function normalize(value: any): any {
  if (value instanceof Map) return Object.fromEntries([...value.entries()].map(([k, v]) => [String(k), normalize(v)]));
  if (Array.isArray(value)) return value.map(normalize);
  if (value && typeof value === "object") return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, normalize(v)]));
  return typeof value === "bigint" ? value.toString() : value;
}

async function account(name: string) {
  const key = await keytar.getPassword("genlayer-cli", `account:${name}`);
  if (!key) throw new Error(`Test wallet ${name} is not unlocked in the OS keychain`);
  return createAccount(key as `0x${string}`);
}

function client(wallet?: any) {
  return createClient({ chain: studionet, endpoint: rpc, ...(wallet ? { account: wallet } : {}) } as any);
}

async function read(method: string, args: unknown[] = []) {
  return normalize(await client().readContract({ address: registry, functionName: method, args,
    transactionHashVariant: TransactionHashVariant.LATEST_FINAL } as any));
}

async function send(wallet: any, method: string, args: unknown[], value = 0n) {
  const signer = client(wallet);
  const hash = String(await signer.writeContract({ address: registry, functionName: method, args, value } as any));
  console.log(`${method} submitted: ${hash}`);
  const receipt: any = await signer.waitForTransactionReceipt({ hash: hash as any, status: TransactionStatus.FINALIZED,
    retries: 240, interval: 5000 } as any);
  const status = receipt?.statusName ?? receipt?.status_name;
  if (status !== "FINALIZED") throw new Error(`${method} did not finalize: ${status}`);
  console.log(`${method} finalized: ${hash}`);
  return hash;
}

function save(update: Record<string, unknown>) {
  let existing: Record<string, unknown> = {};
  try { existing = JSON.parse(readFileSync(proofPath, "utf8")); } catch { /* first phase */ }
  writeFileSync(proofPath, JSON.stringify({ ...existing, ...update }, null, 2) + "\n");
}

async function pollCovenant(id: string, expected: string[], attempts = 100) {
  for (let i = 0; i < attempts; i++) {
    const state = await read("get_covenant", [id]);
    if (expected.includes(state.status)) return state;
    await new Promise((resolve) => setTimeout(resolve, 10000));
  }
  throw new Error(`Covenant ${id} did not reach ${expected.join("/")} within the proof window`);
}

async function pollChallenge(id: string, attempts = 100) {
  const terminal = ["NO_RELEVANT_CHANGE", "SOURCE_UNAVAILABLE", "AMBIGUOUS", "PERMITTED_CHANGE", "INCONCLUSIVE", "BREACH", "TIMED_OUT", "STALE", "PROTOCOL_BLOCKED"];
  for (let i = 0; i < attempts; i++) {
    const state = await read("get_challenge", [id]);
    if (terminal.includes(state.status)) return state;
    await new Promise((resolve) => setTimeout(resolve, 10000));
  }
  throw new Error(`Challenge ${id} did not settle within the proof window`);
}

async function main() {
  const owner = await account(ownerName);
  const challenger = await account(challengerName);
  const beneficiary = await account(beneficiaryName);
  if (new Set([owner.address, challenger.address, beneficiary.address].map((x) => x.toLowerCase())).size !== 3) {
    throw new Error("Proof wallets must be distinct");
  }
  if (phase === "create") {
    const expires = BigInt(Math.floor(Date.now() / 1000) + 2 * 86400);
    const hash = await send(owner, "create_covenant", [
      "Public customer-data promise", "The current customer-data policy of Driftlock Demo Company.", sourceUrl,
      "Customer information is not sold, licensed or commercially transferred to third parties.",
      "Allowing the sale, commercial licensing or commercial transfer of customer information to third parties constitutes breach.",
      "Formatting, typography and unrelated clarifications are permitted.", beneficiary.address, 1000n, expires,
    ], 10n ** 16n);
    const id = String(await read("find_latest_covenant_by_owner", [owner.address]));
    const covenant = await pollCovenant(id, ["ACTIVE", "BASELINE_REJECTED", "BASELINE_RETRYABLE", "EXPIRED_UNVERIFIED"]);
    save({ sourceUrl, owner: owner.address, challenger: challenger.address, beneficiary: beneficiary.address,
      covenantId: id, createTx: hash, baseline: covenant.baseline_review, baselineState: covenant.status });
    console.log(JSON.stringify({ covenantId: id, status: covenant.status, baseline: covenant.baseline_review }, null, 2));
    return;
  }
  const proof = JSON.parse(readFileSync(proofPath, "utf8"));
  const id = proof.covenantId;
  if (!id) throw new Error("Create phase must run first");
  if (phase === "verify") {
    const covenant = await read("get_covenant", [id]);
    const challenge = await read("get_challenge", [proof.changed.challengeId]);
    const credits = {
      owner: await read("get_credit", [owner.address]),
      challenger: await read("get_credit", [challenger.address]),
      beneficiary: await read("get_credit", [beneficiary.address]),
    };
    const stats = await read("get_stats");
    const verification = { covenantStatus: covenant.status, remainingStake: covenant.remaining_stake_atto,
      challengeStatus: challenge.status, inspection: challenge.inspection, judgment: challenge.judgment, credits, stats };
    save({ finalVerification: verification });
    console.log(JSON.stringify(verification, null, 2));
    return;
  }
  if (phase === "challenge-unchanged" || phase === "challenge-changed") {
    const covenant = await read("get_covenant", [id]);
    if (!covenant.can_challenge) throw new Error("Covenant is not challengeable yet (cooldown or stage)");
    const hash = await send(challenger, "challenge_covenant", [id], BigInt(covenant.challenge_bond_atto));
    const page = await read("list_challenges", [id, BigInt(Number(covenant.challenge_count)), 1n]);
    const challengeId = page.items?.[0]?.id;
    if (!challengeId) throw new Error("Finalized challenge ID not found");
    const challenge = await pollChallenge(challengeId);
    const settledCovenant = await read("get_covenant", [id]);
    const label = phase === "challenge-unchanged" ? "unchanged" : "changed";
    save({ [label]: { challengeTx: hash, challengeId, challenge, covenantStatus: settledCovenant.status } });
    console.log(JSON.stringify({ challengeId, status: challenge.status, inspection: challenge.inspection,
      judgment: challenge.judgment, covenantStatus: settledCovenant.status }, null, 2));
    return;
  }
  if (phase === "withdraw") {
    const creditsBefore = {
      owner: await read("get_credit", [owner.address]),
      challenger: await read("get_credit", [challenger.address]),
      beneficiary: await read("get_credit", [beneficiary.address]),
    };
    const withdrawalTxs: Record<string, string> = {};
    for (const [name, wallet] of [["owner", owner], ["challenger", challenger], ["beneficiary", beneficiary]] as const) {
      if (BigInt(creditsBefore[name]) > 0n) withdrawalTxs[name] = await send(wallet, "withdraw_credit", [wallet.address]);
    }
    const stats = await read("get_stats");
    save({ creditsBefore, withdrawalTxs, finalStats: stats });
    console.log(JSON.stringify({ creditsBefore, withdrawalTxs, stats }, null, 2));
    return;
  }
  throw new Error("Phase must be create, challenge-unchanged, challenge-changed, withdraw, or verify");
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
