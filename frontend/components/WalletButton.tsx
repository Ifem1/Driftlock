"use client";

import { useState } from "react";
import { AlertTriangle, Check, Copy, Unplug } from "lucide-react";
import { toast } from "sonner";
import { copyWalletAddress, useInjectedWallet } from "@/lib/wallet";
import { shorten } from "@/lib/format";

export function WalletButton() {
  const wallet = useInjectedWallet();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  async function act(action: () => Promise<unknown>) {
    setBusy(true); setError("");
    try { await action(); }
    catch (e) { setError(e instanceof Error ? e.message : String(e)); }
    finally { setBusy(false); }
  }

  async function copyAddress() {
    if (!wallet.address) return;
    setError("");
    try {
      await copyWalletAddress(wallet.address);
      setCopied(true);
      toast.success("Address copied");
      window.setTimeout(() => setCopied(false), 1600);
    } catch (e) {
      const message = e instanceof Error ? e.message : String(e);
      setError(message);
      toast.error(message);
    }
  }

  if (!wallet.ready) return <button className="wallet-control muted" disabled>Wallet</button>;
  if (!wallet.connected) {
    return <div className="wallet-wrap"><button className="wallet-control" disabled={busy} onClick={() => void act(wallet.connect)}>{busy ? "Connecting" : "Connect wallet"}</button>{error && <span className="wallet-error">{error}</span>}</div>;
  }
  if (!wallet.correctNetwork) {
    return <div className="wallet-wrap"><button className="wallet-control signal" disabled={busy} onClick={() => void act(wallet.switchNetwork)}><AlertTriangle size={14}/> Switch to 61999</button>{error && <span className="wallet-error">{error}</span>}</div>;
  }
  return <div className="wallet-wrap">
    <div className="wallet-cluster">
      <button className="wallet-address" onClick={() => void copyAddress()} aria-label="Copy connected wallet address" title="Copy full address">
        <span className="wallet-status-dot"/><span>{shorten(wallet.address)}</span>{copied ? <Check size={12}/> : <Copy size={12}/>}
      </button>
      <button className="wallet-disconnect" onClick={wallet.disconnect} aria-label="Disconnect wallet" title="Disconnect wallet"><Unplug size={14}/></button>
    </div>
    {error && <span className="wallet-error">{error}</span>}
  </div>;
}
