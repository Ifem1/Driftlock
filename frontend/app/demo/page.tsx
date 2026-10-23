"use client";

import { EXPLORER_URL } from "@/lib/wallet";
import { PROTOCOL_VERSION } from "@/lib/protocol";
import deployment from "../../../deployments/studionet.json";

const components = [
  ["DRIFT REGISTRY", deployment.contracts.registry.address, deployment.contracts.registry.txHash],
  ["SOURCE INSPECTOR", deployment.contracts.inspector.address, deployment.contracts.inspector.txHash],
  ["BREACH JUDGE", deployment.contracts.judge.address, deployment.contracts.judge.txHash],
];
const bindingTx = deployment.contracts.configureTxHash;

export default function DemoPage() {
  return <section className="page-shell demo-page"><div className="page-intro"><span className="mono-label">STUDIONET / DEPLOYMENT EVIDENCE</span><h1>Deployed protocol.<br/><em>Public evidence.</em></h1><p>These addresses come from the active deployment manifest. They identify the {PROTOCOL_VERSION === 2 ? "V2" : "historical V1"} Studionet components and their recorded binding.</p></div>
    <div className="evidence-status"><span className="proof-dot live"/><div><strong>Studionet {PROTOCOL_VERSION === 2 ? "V2" : "V1"} deployment · Chain 61999</strong><p>{PROTOCOL_VERSION === 2 ? "V2 commits bounded rendered-text evidence and allows one bonded appeal. Review the repository live-verification record for lifecycle receipts." : "These finalized deployment receipts belong to V1. No V2 deployment or lifecycle transaction is claimed by this page."}</p></div></div>
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
