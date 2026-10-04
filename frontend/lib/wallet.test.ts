import { describe, expect, it, vi } from "vitest";
import { CHAIN_HEX, CHAIN_ID, copyWalletAddress, ensureStudionet, isStudionetChain, normalizeAccounts, sameWallet } from "./wallet";

describe("wallet helpers", () => {
  it("pins the stable Studionet chain", () => {
    expect(CHAIN_ID).toBe(61999);
    expect(parseInt(CHAIN_HEX, 16)).toBe(61999);
  });

  it("drops non-string account values", () => {
    expect(normalizeAccounts(["0xabc", 3, null, "0xdef"])).toEqual(["0xabc", "0xdef"]);
  });

  it("compares addresses case-insensitively", () => {
    expect(sameWallet("0xAbC", "0xabc")).toBe(true);
    expect(sameWallet(null, "0xabc")).toBe(false);
  });

  it("detects the Studionet wallet state", () => {
    expect(isStudionetChain(61999)).toBe(true);
    expect(isStudionetChain(1)).toBe(false);
    expect(isStudionetChain(null)).toBe(false);
  });

  it("copies the exact connected address", async () => {
    const calls: string[] = [];
    await copyWalletAddress("0xAbCd", { writeText: async (value) => { calls.push(value); } });
    expect(calls).toEqual(["0xAbCd"]);
  });

  it("fails clearly when clipboard access is unavailable", async () => {
    await expect(copyWalletAddress("0xAbCd", null)).rejects.toThrow("Clipboard is not available");
  });

  it("confirms the injected wallet switched to Studionet", async () => {
    let chain = "0x1";
    const request = vi.fn(async ({ method }: { method: string }) => {
      if (method === "eth_chainId") return chain;
      if (method === "wallet_switchEthereumChain") { chain = CHAIN_HEX; return null; }
      throw new Error(method);
    });
    vi.stubGlobal("window", { ethereum: { request } });
    await expect(ensureStudionet()).resolves.toBeUndefined();
    expect(request).toHaveBeenCalledTimes(3);
  });

  it("blocks writes when the wallet refuses the Studionet switch", async () => {
    const request = vi.fn(async ({ method }: { method: string }) => method === "eth_chainId" ? "0x1" : null);
    vi.stubGlobal("window", { ethereum: { request } });
    await expect(ensureStudionet()).rejects.toThrow("Wallet is not connected to GenLayer Studionet");
  });
});
