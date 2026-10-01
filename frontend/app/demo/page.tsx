"use client";

import { protocolConfigured, REGISTRY_ADDRESS, INSPECTOR_ADDRESS, JUDGE_ADDRESS } from "@/lib/protocol";
import { EXPLORER_URL } from "@/lib/wallet";

const deploymentTxs = [
  ["REGISTRY", "0xa61bcf245944be3c2bb5be42d847f0f53e9292c3f04390f00c2414c811d23c73"],
  ["SOURCE INSPECTOR", "0x2050636fe00199dabffbe07419651bd42cb4f9b5104051b2662feca7bb5a6945"],
  ["BREACH JUDGE", "0x20c9798fe26b2a7d9ee79a53e4d3b6e25a0dd0be269a360869141df70f9c23a0"],
  ["COMPONENT BINDING", "0xd3498a192d0548cbc4e695657a22a4f338b1deb72051b0af9104d81dbf153d3c"],
];

export default function DemoPage() {
  const configured = protocolConfigured();
  return <section className="page-shell demo-page"><div className="page-intro"><span className="mono-label">REVIEWER EVIDENCE / DO NOT TRUST CLAIMS</span><h1>Live proof,<br/><em>not theatre.</em></h1><p>This page is intentionally evidence-first. Codex should populate it only from finalized Studionet transactions and public source commits.</p></div>
    <div className="evidence-status"><span className={configured ? "proof-dot live" : "proof-dot"}/><div><strong>{configured ? "Deployment configuration detected" : "Awaiting live deployment"}</strong><p>{configured ? "Addresses are configured. Final transaction evidence still belongs in docs/REVIEW_EVIDENCE.md and this page after manual verification." : "The starter does not invent transaction hashes, contract addresses or live outcomes. Those must be created and verified during final deployment."}</p></div></div>
    <div className="proof-grid"><article><small>REGISTRY</small><strong>{REGISTRY_ADDRESS || "NOT YET DEPLOYED"}</strong></article><article><small>SOURCE INSPECTOR</small><strong>{INSPECTOR_ADDRESS || "NOT YET DEPLOYED"}</strong></article><article><small>BREACH JUDGE</small><strong>{JUDGE_ADDRESS || "NOT YET DEPLOYED"}</strong></article></div>
    <div className="proof-grid">{deploymentTxs.map(([name, hash]) => <article key={name}><small>{name} / FINALIZED</small><a className="tx-proof" href={`${EXPLORER_URL}/tx/${hash}`} target="_blank" rel="noreferrer">{hash.slice(0, 14)}… ↗</a></article>)}</div>
    <div className="proof-sequence">{[
      ["01", "Baseline", "Create a covenant against demo-source/public-promise.txt and record finalized BASELINE_VERIFIED state."],
      ["02", "Unchanged challenge", "Challenge the unchanged source and preserve finalized NO_RELEVANT_CHANGE evidence."],
      ["03", "Public source commit", "Change the same file at the same URL through a visible Git commit. Keep before and after SHAs."],
      ["04", "Breach challenge", "Challenge again. Record MATERIAL_CHANGE, BREACH, credits and exact settlement."],
      ["05", "Withdrawal", "Withdraw finder and beneficiary credits and prove the accounting invariant remains balanced."],
    ].map(([n,t,c]) => <article key={n}><span>{n}</span><h2>{t}</h2><p>{c}</p><b>VERIFIED ONLY AFTER LIVE RUN</b></article>)}</div>
  </section>;
}
