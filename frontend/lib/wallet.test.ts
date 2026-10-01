import { afterEach, describe, expect, it, vi } from "vitest";
import { CHAIN_HEX, CHAIN_ID, copyWalletAddress, currentWriteAccount, isStudionetChain, normalizeAccounts, sameWallet } from "./wallet";

afterEach(() => { vi.unstubAllGlobals(); });

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

  it("switches and rechecks the chain before a write", async () => {
    let chain = "0x1";
    const request = vi.fn(async ({ method }: { method: string }) => {
      if (method === "eth_chainId") return chain;
      if (method === "wallet_switchEthereumChain") { chain = CHAIN_HEX; return null; }
      if (method === "eth_accounts") return ["0xabc"];
      throw new Error(method);
    });
    vi.stubGlobal("window", { ethereum: { request } });
    await expect(currentWriteAccount("0xAbC")).resolves.toBe("0xabc");
    expect(request).toHaveBeenCalledWith({ method: "wallet_switchEthereumChain", params: [{ chainId: CHAIN_HEX }] });
  });

  it("aborts when the switch does not change the chain", async () => {
    vi.stubGlobal("window", { ethereum: { request: vi.fn(async ({ method }: { method: string }) => method === "eth_chainId" ? "0x1" : null) } });
    await expect(currentWriteAccount("0xabc")).rejects.toThrow("not connected");
  });

  it("aborts when the account changes before signing", async () => {
    vi.stubGlobal("window", { ethereum: { request: vi.fn(async ({ method }: { method: string }) => method === "eth_chainId" ? CHAIN_HEX : ["0xdef"]) } });
    await expect(currentWriteAccount("0xabc")).rejects.toThrow("account changed");
  });
});
