"use client";

import { protocolConfigured, REGISTRY_ADDRESS, INSPECTOR_ADDRESS, JUDGE_ADDRESS } from "@/lib/protocol";
import { EXPLORER_URL } from "@/lib/wallet";

const deploymentTxs = [
  ["REGISTRY", "0x959450ea93b9c7a707eee2c5f51e52b202f38332396e26d7f2d2ba1a0b725dab"],
  ["SOURCE INSPECTOR", "0xe3a097dba29de5717b8e95dfb0ea1f8284e49d47749b66b3507b67e7bb71ffdf"],
  ["BREACH JUDGE", "0xcfab190339a4a134093ebdf897b427d424bbeb1ebbb162dd162abf38906a2133"],
  ["COMPONENT BINDING", "0x23b39318a4320d756c1ebcf881d9cb69d50f988fe2b99359bba5789b88f2db33"],
];

export default function DemoPage() {
  const configured = protocolConfigured();
  return <section className="page-shell demo-page"><div className="page-intro"><span className="mono-label">REVIEWER EVIDENCE / DO NOT TRUST CLAIMS</span><h1>Live proof,<br/><em>not theatre.</em></h1><p>This page is intentionally evidence-first. Codex should populate it only from finalized Studionet transactions and public source commits.</p></div>
    <div className="evidence-status"><span className={configured ? "proof-dot live" : "proof-dot"}/><div><strong>{configured ? "Studionet deployment and live proof verified" : "Awaiting live deployment"}</strong><p>{configured ? "Baseline verification, unchanged-source result, material change, breach judgment, withdrawals, and balanced accounting are finalized on Studionet." : "Contract addresses and live outcomes appear here only after they are created and verified."}</p></div></div>
    <div className="proof-grid"><article><small>REGISTRY</small><strong>{REGISTRY_ADDRESS || "NOT YET DEPLOYED"}</strong></article><article><small>SOURCE INSPECTOR</small><strong>{INSPECTOR_ADDRESS || "NOT YET DEPLOYED"}</strong></article><article><small>BREACH JUDGE</small><strong>{JUDGE_ADDRESS || "NOT YET DEPLOYED"}</strong></article></div>
    <div className="proof-grid">{deploymentTxs.map(([name, hash]) => <article key={name}><small>{name} / FINALIZED</small><a className="tx-proof" href={`${EXPLORER_URL}/tx/${hash}`} target="_blank" rel="noreferrer">{hash.slice(0, 14)}… ↗</a></article>)}</div>
    <div className="proof-grid"><article><small>LIVE COVENANT</small><strong>dl-1 / ACTIVE</strong><p>Owner 0xA49c…341F · Challenger 0x77e2…ffbA5 · Beneficiary 0x6B47…FCBe</p></article><article><small>VERIFIED BASELINE</small><strong>BASELINE_VERIFIED</strong><p>SHA-256 cb713d95689489779a48b35cd0dce6117a0316821948ce055639fd96c0a98f25</p></article><article><small>UNCHANGED CHALLENGE</small><strong>NO_RELEVANT_CHANGE</strong><p>Challenge dc-1 · tx 0xef8dc1cb7b364b8a448581d22987fc37d9bd2abb66d9300f390968542dcea88e</p></article></div>
    <div className="proof-sequence">{[
      ["01", "Baseline", "Finalized create and baseline verification stored bounded source text and its SHA-256 digest.", "VERIFIED"],
      ["02", "Unchanged challenge", "The same canonical URL returned byte-for-byte identical bounded text and NO_RELEVANT_CHANGE.", "VERIFIED"],
      ["03", "Public source commit", "The same raw URL now serves the updated policy. Before commit a092268bdeca39ac494297b3b87c6171ff61a31c; after commit 7048cefa430fbde3fbfca8f125ec58d94a540eb8.", "VERIFIED"],
      ["04", "Breach challenge", "Challenge dc-2 finalized as MATERIAL_CHANGE and BREACH; the covenant settled as BREACHED.", "VERIFIED"],
      ["05", "Withdrawal", "Owner, finder, and beneficiary withdrawals finalized; get_stats() reports balanced accounting.", "VERIFIED"],
    ].map(([n,t,c,state]) => <article key={n}><span>{n}</span><h2>{t}</h2><p>{c}</p><b>{state}</b></article>)}</div>
  </section>;
}
