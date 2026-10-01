"use client";

import Link from "next/link";
import { motion, useReducedMotion, useScroll, useTransform } from "motion/react";
import { ArrowDownRight, ArrowRight, LockKeyhole, ScanLine, ShieldCheck } from "lucide-react";
import { useRef } from "react";

const stages = [
  ["01", "Baseline verified", "The canonical page supports the exact promise before any stake-backed covenant becomes active."],
  ["02", "Source changes", "A later challenge re-fetches that same immutable URL. The challenger cannot swap in a friendlier source."],
  ["03", "Breach judged", "Only a verified material change reaches the independent breach stage and settlement."],
] as const;

export function HomeExperience() {
  const reduce = useReducedMotion();
  const story = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: story, offset: ["start start", "end end"] });
  const currentY = useTransform(scrollYProgress, [0.18, 0.48, 0.72], reduce ? [0, 0, 0] : [84, 8, -28]);
  const baselineOpacity = useTransform(scrollYProgress, [0, .16, .72], [.4, 1, 1]);
  const changeOpacity = useTransform(scrollYProgress, [.32, .5], [0, 1]);
  const breachOpacity = useTransform(scrollYProgress, [.62, .82], [0, 1]);

  return <>
    <section className="home-hero">
      <div className="hero-kicker"><span>GENLAYER / STAKE-BACKED COVENANTS</span><span>01 — 04</span></div>
      <motion.h1 initial={{ opacity: 0, y: 36 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .9, ease: [0.16, 1, 0.3, 1] }}>
        PUBLIC WORDS <span>CHANGE.</span><br/>YOUR AGREEMENT <em>SHOULDN&apos;T.</em>
      </motion.h1>
      <div className="hero-lower">
        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: .35, duration: .7 }}>Lock an already-verifiable public promise behind GEN. If that same source materially changes later, GenLayer independently determines whether the covenant was breached.</motion.p>
        <div className="hero-ctas"><Link href="/create" className="cta primary">Create covenant <ArrowRight size={16}/></Link><Link href="/covenants" className="cta ghost">Watch live covenants</Link></div>
        <div className="scroll-cue"><ArrowDownRight size={18}/><span>Scroll to inspect the protocol</span></div>
      </div>
    </section>

    <section className="story-shell" ref={story}>
      <div className="story-sticky">
        <div className="story-copy">
          <span className="mono-label">ONE URL. TWO MOMENTS. ONE FROZEN RULE.</span>
          <h2>The promise stays still.<br/><i>The world moves around it.</i></h2>
          <p>Driftlock does not ask challengers to bring evidence. It re-opens the covenant&apos;s own canonical source and compares the present against the promise that was verified at creation.</p>
          <div className="story-states">
            <motion.span style={{ opacity: baselineOpacity }}>BASELINE LOCKED</motion.span>
            <motion.span className="warning" style={{ opacity: changeOpacity }}>CHANGE DETECTED</motion.span>
            <motion.span className="signal" style={{ opacity: breachOpacity }}>BREACH CONFIRMED</motion.span>
          </div>
        </div>
        <div className="document-stage" aria-label="Illustrative promise comparison">
          <motion.article className="document-card baseline-doc" style={{ opacity: baselineOpacity }}>
            <div className="doc-top"><span>BASELINE / POLICY</span><LockKeyhole size={15}/></div>
            <div className="doc-lines"><i/><i/><i/><i/></div>
            <blockquote>Customer information is <b>not sold, licensed or commercially transferred</b> to third parties.</blockquote>
            <div className="doc-foot"><span>CANONICAL SOURCE</span><strong>VERIFIED</strong></div>
          </motion.article>
          <motion.article className="document-card current-doc" style={{ y: currentY }}>
            <div className="doc-top"><span>CURRENT / SAME URL</span><ScanLine size={15}/></div>
            <div className="doc-lines"><i/><i/><i/></div>
            <blockquote>Customer information <motion.b style={{ opacity: changeOpacity }}>may be licensed to selected commercial partners.</motion.b></blockquote>
            <div className="change-mark">MATERIAL CHANGE</div>
          </motion.article>
          <motion.div className="breach-stamp" style={{ opacity: breachOpacity, scale: breachOpacity }}>BREACH<br/>CONFIRMED</motion.div>
        </div>
      </div>
    </section>

    <section className="home-section principle-section">
      <div className="section-number">02 / MECHANISM</div>
      <div className="section-headline"><h2>Consensus is not decoration.<br/>It is the enforcement layer.</h2><p>Remove GenLayer and the protocol loses its ability to verify a live public source and make a settlement-driving semantic judgment.</p></div>
      <div className="stage-list">
        {stages.map(([n, title, copy], index) => <motion.article key={n} initial={{ opacity: 0, y: 22 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: .35 }} transition={{ delay: index * .08 }}><span>{n}</span><h3>{title}</h3><p>{copy}</p></motion.article>)}
      </div>
    </section>

    <section className="home-section architecture-section">
      <div className="architecture-title"><span className="mono-label">THREE RESPONSIBILITIES / NO OPERATOR OVERRIDE</span><h2>A change must survive<br/><em>two different questions.</em></h2></div>
      <div className="architecture-flow">
        <div className="flow-node"><small>01</small><ShieldCheck/><strong>DriftRegistry</strong><p>Escrow, deadlines, immutable terms, accounting and settlement.</p></div>
        <div className="flow-arrow">→</div>
        <div className="flow-node"><small>02</small><ScanLine/><strong>SourceInspector</strong><p>Did the same public source materially change?</p></div>
        <div className="flow-arrow">→</div>
        <div className="flow-node signal-node"><small>03</small><LockKeyhole/><strong>BreachJudge</strong><p>Does that verified change violate the frozen covenant?</p></div>
      </div>
      <div className="architecture-actions"><Link href="/protocol" className="text-link">Read the protocol <ArrowRight size={14}/></Link><Link href="/demo" className="text-link">Review live proof <ArrowRight size={14}/></Link></div>
    </section>

    <section className="closing-cta">
      <span className="mono-label">MAKE THE PROMISE EXPENSIVE TO BREAK</span>
      <h2>Put public words<br/>under <em>stake.</em></h2>
      <Link href="/create" className="cta light">Create covenant <ArrowRight size={17}/></Link>
    </section>
  </>;
}
