"use client";

import { motion, useReducedMotion } from "motion/react";
import { CheckCheck, Database, Globe2, Scale, WalletCards } from "lucide-react";

const nodes = [
  [Globe2, "PUBLIC SOURCE", "The canonical HTTPS URL is frozen at activation. Challenges re-fetch this source, not challenger-supplied evidence."],
  [Database, "SOURCE INSPECTOR", "Validators independently inspect whether the same source materially changed. Unavailability is never breach evidence."],
  [CheckCheck, "VERIFIED CHANGE", "Only a finalized material-change result crosses the trust boundary into breach adjudication. Ambiguity stops here."],
  [Scale, "BREACH JUDGE", "A second independent semantic question asks whether that verified change violates the immutable covenant rule."],
  [WalletCards, "REGISTRY SETTLEMENT", "Deterministic escrow, credits, expiry, challenge bonds and the conservation invariant settle the finalized result exactly once."],
] as const;

export default function ProtocolPage() {
  const reduce = useReducedMotion();

  return <section className="protocol-page">
    <div className="protocol-hero">
      <span className="mono-label">PROTOCOL / TRUST BOUNDARIES</span>
      <h1>One source.<br/>Two semantic gates.<br/><em>Zero operator verdicts.</em></h1>
      <p>Driftlock separates observation from consequence. Source inspection must finalize before breach judgment can begin, and deterministic Registry settlement only follows those consensus results.</p>
    </div>
    <div className="protocol-flow">
      {nodes.map(([Icon, title, copy], i) => <motion.article
        key={title}
        initial={reduce ? false : { opacity: 0, y: 24, filter: "blur(6px)" }}
        whileInView={{ opacity: 1, y: 0, filter: "blur(0px)" }}
        viewport={{ once: true, amount: .42 }}
        transition={{ duration: reduce ? 0 : .52, ease: [0.16, 1, 0.3, 1] }}
      >
        <div className="protocol-no">0{i+1}</div>
        <Icon/>
        <div><h2>{title}</h2><p>{copy}</p></div>
        {i < nodes.length-1 && <span className="vertical-line" aria-hidden="true"><motion.span initial={reduce ? false : { scaleY: 0 }} whileInView={{ scaleY: 1 }} viewport={{ once: true, amount: .5 }} transition={{ duration: reduce ? 0 : .75, delay: reduce ? 0 : .12 }}/></span>}
      </motion.article>)}
    </div>
    <div className="principle-grid">
      <article><span>FAIL CLOSED</span><h3>Unknown stays unknown.</h3><p>Source failure, ambiguity and inconclusive judgment refund the challenger rather than manufacturing a breach.</p></article>
      <article><span>IMMUTABLE TERMS</span><h3>The owner cannot move the goalposts.</h3><p>Source, promise, rule, beneficiary and reward parameters freeze once the baseline activates.</p></article>
      <article><span>BOUNDED HISTORY</span><h3>No endless semantic context.</h3><p>Each covenant has a hard lifetime challenge cap. Reads are paginated and prompts never consume cumulative challenge history.</p></article>
      <article><span>PULL ACCOUNTING</span><h3>Settlement survives transfer failure.</h3><p>Credits exist before withdrawals, while deposited value remains equal to escrow plus claimable plus withdrawn.</p></article>
    </div>
  </section>;
}
