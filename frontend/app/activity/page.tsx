"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowUpRight, Coins } from "lucide-react";
import { toast } from "sonner";
import { getCredit, listWalletChallenges, protocolConfigured, submitWrite, waitForFinalization } from "@/lib/protocol";
import type { Challenge } from "@/lib/types";
import { attoToGen, isoLabel } from "@/lib/format";
import { useInjectedWallet } from "@/lib/wallet";
import { StatusPill } from "@/components/StatusPill";

export default function ActivityPage() {
  const wallet = useInjectedWallet();
  const [credit, setCredit] = useState("0");
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [busy, setBusy] = useState(false);
  const configured = protocolConfigured();

  async function refresh() {
    if (!configured || !wallet.address) return;
    const [c, hs] = await Promise.all([getCredit(wallet.address, true), listWalletChallenges(wallet.address, 0, 24, true)]);
    setCredit(c); setChallenges(hs.items.slice().reverse());
  }
  useEffect(() => { void refresh(); }, [wallet.address, configured]); // eslint-disable-line react-hooks/exhaustive-deps

  async function withdraw() {
    if (!wallet.address) return;
    setBusy(true);
    try {
      const hash = await submitWrite(wallet.address, "withdraw_credit", [wallet.address]);
      toast("Withdrawal submitted", { description: "Waiting for finality." });
      await waitForFinalization(hash); toast.success("Withdrawal finalized"); await refresh();
    } catch (e) { toast.error(e instanceof Error ? e.message : String(e)); }
    finally { setBusy(false); }
  }

  return <section className="page-shell activity-page">
    <div className="page-intro"><span className="mono-label">WALLET LEDGER / FINALIZED STATE</span><h1>Your stake.<br/><em>Your traces.</em></h1><p>Challenge history and claimable GEN read directly from DriftRegistry.</p></div>
    {!configured && <div className="deployment-note"><strong>Protocol address not configured.</strong><span>Wallet ledger activates after deployment.</span></div>}
    {!wallet.connected ? <div className="connect-stage"><Coins size={36}/><h2>Connect a wallet to open your ledger.</h2><button className="cta light" onClick={() => void wallet.connect()}>Connect wallet</button></div> : <div className="activity-layout"><aside className="credit-panel"><span className="mono-label">AVAILABLE CREDIT</span><strong>{attoToGen(credit, 6)}<i> GEN</i></strong><p>Credits are pull-based. Settlement records what you can claim before any transfer is attempted.</p><button disabled={busy || BigInt(credit) === 0n} onClick={() => void withdraw()}>{busy ? "Withdrawing…" : "Withdraw credit"}</button></aside><div className="wallet-history"><div className="section-mini-head"><span className="mono-label">MY CHALLENGES / {challenges.length}</span><h2>Inspection history.</h2></div>{!challenges.length && <div className="empty-editorial">No challenges from this wallet yet.</div>}{challenges.map((h) => <Link key={h.id} href={`/covenants/${h.covenant_id}`} className="activity-row"><div><StatusPill status={h.status}/><strong>{h.id}</strong></div><span>{h.covenant_id}</span><time>{isoLabel(h.created_at)}</time><ArrowUpRight/></Link>)}</div></div>}
  </section>;
}
