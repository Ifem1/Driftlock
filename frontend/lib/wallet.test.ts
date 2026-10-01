import { describe, expect, it } from "vitest";
import { CHAIN_HEX, CHAIN_ID, normalizeAccounts, sameWallet } from "./wallet";

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
});
