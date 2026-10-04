import { describe, expect, it } from "vitest";
import { attoToGen, genToAtto, shorten, statusTone } from "./format";
import { assertSuccessfulExecution } from "./protocol";

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

describe("finalized transaction execution", () => {
  it("accepts only a finalized transaction that returned successfully", () => {
    expect(() => assertSuccessfulExecution({
      statusName: "FINALIZED",
      txExecutionResultName: "FINISHED_WITH_RETURN",
    }, "0xabc")).not.toThrow();
  });

  it("rejects finalized contract execution errors with the execution reason", () => {
    expect(() => assertSuccessfulExecution({
      statusName: "FINALIZED",
      txExecutionResultName: "FINISHED_WITH_ERROR",
      consensus_data: { leader_receipt: [{ error: "expiry must be in range" }] },
    }, "0xabc")).toThrow("0xabc finalized but contract execution failed (FINISHED_WITH_ERROR): expiry must be in range");
  });

  it("rejects a receipt that is not finalized", () => {
    expect(() => assertSuccessfulExecution({
      statusName: "ACCEPTED",
      txExecutionResultName: "FINISHED_WITH_RETURN",
    }, "0xabc")).toThrow("0xabc did not finalize (status: ACCEPTED)");
  });
});
