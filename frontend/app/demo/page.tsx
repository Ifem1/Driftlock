"use client";

import { EXPLORER_URL } from "@/lib/wallet";

const components = [
  ["DRIFT REGISTRY", "0xDc1bDE6d262baAa6084a474570b73E724De12ddA", "0xa61bcf245944be3c2bb5be42d847f0f53e9292c3f04390f00c2414c811d23c73"],
  ["SOURCE INSPECTOR", "0xBb19613948808a9323594C0945118F10C7979585", "0x2050636fe00199dabffbe07419651bd42cb4f9b5104051b2662feca7bb5a6945"],
  ["BREACH JUDGE", "0xbb3acd8a549A3Ab5c18deC6762f9876B1E13bfaf", "0x20c9798fe26b2a7d9ee79a53e4d3b6e25a0dd0be269a360869141df70f9c23a0"],
];
const bindingTx = "0xd3498a192d0548cbc4e695657a22a4f338b1deb72051b0af9104d81dbf153d3c";

export default function DemoPage() {
  return <section className="page-shell demo-page"><div className="page-intro"><span className="mono-label">STUDIONET / DEPLOYMENT EVIDENCE</span><h1>Deployed protocol.<br/><em>Public evidence.</em></h1><p>Driftlock is deployed on GenLayer Studionet. The addresses and finalized transactions below identify the live components and their one-time binding.</p></div>
    <div className="evidence-status"><span className="proof-dot live"/><div><strong>Studionet deployment verified · Chain 61999</strong><p>GenLayer validators independently re-evaluate each covenant against the same frozen canonical URL. The protocol does not claim a permanent archive or diff of every later fetched webpage.</p></div></div>
    <div className="proof-grid">{components.map(([name, address, hash]) => <article key={name}><small>{name} / CHAIN 61999</small><strong>{address}</strong><a className="tx-proof" href={`${EXPLORER_URL}/tx/${hash}`} target="_blank" rel="noreferrer">Finalized deployment transaction ↗</a></article>)}</div>
    <div className="proof-grid"><article><small>ONE-TIME COMPONENT BINDING / FINALIZED</small><a className="tx-proof" href={`${EXPLORER_URL}/tx/${bindingTx}`} target="_blank" rel="noreferrer">{bindingTx} ↗</a></article></div>
    <div className="proof-sequence">
      <article><span>01</span><h2>DriftRegistry</h2><p>Owns covenant state, challenge stages, escrow accounting and pull-credit settlement.</p></article>
      <article><span>02</span><h2>SourceInspector</h2><p>GenLayer validators independently assess the source at the covenant’s immutable canonical URL.</p></article>
      <article><span>03</span><h2>BreachJudge</h2><p>After a material change, validators independently assess whether it violates the protected promise and breach rule.</p></article>
    </div>
    <p className="field-note">Automated CI and manual injected-wallet browser verification are reported separately in the repository validation documents. This page lists deployment evidence and does not imply a complete demo-covenant lifecycle record.</p>
  </section>;
}
