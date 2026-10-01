"use client";

import { useState } from "react";
import { AlertTriangle, Check, Unplug } from "lucide-react";
import { useInjectedWallet } from "@/lib/wallet";
import { shorten } from "@/lib/format";

export function WalletButton() {
  const wallet = useInjectedWallet();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function act(action: () => Promise<unknown>) {
    setBusy(true); setError("");
    try { await action(); }
    catch (e) { setError(e instanceof Error ? e.message : String(e)); }
    finally { setBusy(false); }
  }

  if (!wallet.ready) return <button className="wallet-control muted" disabled>Wallet</button>;
  if (!wallet.connected) {
    return <div className="wallet-wrap"><button className="wallet-control" disabled={busy} onClick={() => void act(wallet.connect)}>{busy ? "Connecting" : "Connect wallet"}</button>{error && <span className="wallet-error">{error}</span>}</div>;
  }
  if (!wallet.correctNetwork) {
    return <div className="wallet-wrap"><button className="wallet-control signal" disabled={busy} onClick={() => void act(wallet.switchNetwork)}><AlertTriangle size={14}/> Switch to 61999</button>{error && <span className="wallet-error">{error}</span>}</div>;
  }
  return <div className="wallet-cluster"><span className="wallet-address"><Check size={12}/>{shorten(wallet.address)}</span><button className="wallet-disconnect" onClick={wallet.disconnect} aria-label="Disconnect wallet"><Unplug size={14}/></button></div>;
}
