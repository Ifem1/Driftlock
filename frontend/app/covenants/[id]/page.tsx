"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { ExternalLink, LockKeyhole, ScanLine, ShieldAlert } from "lucide-react";
import { toast } from "sonner";
import { baselineExpiryAvailable, challengeExpiryAvailable, getCovenant, listChallenges, protocolConfigured, submitWrite, waitForFinalization } from "@/lib/protocol";
import type { Challenge, Covenant } from "@/lib/types";
import { attoToGen, isoLabel, shorten, timeLabel } from "@/lib/format";
import { EXPLORER_URL, sameWallet, useInjectedWallet } from "@/lib/wallet";
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
    const c = await getCovenant(id, latest);
    const total = Number(c.challenge_count || 0);
    const pageSize = Math.min(total, 24);
    const hs = await listChallenges(id, Math.max(0, total - pageSize), Math.max(1, pageSize), latest);
    setCovenant(c); setChallenges(hs.items.slice().reverse());
  }
  useEffect(() => { void refresh(); }, [id, configured]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => {
    if (!configured || !covenant || (covenant.status !== "BASELINE_PENDING" && !covenant.pending_challenge)) return;
    const timer = window.setInterval(() => { void refresh(true); }, 15_000);
    return () => window.clearInterval(timer);
  }, [configured, covenant?.status, covenant?.pending_challenge, id]); // eslint-disable-line react-hooks/exhaustive-deps

  async function writeAction(functionName: string, args: string[], submitted: string, success: string, value = 0n) {
    if (!wallet.address) { toast.error("Connect a wallet to submit this action."); return; }
    setBusy(true); setTx("");
    try {
      const hash = await submitWrite(wallet.address, functionName, args, value);
      setTx(hash); toast(`${submitted} submitted`, { description: "Waiting for GenLayer finality." });
      await waitForFinalization(hash);
      toast.success(success);
      await refresh(true);
    } catch (e) { toast.error(e instanceof Error ? e.message : String(e)); }
    finally { setBusy(false); }
  }

  function challenge() {
    if (!covenant) return;
    void writeAction("challenge_covenant", [covenant.id], "Challenge", "Challenge transaction finalized. Source inspection is processing.", BigInt(covenant.challenge_bond_atto));
  }

  if (!configured) return <section className="page-shell"><div className="deployment-note"><strong>Registry not configured.</strong><span>Deploy Driftlock first, then set NEXT_PUBLIC_REGISTRY_ADDRESS.</span></div></section>;
  if (!covenant) return <section className="page-shell"><div className="loading-panel">Reading finalized covenant state…</div></section>;
  const stage = activeStage(covenant);
  const canExpireBaseline = baselineExpiryAvailable(covenant);
  const expirableChallenges = challenges.filter((challenge) => challengeExpiryAvailable(challenge));

  return <section className="page-shell detail-page">
    <div className="detail-hero"><div><div className="detail-topline"><StatusPill status={covenant.status}/><span>{covenant.id}</span></div><h1>{covenant.title}</h1><blockquote>{covenant.protected_promise}</blockquote></div><aside className="stake-panel"><small>STAKE LOCKED</small><strong>{attoToGen(covenant.remaining_stake_atto)} <i>GEN</i></strong><dl><div><dt>Owner</dt><dd>{shorten(covenant.owner)}</dd></div><div><dt>Beneficiary</dt><dd>{shorten(covenant.beneficiary)}</dd></div><div><dt>Finder reward</dt><dd>{Number(covenant.finder_reward_bps)/100}%</dd></div><div><dt>Expiry</dt><dd>{timeLabel(covenant.expires_at)}</dd></div></dl></aside></div>

    <div className="lifecycle-rail">{stages.map((label, i) => <div key={label} className={`life-step ${i < stage ? "past" : i === stage ? "current" : "future"}`}><span>{String(i+1).padStart(2,"0")}</span><i/><b>{label}</b></div>)}</div>

    <div className="detail-grid">
      <div>
        <section className="detail-block"><span className="mono-label">IMMUTABLE COVENANT</span><div className="rule-grid"><div><small>SUBJECT</small><p>{covenant.subject}</p></div><div><small>BREACH RULE</small><p>{covenant.breach_rule}</p></div><div><small>PERMITTED CHANGES</small><p>{covenant.permitted_changes}</p></div><div><small>CANONICAL SOURCE</small><a href={covenant.canonical_url} target="_blank" rel="noreferrer">{covenant.canonical_url}<ExternalLink size={13}/></a></div></div></section>

        <section className="compare-section"><div className="compare-head"><span className="mono-label">BASELINE / CURRENT</span><h2>Same source.<br/><em>Different moment.</em></h2></div><div className="compare-grid"><article><header><LockKeyhole size={15}/> BASELINE</header><blockquote>{covenant.protected_promise}</blockquote><footer><StatusPill status={String(covenant.baseline_review?.status || "PENDING")}/><span>{String(covenant.baseline_review?.basis || "Awaiting finalized baseline consensus.")}</span>{covenant.baseline_review && <span className="semantic-facts">Baseline compliant: {covenant.baseline_review.baseline_compliant === true ? "Yes" : "No"} · Breach condition present: {covenant.baseline_review.breach_condition_present === true ? "Yes" : "No"}</span>}</footer></article><article className={covenant.last_inspection?.status === "MATERIAL_CHANGE" ? "changed" : ""}><header><ScanLine size={15}/> CURRENT</header><blockquote>{covenant.last_inspection?.basis || "No finalized current inspection has been recorded yet."}</blockquote><footer>{covenant.last_inspection ? <><StatusPill status={String(covenant.last_inspection.status)}/><span className="semantic-facts">Current compliant: {covenant.last_inspection.current_compliant === true ? "Yes" : "No"} · Breach condition supported now: {covenant.last_inspection.breach_condition_now_supported === true ? "Yes" : "No"}</span></> : <span className="muted-copy">UNCHALLENGED</span>}</footer></article></div></section>

        <section className="challenge-history"><div className="section-mini-head"><span className="mono-label">CHALLENGE HISTORY / {challenges.length}</span><h2>Every inspection leaves a trace.</h2></div>{!challenges.length && <div className="empty-editorial">No finalized or pending challenges yet.</div>}{challenges.map((h) => <article key={h.id} className="history-row"><div><StatusPill status={h.status}/><strong>{h.id}</strong></div><p>{String(h.judgment?.basis || h.inspection?.basis || "Consensus in progress.")}</p><span>{isoLabel(h.created_at)}</span></article>)}</section>
      </div>

      <aside className="challenge-aside"><div className="challenge-card"><ShieldAlert size={22}/><span className="mono-label">CHALLENGE THE CURRENT PROMISE</span><h3>Inspect the same canonical source again.</h3><p>You do not submit evidence. Driftlock refetches the URL frozen at covenant creation and lets GenLayer decide what changed.</p><div className="bond-line"><span>Challenge bond</span><strong>{attoToGen(covenant.challenge_bond_atto)} GEN</strong></div>{!wallet.connected ? <button className="action-button" onClick={() => void wallet.connect()}>Connect wallet</button> : <button className="action-button" disabled={!covenant.can_challenge || busy} onClick={challenge}>{busy ? "Resolving…" : covenant.can_challenge ? "Inspect current promise" : "Challenge unavailable"}</button>}
        {wallet.connected && (canExpireBaseline || covenant.can_expire || (covenant.status === "BASELINE_RETRYABLE" && !covenant.can_expire && sameWallet(wallet.address, covenant.owner)) || expirableChallenges.length > 0) && <div className="recovery-actions"><span className="mono-label">LIFECYCLE ACTIONS</span>
          {canExpireBaseline && <button className="action-button" disabled={busy} onClick={() => void writeAction("expire_baseline", [covenant.id], "Baseline expiry", "Baseline timeout finalized and covenant state was updated.")}>Expire baseline attempt</button>}
          {covenant.status === "BASELINE_RETRYABLE" && !covenant.can_expire && sameWallet(wallet.address, covenant.owner) && <button className="action-button" disabled={busy} onClick={() => void writeAction("retry_baseline", [covenant.id], "Baseline retry", "Baseline retry transaction finalized. Source verification is processing.")}>Retry baseline verification</button>}
          {covenant.can_expire && <button className="action-button" disabled={busy} onClick={() => void writeAction("expire_covenant", [covenant.id], "Covenant expiry", "Covenant expired and remaining stake was credited to the owner.")}>Expire covenant</button>}
          {expirableChallenges.map((item) => <button key={item.id} className="action-button" disabled={busy} onClick={() => void writeAction("expire_challenge", [item.id], "Challenge expiry", "Timed-out challenge expired and its bond was credited back to the challenger.")}>Expire timed-out challenge {item.id}</button>)}
        </div>}
        {tx && <a className="tx-proof" href={`${EXPLORER_URL}/tx/${tx}`} target="_blank" rel="noreferrer">View submitted transaction ↗</a>}</div></aside>
    </div>
  </section>;
}
