"use client";

import { createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";
import { TransactionHashVariant } from "genlayer-js/types";
import { injectedProvider, RPC_URL } from "./wallet";
import type { Challenge, Covenant, ProtocolStats } from "./types";

export const REGISTRY_ADDRESS = process.env.NEXT_PUBLIC_REGISTRY_ADDRESS || "";
export const INSPECTOR_ADDRESS = process.env.NEXT_PUBLIC_INSPECTOR_ADDRESS || "";
export const JUDGE_ADDRESS = process.env.NEXT_PUBLIC_JUDGE_ADDRESS || "";

export function protocolConfigured(): boolean {
  return /^0x[0-9a-fA-F]{40}$/.test(REGISTRY_ADDRESS);
}

function assertRegistry(): `0x${string}` {
  if (!protocolConfigured()) throw new Error("Driftlock Registry is not configured. Set NEXT_PUBLIC_REGISTRY_ADDRESS.");
  return REGISTRY_ADDRESS as `0x${string}`;
}

function normalize(value: unknown): any {
  if (value instanceof Map) return Object.fromEntries(Array.from(value.entries()).map(([k, v]) => [String(k), normalize(v)]));
  if (Array.isArray(value)) return value.map(normalize);
  if (value && typeof value === "object") {
    const out: Record<string, unknown> = {};
    for (const [key, val] of Object.entries(value)) out[key] = normalize(val);
    return out;
  }
  return typeof value === "bigint" ? value.toString() : value;
}

const rpcTimes: number[] = [];
const cache = new Map<string, { expires: number; value: unknown }>();
const inflight = new Map<string, Promise<unknown>>();
const RPC_WINDOW_MS = 60_000;
const RPC_BUDGET = 24;

async function reserveRpc(): Promise<void> {
  while (true) {
    const now = Date.now();
    while (rpcTimes.length && now - rpcTimes[0] >= RPC_WINDOW_MS) rpcTimes.shift();
    if (rpcTimes.length < RPC_BUDGET) { rpcTimes.push(now); return; }
    await new Promise((resolve) => setTimeout(resolve, Math.max(500, RPC_WINDOW_MS - (now - rpcTimes[0]) + 50)));
  }
}

async function withBudget<T>(operation: () => Promise<T>): Promise<T> {
  let delay = 1200;
  for (let attempt = 0; ; attempt += 1) {
    await reserveRpc();
    try { return await operation(); }
    catch (error) {
      const message = String((error as Error)?.message || error).toLowerCase();
      const retry = message.includes("429") || message.includes("rate limit") || message.includes("too many requests") || message.includes("fetch failed");
      if (!retry || attempt >= 3) throw error;
      await new Promise((resolve) => setTimeout(resolve, delay));
      delay = Math.min(delay * 2, 10_000);
    }
  }
}

export function readClient() {
  return createClient({ chain: studionet, endpoint: RPC_URL } as any);
}

async function writeClient(address: string) {
  const provider = injectedProvider();
  if (!provider) throw new Error("No injected EIP-1193 wallet found");
  return createClient({ chain: studionet, endpoint: RPC_URL, account: address as `0x${string}`, provider } as any);
}

async function read<T>(functionName: string, args: unknown[] = [], latest = false): Promise<T> {
  const key = JSON.stringify([functionName, args.map((v) => typeof v === "bigint" ? v.toString() : v), latest]);
  const existing = cache.get(key);
  if (existing && existing.expires > Date.now()) return existing.value as T;
  const pending = inflight.get(key);
  if (pending) return pending as Promise<T>;
  const request = withBudget(() => readClient().readContract({
    address: assertRegistry(), functionName, args,
    transactionHashVariant: latest ? TransactionHashVariant.LATEST_NONFINAL : TransactionHashVariant.LATEST_FINAL,
  } as any)).then(normalize).then((value) => {
    cache.set(key, { value, expires: Date.now() + (latest ? 1800 : 7000) });
    return value as T;
  }).finally(() => inflight.delete(key));
  inflight.set(key, request);
  return request;
}

export async function listCovenants(offset = 0, count = 24): Promise<{ items: Covenant[]; total: string }> {
  return read("list_covenants", [BigInt(offset), BigInt(count)]);
}
export async function getCovenant(id: string, latest = false): Promise<Covenant> { return read("get_covenant", [id], latest); }
export async function listChallenges(id: string, offset = 0, count = 24, latest = false): Promise<{ items: Challenge[]; total: string }> {
  return read("list_challenges", [id, BigInt(offset), BigInt(count)], latest);
}
export async function listWalletChallenges(address: string, offset = 0, count = 24, latest = false): Promise<{ items: Challenge[]; total: string }> {
  return read("list_wallet_challenges", [address, BigInt(offset), BigInt(count)], latest);
}
export async function getStats(): Promise<ProtocolStats> { return read("get_stats"); }
export async function getCredit(address: string, latest = false): Promise<string> { return read("get_credit", [address], latest); }
export async function findLatestCovenantByOwner(address: string, latest = false): Promise<string> { return read("find_latest_covenant_by_owner", [address], latest); }

export async function submitWrite(address: string, functionName: string, args: unknown[] = [], value = 0n): Promise<string> {
  const client = await writeClient(address);
  const hash = await withBudget(() => client.writeContract({ address: assertRegistry(), functionName, args, value } as any));
  cache.clear();
  return String(hash);
}

export async function waitForFinalization(hash: string): Promise<unknown> {
  return readClient().waitForTransactionReceipt({ hash: hash as any, status: "FINALIZED" as any, retries: 240, interval: 15_000 });
}
