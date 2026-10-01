import { statusTone } from "@/lib/format";

export function StatusPill({ status }: { status: string }) {
  return <span className={`status-pill ${statusTone(status)}`}><i/>{status.replaceAll("_", " ")}</span>;
}
