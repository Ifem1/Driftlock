"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { ExternalLink, LockKeyhole, ScanLine, ShieldAlert } from "lucide-react";
import { toast } from "sonner";
import { getCovenant, listChallenges, protocolConfigured, submitWrite, waitForFinalization } from "@/lib/protocol";
import type { Challenge, Covenant } from "@/lib/types";
import { attoToGen, isoLabel, shorten, timeLabel } from "@/lib/format";
import { EXPLORER_URL, useInjectedWallet } from "@/lib/wallet";
import { StatusPill } from "@/components/StatusPill";

const stages = ["BASELINE LOCKED", "ACTIVE", "CHALLENGE", "SOURCE INSPECTION", "BREACH JUDGMENT", "SETTLEMENT"];

function activeStage(c?: Covenant): number {
  if (!c) return 0;
  if (c.status === "BREACHED" || c.status.startsWith("EXPIRED")) return 5;
  if (c.pending_challenge) return c.last_inspection?.status === "MATERIAL_CHANGE" ? 4 : 3;
  if (c.status === "ACTIVE") return 1;
  return 0;
}

export default function CovenantDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const wallet = useInjectedWallet();
  const [covenant, setCovenant] = useState<Covenant>();
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [busy, setBusy] = useState(false);
  const [tx, setTx] = useState("");
  const configured = protocolConfigured();

  async function refresh(latest = false) {
    if (!configured) return;
    const [c, hs] = await Promise.all([getCovenant(id, latest), listChallenges(id, 0, 24, latest)]);
    setCovenant(c); setChallenges(hs.items.slice().reverse());
  }
  useEffect(() => { void refresh(); }, [id, configured]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => {
    if (!configured || !covenant || (covenant.status !== "BASELINE_PENDING" && !covenant.pending_challenge)) return;
    const timer = window.setInterval(() => { void refresh(true); }, 15_000);
    return () => window.clearInterval(timer);
  }, [configured, covenant?.status, covenant?.pending_challenge, id]); // eslint-disable-line react-hooks/exhaustive-deps

  async function challenge() {
    if (!covenant || !wallet.address) return;
    setBusy(true); setTx("");
    try {
      if (!wallet.correctNetwork) await wallet.switchNetwork();
      const hash = await submitWrite(wallet.address, "challenge_covenant", [covenant.id], BigInt(covenant.challenge_bond_atto));
      setTx(hash); toast("Challenge submitted", { description: "Waiting for GenLayer finality." });
      await waitForFinalization(hash);
      toast.success("Challenge finalized");
      await refresh(true);
    } catch (e) { toast.error(e instanceof Error ? e.message : String(e)); }
    finally { setBusy(false); }
  }

  if (!configured) return <section className="page-shell"><div className="deployment-note"><strong>Registry not configured.</strong><span>Deploy Driftlock first, then set NEXT_PUBLIC_REGISTRY_ADDRESS.</span></div></section>;
  if (!covenant) return <section className="page-shell"><div className="loading-panel">Reading finalized covenant state…</div></section>;
  const stage = activeStage(covenant);

  return <section className="page-shell detail-page">
    <div className="detail-hero"><div><div className="detail-topline"><StatusPill status={covenant.status}/><span>{covenant.id}</span></div><h1>{covenant.title}</h1><blockquote>{covenant.protected_promise}</blockquote></div><aside className="stake-panel"><small>STAKE LOCKED</small><strong>{attoToGen(covenant.remaining_stake_atto)} <i>GEN</i></strong><dl><div><dt>Owner</dt><dd>{shorten(covenant.owner)}</dd></div><div><dt>Beneficiary</dt><dd>{shorten(covenant.beneficiary)}</dd></div><div><dt>Finder reward</dt><dd>{Number(covenant.finder_reward_bps)/100}%</dd></div><div><dt>Expiry</dt><dd>{timeLabel(covenant.expires_at)}</dd></div></dl></aside></div>

    <div className="lifecycle-rail">{stages.map((label, i) => <div key={label} className={`life-step ${i < stage ? "past" : i === stage ? "current" : "future"}`}><span>{String(i+1).padStart(2,"0")}</span><i/><b>{label}</b></div>)}</div>

    <div className="detail-grid">
      <div>
        <section className="detail-block"><span className="mono-label">IMMUTABLE COVENANT</span><div className="rule-grid"><div><small>SUBJECT</small><p>{covenant.subject}</p></div><div><small>BREACH RULE</small><p>{covenant.breach_rule}</p></div><div><small>PERMITTED CHANGES</small><p>{covenant.permitted_changes}</p></div><div><small>CANONICAL SOURCE</small><a href={covenant.canonical_url} target="_blank" rel="noreferrer">{covenant.canonical_url}<ExternalLink size={13}/></a></div></div></section>

        <section className="compare-section"><div className="compare-head"><span className="mono-label">BASELINE / CURRENT</span><h2>Same source.<br/><em>Different moment.</em></h2></div><div className="compare-grid"><article><header><LockKeyhole size={15}/> BASELINE</header><blockquote>{covenant.baseline_review?.baseline_text?.slice(0, 500) || "No verified baseline source evidence is available yet."}</blockquote><footer><StatusPill status={String(covenant.baseline_review?.status || "PENDING")}/><span>{covenant.baseline_review?.recorded_at ? `Captured ${isoLabel(covenant.baseline_review.recorded_at)} · ` : ""}{covenant.baseline_review?.baseline_digest ? `SHA-256 ${covenant.baseline_review.baseline_digest}` : String(covenant.baseline_review?.basis || "Awaiting finalized baseline consensus.")}</span></footer></article><article className={covenant.last_inspection?.status === "MATERIAL_CHANGE" ? "changed" : ""}><header><ScanLine size={15}/> CURRENT</header><blockquote>{covenant.last_inspection?.current_excerpt || "No finalized current source excerpt is available yet."}</blockquote><footer>{covenant.last_inspection ? <><StatusPill status={String(covenant.last_inspection.status)}/><span>{covenant.last_inspection.current_digest ? `SHA-256 ${covenant.last_inspection.current_digest}` : ""}</span></> : <span className="muted-copy">UNCHALLENGED</span>}</footer></article></div></section>

        <section className="challenge-history"><div className="section-mini-head"><span className="mono-label">CHALLENGE HISTORY / {challenges.length}</span><h2>Every inspection leaves a trace.</h2></div>{!challenges.length && <div className="empty-editorial">No finalized or pending challenges yet.</div>}{challenges.map((h) => <article key={h.id} className="history-row"><div><StatusPill status={h.status}/><strong>{h.id}</strong></div><p>{String(h.judgment?.basis || h.inspection?.basis || "Consensus in progress.")}</p><span>{isoLabel(h.created_at)}</span></article>)}</section>
      </div>

      <aside className="challenge-aside"><div className="challenge-card"><ShieldAlert size={22}/><span className="mono-label">CHALLENGE THE CURRENT PROMISE</span><h3>Inspect the same canonical source again.</h3><p>You do not submit evidence. Driftlock refetches the URL frozen at covenant creation and lets GenLayer decide what changed.</p><div className="bond-line"><span>Challenge bond</span><strong>{attoToGen(covenant.challenge_bond_atto)} GEN</strong></div>{!wallet.connected ? <button className="action-button" onClick={() => void wallet.connect()}>Connect wallet</button> : <button className="action-button" disabled={!covenant.can_challenge || busy} onClick={() => void challenge()}>{busy ? "Resolving…" : covenant.can_challenge ? "Inspect current promise" : "Challenge unavailable"}</button>}{tx && <a className="tx-proof" href={`${EXPLORER_URL}/tx/${tx}`} target="_blank" rel="noreferrer">View submitted transaction ↗</a>}</div></aside>
    </div>
  </section>;
}
