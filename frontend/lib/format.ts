export function shorten(value?: string | null, left = 6, right = 4): string {
  if (!value) return "—";
  if (value.length <= left + right + 2) return value;
  return `${value.slice(0, left)}…${value.slice(-right)}`;
}

export function attoToGen(value?: string | bigint | null, max = 4): string {
  if (value === undefined || value === null || value === "") return "0";
  const raw = typeof value === "bigint" ? value : BigInt(value);
  const whole = raw / 10n ** 18n;
  const fraction = raw % 10n ** 18n;
  if (fraction === 0n) return whole.toString();
  const digits = fraction.toString().padStart(18, "0").slice(0, max).replace(/0+$/, "");
  return digits ? `${whole}.${digits}` : whole.toString();
}

export function genToAtto(value: string): bigint {
  const text = value.trim();
  if (!/^\d+(?:\.\d{0,18})?$/.test(text)) throw new Error("Enter a valid GEN amount with at most 18 decimals");
  const [whole, fraction = ""] = text.split(".");
  return BigInt(whole) * 10n ** 18n + BigInt(fraction.padEnd(18, "0") || "0");
}

export function timeLabel(unix?: string | number | null): string {
  if (!unix) return "—";
  const numeric = Number(unix);
  if (!Number.isFinite(numeric)) return String(unix);
  return new Intl.DateTimeFormat("en-GB", { dateStyle: "medium", timeStyle: "short", timeZone: "UTC" })
    .format(new Date(numeric * 1000)) + " UTC";
}

export function isoLabel(value?: string | null): string {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return new Intl.DateTimeFormat("en-GB", { dateStyle: "medium", timeStyle: "short", timeZone: "UTC" }).format(d) + " UTC";
}

export function statusTone(status: string): "quiet" | "signal" | "warn" | "muted" {
  const s = status.toUpperCase();
  if (s.includes("BREACH") && !s.includes("PENDING")) return "signal";
  if (s.includes("PENDING") || s.includes("MATERIAL_CHANGE")) return "warn";
  if (s.includes("ACTIVE") || s.includes("VERIFIED") || s.includes("NO_RELEVANT_CHANGE") || s.includes("PERMITTED")) return "quiet";
  return "muted";
}
