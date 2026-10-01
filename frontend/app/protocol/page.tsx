"use client";

import { motion } from "motion/react";
import { Database, Globe2, Scale, WalletCards } from "lucide-react";

const nodes = [
  [Globe2, "PUBLIC SOURCE", "The canonical HTTPS URL is frozen at activation. Challenges re-fetch this source, not challenger-supplied evidence."],
  [Database, "SOURCE INSPECTOR", "Validators independently inspect whether the same source materially changed. Unavailability is never breach evidence."],
  [Scale, "BREACH JUDGE", "Only a verified material change reaches a second independent question: does the current source violate the immutable rule?"],
  [WalletCards, "REGISTRY SETTLEMENT", "Deterministic escrow, credits, expiry, challenge bonds and a conservation invariant settle the result exactly once."],
] as const;

export default function ProtocolPage() {
  return <section className="protocol-page">
    <div className="protocol-hero"><span className="mono-label">PROTOCOL / TRUST BOUNDARIES</span><h1>One source.<br/>Two semantic gates.<br/><em>Zero operator verdicts.</em></h1><p>Driftlock separates observation from consequence. The first consensus asks what changed. The second asks whether that verified change actually violates the covenant.</p></div>
    <div className="protocol-flow">{nodes.map(([Icon, title, copy], i) => <motion.article key={title} initial={{ opacity: 0, x: i%2 ? 30 : -30 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true, amount: .4 }}><div className="protocol-no">0{i+1}</div><Icon/><div><h2>{title}</h2><p>{copy}</p></div>{i < nodes.length-1 && <span className="vertical-line"/>}</motion.article>)}</div>
    <div className="principle-grid"><article><span>FAIL CLOSED</span><h3>Unknown stays unknown.</h3><p>Source failure, ambiguity and inconclusive judgment refund the challenger rather than manufacturing a breach.</p></article><article><span>IMMUTABLE TERMS</span><h3>The owner cannot move the goalposts.</h3><p>Source, promise, rule, beneficiary and reward parameters freeze once the baseline activates.</p></article><article><span>BOUNDED HISTORY</span><h3>No endless semantic context.</h3><p>Each covenant has a hard lifetime challenge cap. Reads are paginated and prompts never consume cumulative challenge history.</p></article><article><span>PULL ACCOUNTING</span><h3>Settlement survives transfer failure.</h3><p>Credits exist before withdrawals, while deposited value remains equal to escrow plus claimable plus withdrawn.</p></article></div>
  </section>;
}
