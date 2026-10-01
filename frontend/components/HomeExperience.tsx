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
  const { scrollY } = useScroll();
  const { scrollYProgress } = useScroll({ target: story, offset: ["start start", "end end"] });
  const heroKickerY = useTransform(scrollY, [0, 600], reduce ? [0, 0] : [0, -3]);
  const heroHeadingY = useTransform(scrollY, [0, 600], reduce ? [0, 0] : [0, -6]);
  const heroLowerY = useTransform(scrollY, [0, 600], reduce ? [0, 0] : [0, -4]);
  const heroGlowY = useTransform(scrollY, [0, 700], reduce ? [0, 0] : [0, 18]);
  const heroGlowX = useTransform(scrollY, [0, 700], reduce ? [0, 0] : [0, -8]);
  const currentY = useTransform(scrollYProgress, [0.14, 0.48, 0.78], reduce ? [0, 0, 0] : [76, 4, -30]);
  const currentX = useTransform(scrollYProgress, [0.18, 0.6], reduce ? [0, 0] : [18, -8]);
  const baselineOpacity = useTransform(scrollYProgress, [0, .16, .72], [.5, 1, 1]);
  const sourceOpacity = useTransform(scrollYProgress, [.18, .36], [0, 1]);
  const changeOpacity = useTransform(scrollYProgress, [.38, .56], [0, 1]);
  const breachOpacity = useTransform(scrollYProgress, [.62, .82], [0, 1]);

  return <>
    <section className="home-hero">
      <motion.div className="hero-parallax-glow" style={{ y: heroGlowY, x: heroGlowX }} aria-hidden="true"/>
      <motion.div className="hero-kicker" style={{ y: heroKickerY }}><span>GENLAYER / STAKE-BACKED COVENANTS</span><span>01 — 04</span></motion.div>
      <motion.h1 style={{ y: heroHeadingY }} aria-label="Public words change. Your agreement shouldn't.">
        <span className="hero-line-mask">
          <motion.span
            className="hero-line"
            initial={reduce ? false : { y: "110%", opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: reduce ? 0 : .82, ease: [0.16, 1, 0.3, 1] }}
          >
            PUBLIC WORDS{" "}
            <motion.span
              className="hero-change"
              animate={reduce ? undefined : { y: [0, -3, 1, 0], opacity: [.68, 1, .78, .68] }}
              transition={{ duration: 5.2, repeat: Infinity, ease: "easeInOut" }}
            >CHANGE.</motion.span>
          </motion.span>
        </span>
        <span className="hero-line-mask">
          <motion.span
            className="hero-line"
            initial={reduce ? false : { y: "110%", opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: reduce ? 0 : .88, delay: reduce ? 0 : .12, ease: [0.16, 1, 0.3, 1] }}
          >
            YOUR AGREEMENT{" "}
            <motion.em
              className="hero-shouldnt"
              animate={reduce ? undefined : { backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"] }}
              transition={{ duration: 7.5, repeat: Infinity, ease: "linear" }}
            >SHOULDN&apos;T.</motion.em>
          </motion.span>
        </span>
      </motion.h1>
      <motion.div className="hero-lower" style={{ y: heroLowerY }}>
        <motion.p initial={reduce ? false : { opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: reduce ? 0 : .38, duration: .62 }}>
          Lock an already-verifiable public promise behind GEN. If that same source materially changes later, GenLayer independently determines whether the covenant was breached.
        </motion.p>
        <motion.div className="hero-ctas" initial={reduce ? false : { opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: reduce ? 0 : .46, duration: .62 }}>
          <Link href="/create" className="cta primary">Create covenant <ArrowRight size={16}/></Link>
          <Link href="/covenants" className="cta ghost">Watch live covenants</Link>
        </motion.div>
        <div className="scroll-cue"><ArrowDownRight size={18}/><span>Scroll to inspect the protocol</span></div>
      </motion.div>
    </section>

    <section className="story-shell" ref={story}>
      <div className="story-sticky">
        <div className="story-copy">
          <span className="mono-label">ONE URL. TWO MOMENTS. ONE FROZEN RULE.</span>
          <h2>The promise stays still.<br/><i>The world moves around it.</i></h2>
          <p>Driftlock does not ask challengers to bring evidence. It re-opens the covenant&apos;s own canonical source and compares the present against the promise that was verified at creation.</p>
          <div className="story-states" aria-label="Covenant transition">
            <motion.span style={{ opacity: baselineOpacity }}>BASELINE LOCKED</motion.span>
            <motion.span className="source" style={{ opacity: sourceOpacity }}>SOURCE MOVES</motion.span>
            <motion.span className="warning material" style={{ opacity: changeOpacity }}>MATERIAL CHANGE</motion.span>
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
          <motion.article className="document-card current-doc" style={{ y: currentY, x: currentX }}>
            <div className="doc-top"><span>CURRENT / SAME URL</span><ScanLine size={15}/></div>
            <div className="doc-lines"><i/><i/><i/></div>
            <blockquote>Customer information <motion.b style={{ opacity: changeOpacity }}>may be licensed to selected commercial partners.</motion.b></blockquote>
            <motion.div className="change-mark" style={{ opacity: changeOpacity }}>MATERIAL CHANGE</motion.div>
          </motion.article>
          <motion.div className="breach-stamp" style={{ opacity: breachOpacity, scale: breachOpacity }}>BREACH<br/>CONFIRMED</motion.div>
        </div>
      </div>
    </section>

    <section className="home-section principle-section">
      <div className="section-number">02 / MECHANISM</div>
      <div className="section-headline"><h2>Consensus is not decoration.<br/>It is the enforcement layer.</h2><p>Remove GenLayer and the protocol loses its ability to verify a live public source and make a settlement-driving semantic judgment.</p></div>
      <div className="stage-list">
        {stages.map(([n, title, copy], index) => <motion.article key={n} initial={reduce ? false : { opacity: 0, y: 22, filter: "blur(5px)" }} whileInView={{ opacity: 1, y: 0, filter: "blur(0px)" }} viewport={{ once: true, amount: .35 }} transition={{ delay: reduce ? 0 : index * .08, duration: .5 }}><span>{n}</span><h3>{title}</h3><p>{copy}</p></motion.article>)}
      </div>
    </section>

    <section className="home-section architecture-section">
      <div className="architecture-title"><span className="mono-label">THREE RESPONSIBILITIES / NO OPERATOR OVERRIDE</span><h2>A change must survive<br/><em>two different questions.</em></h2></div>
      <div className="architecture-flow">
        <motion.div className="flow-node" initial={reduce ? false : { opacity: 0, y: 18 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: .4 }}><small>01</small><ShieldCheck/><strong>DriftRegistry</strong><p>Escrow, deadlines, immutable terms, accounting and settlement.</p></motion.div>
        <div className="flow-arrow">→</div>
        <motion.div className="flow-node" initial={reduce ? false : { opacity: 0, y: 18 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: .4 }} transition={{ delay: reduce ? 0 : .08 }}><small>02</small><ScanLine/><strong>SourceInspector</strong><p>Did the same public source materially change?</p></motion.div>
        <div className="flow-arrow">→</div>
        <motion.div className="flow-node signal-node" initial={reduce ? false : { opacity: 0, y: 18 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: .4 }} transition={{ delay: reduce ? 0 : .16 }}><small>03</small><LockKeyhole/><strong>BreachJudge</strong><p>Does that verified change violate the frozen covenant?</p></motion.div>
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
