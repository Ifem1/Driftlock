import { describe, expect, it } from "vitest";
import { attoToGen, genToAtto, shorten, statusTone } from "./format";
import { assertSuccessfulExecution, baselineExpiryAvailable, challengeExpiryAvailable } from "./protocol";
import type { Challenge, Covenant } from "./types";

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

describe("recovery action eligibility", () => {
  it("supports the deployed covenant view without a can_expire_baseline field", () => {
    expect(baselineExpiryAvailable({
      status: "BASELINE_PENDING", baseline_deadline: "100", expires_at: "200",
    } as unknown as Covenant, 100)).toBe(true);
    expect(baselineExpiryAvailable({
      status: "BASELINE_PENDING", baseline_deadline: "100", expires_at: "200",
    } as unknown as Covenant, 200)).toBe(false);
  });

  it("supports the deployed challenge list without a can_expire field", () => {
    expect(challengeExpiryAvailable({
      status: "INSPECTION_PENDING", stage_deadline: "100",
    } as unknown as Challenge, 100)).toBe(true);
    expect(challengeExpiryAvailable({
      status: "BREACH", stage_deadline: "100",
    } as unknown as Challenge, 200)).toBe(false);
  });

  it("uses explicit finalized Registry eligibility when available", () => {
    expect(baselineExpiryAvailable({
      status: "BASELINE_PENDING", can_expire_baseline: false, baseline_deadline: "1", expires_at: "200",
    } as unknown as Covenant, 100)).toBe(false);
    expect(challengeExpiryAvailable({
      status: "JUDGMENT_PENDING", can_expire: false, stage_deadline: "1",
    } as unknown as Challenge, 100)).toBe(false);
  });
});
