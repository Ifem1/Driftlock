"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { AnimatePresence, motion } from "motion/react";
import { ArrowLeft, ArrowRight, Check, ExternalLink, LockKeyhole } from "lucide-react";
import { toast } from "sonner";
import { findLatestCovenantByOwner, protocolConfigured, submitWrite, waitForFinalization } from "@/lib/protocol";
import { genToAtto } from "@/lib/format";
import { useInjectedWallet, EXPLORER_URL } from "@/lib/wallet";

const labels = ["Source", "Promise", "Breach rule", "Permitted changes", "Beneficiary", "Stake", "Expiry", "Review"];

type FormState = {
  title: string; subject: string; canonicalUrl: string; promise: string; breachRule: string;
  permitted: string; beneficiary: string; stake: string; rewardPercent: string; expiryHours: string;
};

const initial: FormState = {
  title: "", subject: "", canonicalUrl: "", promise: "", breachRule: "",
  permitted: "Formatting, spelling, clarification and changes unrelated to the protected promise are permitted.",
  beneficiary: "", stake: "0.1", rewardPercent: "10", expiryHours: "168",
};

export default function CreatePage() {
  const [step, setStep] = useState(0);
  const [form, setForm] = useState<FormState>(initial);
  const [busy, setBusy] = useState(false);
  const [tx, setTx] = useState("");
  const wallet = useInjectedWallet();
  const router = useRouter();
  const configured = protocolConfigured();
  const update = (key: keyof FormState, value: string) => setForm((x) => ({ ...x, [key]: value }));
  const expiry = useMemo(() => Math.floor(Date.now()/1000) + Math.max(2, Number(form.expiryHours || 0)) * 3600, [form.expiryHours]);

  function validateStep(): string {
    if (step === 0 && (!form.title.trim() || !form.subject.trim() || !form.canonicalUrl.startsWith("https://"))) return "Add a title, subject and HTTPS canonical URL.";
    if (step === 1 && form.promise.trim().length < 12) return "Write the exact public promise you want to protect.";
    if (step === 2 && form.breachRule.trim().length < 20) return "Make the breach rule specific enough to adjudicate.";
    if (step === 3 && form.permitted.trim().length < 4) return "State what kinds of changes remain permitted.";
    if (step === 4 && !/^0x[0-9a-fA-F]{40}$/.test(form.beneficiary)) return "Enter a valid beneficiary address.";
    if (step === 5) {
      try { const amount = genToAtto(form.stake); if (amount < 10n**15n || amount > 10n*10n**18n) return "Stake must be between 0.001 and 10 test GEN."; } catch { return "Enter a valid GEN stake."; }
      const reward = Number(form.rewardPercent); if (reward < 1 || reward > 25) return "Finder reward must be between 1% and 25%.";
    }
    if (step === 6 && (Number(form.expiryHours) < 2 || Number(form.expiryHours) > 720)) return "Expiry must be between 2 and 720 hours.";
    return "";
  }

  function next() { const problem = validateStep(); if (problem) return toast.error(problem); setStep((s) => Math.min(labels.length - 1, s + 1)); }
  function back() { setStep((s) => Math.max(0, s - 1)); }

  async function submit() {
    if (!configured) return toast.error("Registry is not configured yet.");
    setBusy(true); setTx("");
    try {
      const address = wallet.address || await wallet.connect();
      if (!wallet.correctNetwork) await wallet.switchNetwork();
      const hash = await submitWrite(address, "create_covenant", [
        form.title.trim(), form.subject.trim(), form.canonicalUrl.trim(), form.promise.trim(), form.breachRule.trim(),
        form.permitted.trim(), form.beneficiary, BigInt(Math.round(Number(form.rewardPercent) * 100)), BigInt(expiry),
      ], genToAtto(form.stake));
      setTx(hash); toast("Covenant submitted", { description: "Your terms are now waiting for source-grounded baseline consensus." });
      await waitForFinalization(hash);
      toast.success("Creation transaction finalized");
      const id = await findLatestCovenantByOwner(address, true);
      if (id) router.push(`/covenants/${id}`);
    } catch (e) { toast.error(e instanceof Error ? e.message : String(e)); }
    finally { setBusy(false); }
  }

  return <section className="composer-shell">
    <div className="composer-head"><span className="mono-label">CREATE / IMMUTABLE AFTER BASELINE</span><h1>Compose the<br/><em>covenant.</em></h1><p>Each step becomes part of what GenLayer will later judge. Be precise now; active covenants cannot be silently rewritten.</p></div>
    {!configured && <div className="deployment-note composer-note"><strong>Build mode.</strong><span>The full composer is ready. Live signing becomes available after the Registry address is configured.</span></div>}
    <div className="composer-progress">{labels.map((label, i) => <button key={label} onClick={() => i < step && setStep(i)} className={i === step ? "current" : i < step ? "done" : ""}><span>{i < step ? <Check size={11}/> : String(i+1).padStart(2,"0")}</span>{label}</button>)}</div>

    <div className="composer-body"><AnimatePresence mode="wait" initial={false}>
      <motion.div key={step} className="composer-panel" initial={{ opacity: 0, y: 26, filter: "blur(8px)" }} animate={{ opacity: 1, y: 0, filter: "blur(0px)" }} exit={{ opacity: 0, y: -18, filter: "blur(5px)" }} transition={{ duration: .38, ease: [0.16,1,.3,1] }}>
        {step === 0 && <><span className="step-overline">01 / SOURCE</span><h2>What public source carries the promise?</h2><label>Short title <input maxLength={100} value={form.title} onChange={(e) => update("title", e.target.value)} placeholder="Customer data covenant"/></label><label>Subject <textarea maxLength={1200} value={form.subject} onChange={(e) => update("subject", e.target.value)} placeholder="The current customer-data handling policy of Example Company."/></label><label>Canonical HTTPS URL <input maxLength={800} value={form.canonicalUrl} onChange={(e) => update("canonicalUrl", e.target.value)} placeholder="https://example.com/privacy"/></label><p className="field-note">The URL is frozen when the covenant activates. Future challengers cannot substitute another source.</p></>}
        {step === 1 && <><span className="step-overline">02 / PROMISE</span><h2>Write the exact promise you expect to remain true.</h2><label>Protected promise <textarea className="large-input" maxLength={1800} value={form.promise} onChange={(e) => update("promise", e.target.value)} placeholder="Customer information is not sold, licensed or commercially transferred to third parties."/><small>{form.promise.length}/1800</small></label></>}
        {step === 2 && <><span className="step-overline">03 / BREACH RULE</span><h2>Define what would actually count as breaking it.</h2><label>Breach rule <textarea className="large-input" maxLength={2400} value={form.breachRule} onChange={(e) => update("breachRule", e.target.value)} placeholder="A future version that permits sale, licensing, brokerage or commercial transfer of customer information constitutes breach."/><small>{form.breachRule.length}/2400</small></label></>}
        {step === 3 && <><span className="step-overline">04 / SAFE CHANGES</span><h2>What can change without becoming a breach?</h2><label>Permitted changes <textarea className="large-input" maxLength={1600} value={form.permitted} onChange={(e) => update("permitted", e.target.value)}/><small>{form.permitted.length}/1600</small></label></>}
        {step === 4 && <><span className="step-overline">05 / BENEFICIARY</span><h2>Who receives the remaining stake after a confirmed breach?</h2><label>Beneficiary address <input value={form.beneficiary} onChange={(e) => update("beneficiary", e.target.value)} placeholder="0x…"/></label><p className="field-note">This address becomes immutable after activation. It does not need to be the covenant owner.</p></>}
        {step === 5 && <><span className="step-overline">06 / ECONOMICS</span><h2>Put value behind the promise.</h2><div className="split-fields"><label>Stake / GEN <input inputMode="decimal" value={form.stake} onChange={(e) => update("stake", e.target.value)}/></label><label>Finder reward / % <input inputMode="decimal" value={form.rewardPercent} onChange={(e) => update("rewardPercent", e.target.value)}/></label></div><p className="field-note">On confirmed breach, the finder reward goes to the challenger and the remaining stake goes to the beneficiary. Otherwise the covenant owner recovers unbreached stake at expiry.</p></>}
        {step === 6 && <><span className="step-overline">07 / EXPIRY</span><h2>How long should the promise stay under stake?</h2><label>Lifetime in hours <input inputMode="numeric" value={form.expiryHours} onChange={(e) => update("expiryHours", e.target.value)}/></label><div className="expiry-preview">Projected expiry <strong>{new Date(expiry * 1000).toUTCString()}</strong></div></>}
        {step === 7 && <><span className="step-overline">08 / REVIEW</span><h2>These terms are about to lock.</h2><div className="review-lock"><LockKeyhole/><div><small>{form.title || "UNTITLED COVENANT"}</small><blockquote>“{form.promise || "No protected promise entered."}”</blockquote></div></div><dl className="review-grid"><div><dt>Canonical source</dt><dd>{form.canonicalUrl || "—"}</dd></div><div><dt>Beneficiary</dt><dd>{form.beneficiary || "—"}</dd></div><div><dt>Stake</dt><dd>{form.stake} GEN</dd></div><div><dt>Finder reward</dt><dd>{form.rewardPercent}%</dd></div><div><dt>Expiry</dt><dd>{new Date(expiry*1000).toUTCString()}</dd></div></dl><p className="field-note">Signing creates BASELINE_PENDING first. The covenant becomes ACTIVE only after GenLayer independently verifies that the canonical source actually supports the protected promise.</p>{tx && <a className="tx-proof" href={`${EXPLORER_URL}/tx/${tx}`} target="_blank" rel="noreferrer">Submitted transaction <ExternalLink size={12}/></a>}</>}
      </motion.div>
    </AnimatePresence></div>

    <div className="composer-actions"><button className="composer-back" disabled={step === 0 || busy} onClick={back}><ArrowLeft size={15}/> Back</button>{step < labels.length - 1 ? <button className="composer-next" onClick={next}>Continue <ArrowRight size={15}/></button> : <button className="composer-next signal-button" disabled={busy || !configured} onClick={() => void submit()}>{busy ? "Waiting for finality…" : "Sign & lock covenant"}<LockKeyhole size={15}/></button>}</div>
  </section>;
}
