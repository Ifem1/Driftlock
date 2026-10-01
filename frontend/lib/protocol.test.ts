import { describe, expect, it } from "vitest";
import { attoToGen, genToAtto, shorten, statusTone } from "./format";

 describe("format helpers", () => {
  it("round-trips GEN to atto units", () => {
    expect(genToAtto("1.25")).toBe(1_250_000_000_000_000_000n);
    expect(attoToGen(1_250_000_000_000_000_000n)).toBe("1.25");
  });

  it("shortens long identifiers without losing ends", () => {
    expect(shorten("0x1234567890abcdef", 6, 4)).toBe("0x1234…cdef");
  });

  it("uses breach as the signal state", () => {
    expect(statusTone("BREACHED")).toBe("signal");
    expect(statusTone("ACTIVE")).toBe("quiet");
    expect(statusTone("JUDGMENT_PENDING")).toBe("warn");
  });
});
