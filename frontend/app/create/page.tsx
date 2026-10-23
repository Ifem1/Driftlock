"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { AnimatePresence, motion } from "motion/react";
import { ArrowLeft, ArrowRight, Check, ExternalLink, LockKeyhole } from "lucide-react";
import { toast } from "sonner";
import { findLatestCovenantByOwner, PROTOCOL_VERSION, protocolConfigured, submitWrite, waitForFinalization } from "@/lib/protocol";
import { genToAtto } from "@/lib/format";
import { useInjectedWallet, EXPLORER_URL } from "@/lib/wallet";

const labels = ["Source", "Promise", "Breach rule", "Permitted changes", "Beneficiary", "Stake", "Expiry", "Review"];
const submitStages = ["wallet", "submitted", "consensus", "finalized"] as const;
type SubmitStage = "idle" | typeof submitStages[number];

type FormState = {
  title: string; subject: string; canonicalUrl: string; promise: string; breachRule: string;
  permitted: string; beneficiary: string; stake: string; rewardPercent: string; expiryHours: string;
  primaryPublisher: string; corroboratorUrl: string; corroboratorPublisher: string;
  contextUrl: string; contextPublisher: string;
  secondCorroboratorUrl: string; secondCorroboratorPublisher: string; minCorroborations: string;
};

const initial: FormState = {
  title: "", subject: "", canonicalUrl: "", promise: "", breachRule: "",
  permitted: "Formatting, spelling, clarification and changes unrelated to the protected promise are permitted.",
  beneficiary: "", stake: "0.1", rewardPercent: "10", expiryHours: "168",
  primaryPublisher: "", corroboratorUrl: "", corroboratorPublisher: "",
  contextUrl: "", contextPublisher: "",
  secondCorroboratorUrl: "", secondCorroboratorPublisher: "", minCorroborations: "1",
};

export default function CreatePage() {
  const [step, setStep] = useState(0);
  const [form, setForm] = useState<FormState>(initial);
  const [busy, setBusy] = useState(false);
  const [tx, setTx] = useState("");
  const [submitStage, setSubmitStage] = useState<SubmitStage>("idle");
  const wallet = useInjectedWallet();
  const router = useRouter();
  const configured = protocolConfigured();
  const update = (key: keyof FormState, value: string) => setForm((x) => ({ ...x, [key]: value }));
  const expiry = useMemo(() => Math.floor(Date.now()/1000) + Math.max(2, Number(form.expiryHours || 0)) * 3600, [form.expiryHours]);

  function validateStep(): string {
    if (step === 0) {
      if (!form.title.trim() || !form.subject.trim() || !form.canonicalUrl.startsWith("https://")) return "Add a title, subject and HTTPS canonical URL.";
      if (PROTOCOL_VERSION === 2 && (!form.corroboratorUrl.startsWith("https://") || form.primaryPublisher.trim().length < 3 || form.corroboratorPublisher.trim().length < 3)) return "Add a corroborating HTTPS source and both publisher identities.";
      if (PROTOCOL_VERSION === 2 && form.contextUrl && (!form.contextUrl.startsWith("https://") || form.contextPublisher.trim().length < 3)) return "Optional context needs an HTTPS URL and publisher.";
      if (PROTOCOL_VERSION === 2 && form.secondCorroboratorUrl && (!form.secondCorroboratorUrl.startsWith("https://") || form.secondCorroboratorPublisher.trim().length < 3)) return "The second corroborator needs an HTTPS URL and publisher.";
      if (PROTOCOL_VERSION === 2 && form.contextUrl && form.secondCorroboratorUrl) return "Choose context or a second corroborator; the policy accepts three sources total.";
      if (PROTOCOL_VERSION === 2 && form.minCorroborations === "2" && !form.secondCorroboratorUrl) return "Two required corroborations need two corroborating sources.";
      if (PROTOCOL_VERSION === 2) {
        try {
          const site = (url: string) => new URL(url).hostname.toLowerCase().split(".").slice(-2).join(".");
          const sites = [form.canonicalUrl, form.corroboratorUrl, ...(form.contextUrl ? [form.contextUrl] : []), ...(form.secondCorroboratorUrl ? [form.secondCorroboratorUrl] : [])].map(site);
          const publishers = [form.primaryPublisher, form.corroboratorPublisher, ...(form.contextUrl ? [form.contextPublisher] : []), ...(form.secondCorroboratorUrl ? [form.secondCorroboratorPublisher] : [])].map((x) => x.trim().toLowerCase());
          if (new Set(sites).size !== sites.length || new Set(publishers).size !== publishers.length) return "Sources need distinct sites and declared publishers.";
        } catch { return "Enter valid HTTPS source URLs."; }
      }
    }
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
    setBusy(true); setTx(""); setSubmitStage("wallet");
    try {
      const address = wallet.address || await wallet.connect();
      const policy = { version: 1, min_corroborations: Number(form.minCorroborations), sources: [
        { url: form.canonicalUrl.trim(), role: "PRIMARY", publisher: form.primaryPublisher.trim() },
        { url: form.corroboratorUrl.trim(), role: "CORROBORATING", publisher: form.corroboratorPublisher.trim() },
        ...(form.secondCorroboratorUrl.trim() ? [{ url: form.secondCorroboratorUrl.trim(), role: "CORROBORATING", publisher: form.secondCorroboratorPublisher.trim() }] : []),
        ...(form.contextUrl.trim() ? [{ url: form.contextUrl.trim(), role: "CONTEXT", publisher: form.contextPublisher.trim() }] : []),
      ] };
      const hash = await submitWrite(address, PROTOCOL_VERSION === 2 ? "create_covenant_v2" : "create_covenant", [
        form.title.trim(), form.subject.trim(), form.canonicalUrl.trim(), form.promise.trim(), form.breachRule.trim(),
        form.permitted.trim(), form.beneficiary, BigInt(Math.round(Number(form.rewardPercent) * 100)), BigInt(expiry),
        ...(PROTOCOL_VERSION === 2 ? [JSON.stringify(policy)] : []),
      ], genToAtto(form.stake));
      setTx(hash);
      setSubmitStage("submitted");
      toast("Covenant submitted", { description: "The transaction is accepted. Waiting for source-grounded baseline consensus." });
      setSubmitStage("consensus");
      await waitForFinalization(hash);
      setSubmitStage("finalized");
      toast.success("Creation transaction finalized. Baseline verification is processing.");
      const id = await findLatestCovenantByOwner(address, true);
      if (id) router.push(`/covenants/${id}`);
    } catch (e) {
      setSubmitStage((stage) => stage === "wallet" ? "idle" : stage);
      toast.error(e instanceof Error ? e.message : String(e));
    }
    finally { setBusy(false); }
  }

  const submitStageIndex = submitStages.indexOf(submitStage === "idle" ? "wallet" : submitStage);
  const submitLabel = busy
    ? submitStage === "wallet" ? "Awaiting wallet approval…"
      : submitStage === "submitted" ? "Transaction submitted…"
      : "Consensus pending…"
    : submitStage === "finalized" ? "Finalized" : "Sign & lock covenant";

  return <section className="composer-shell">
    <div className="composer-head"><span className="mono-label">CREATE / IMMUTABLE AFTER BASELINE</span><h1>Compose the<br/><em>covenant.</em></h1><p>Each step becomes part of what GenLayer will later judge. Be precise now; active covenants cannot be silently rewritten.</p></div>
    {!configured && <div className="deployment-note composer-note"><strong>Build mode.</strong><span>The full composer is ready. Live signing becomes available after the Registry address is configured.</span></div>}
    <div className="composer-progress">{labels.map((label, i) => <button key={label} onClick={() => i < step && setStep(i)} className={i === step ? "current" : i < step ? "done" : ""}><span>{i < step ? <Check size={11}/> : String(i+1).padStart(2,"0")}</span>{label}</button>)}</div>

    <div className="composer-body"><AnimatePresence mode="wait" initial={false}>
      <motion.div key={step} className="composer-panel" initial={{ opacity: 0, y: 26, filter: "blur(8px)" }} animate={{ opacity: 1, y: 0, filter: "blur(0px)" }} exit={{ opacity: 0, y: -18, filter: "blur(5px)" }} transition={{ duration: .38, ease: [0.16,1,.3,1] }}>
        {step === 0 && <><span className="step-overline">01 / SOURCE</span><h2>What public source carries the promise?</h2><label>Short title <input maxLength={100} value={form.title} onChange={(e) => update("title", e.target.value)} placeholder="Customer data covenant"/></label><label>Subject <textarea maxLength={1200} value={form.subject} onChange={(e) => update("subject", e.target.value)} placeholder="The current customer-data handling policy of Example Company."/></label><label>Canonical HTTPS URL <input maxLength={800} value={form.canonicalUrl} onChange={(e) => update("canonicalUrl", e.target.value)} placeholder="https://example.com/privacy"/></label>{PROTOCOL_VERSION === 2 && <><label>Primary publisher <input maxLength={100} value={form.primaryPublisher} onChange={(e) => update("primaryPublisher", e.target.value)} placeholder="Example Company"/></label><label>Corroborating HTTPS URL <input maxLength={800} value={form.corroboratorUrl} onChange={(e) => update("corroboratorUrl", e.target.value)} placeholder="https://observer.example/report"/></label><label>Corroborating publisher <input maxLength={100} value={form.corroboratorPublisher} onChange={(e) => update("corroboratorPublisher", e.target.value)} placeholder="Independent Observer"/></label><label>Second corroborator / optional <input maxLength={800} value={form.secondCorroboratorUrl} onChange={(e) => update("secondCorroboratorUrl", e.target.value)} placeholder="https://another.example/report"/></label>{form.secondCorroboratorUrl && <label>Second publisher <input maxLength={100} value={form.secondCorroboratorPublisher} onChange={(e) => update("secondCorroboratorPublisher", e.target.value)} placeholder="Another observer"/></label>}<label>Required corroborations <select value={form.minCorroborations} onChange={(e) => update("minCorroborations", e.target.value)}><option value="1">One</option><option value="2">Two</option></select></label><label>Context URL / optional <input maxLength={800} value={form.contextUrl} onChange={(e) => update("contextUrl", e.target.value)} placeholder="https://context.example/background"/></label>{form.contextUrl && <label>Context publisher <input maxLength={100} value={form.contextPublisher} onChange={(e) => update("contextPublisher", e.target.value)} placeholder="Context publisher"/></label>}</>}<p className="field-note">Source identities and evidence policy are frozen at creation. Context cannot satisfy the corroboration threshold. Declared publisher independence is checked for duplicates but is not cryptographic proof of ownership.</p></>}
        {step === 1 && <><span className="step-overline">02 / PROMISE</span><h2>Write the exact promise you expect to remain true.</h2><label>Protected promise <textarea className="large-input" maxLength={1800} value={form.promise} onChange={(e) => update("promise", e.target.value)} placeholder="Customer information is not sold, licensed or commercially transferred to third parties."/><small>{form.promise.length}/1800</small></label></>}
        {step === 2 && <><span className="step-overline">03 / BREACH RULE</span><h2>Define what would actually count as breaking it.</h2><label>Breach rule <textarea className="large-input" maxLength={2400} value={form.breachRule} onChange={(e) => update("breachRule", e.target.value)} placeholder="A future version that permits sale, licensing, brokerage or commercial transfer of customer information constitutes breach."/><small>{form.breachRule.length}/2400</small></label></>}
        {step === 3 && <><span className="step-overline">04 / SAFE CHANGES</span><h2>What can change without becoming a breach?</h2><label>Permitted changes <textarea className="large-input" maxLength={1600} value={form.permitted} onChange={(e) => update("permitted", e.target.value)}/><small>{form.permitted.length}/1600</small></label></>}
        {step === 4 && <><span className="step-overline">05 / BENEFICIARY</span><h2>Who receives the remaining stake after a confirmed breach?</h2><label>Beneficiary address <input value={form.beneficiary} onChange={(e) => update("beneficiary", e.target.value)} placeholder="0x…"/></label><p className="field-note">This address becomes immutable after activation. It does not need to be the covenant owner.</p></>}
        {step === 5 && <><span className="step-overline">06 / ECONOMICS</span><h2>Put value behind the promise.</h2><div className="split-fields"><label>Stake / GEN <input inputMode="decimal" value={form.stake} onChange={(e) => update("stake", e.target.value)}/></label><label>Finder reward / % <input inputMode="decimal" value={form.rewardPercent} onChange={(e) => update("rewardPercent", e.target.value)}/></label></div><p className="field-note">On confirmed breach, the finder reward goes to the challenger and the remaining stake goes to the beneficiary. Otherwise the covenant owner recovers unbreached stake at expiry.</p></>}
        {step === 6 && <><span className="step-overline">07 / EXPIRY</span><h2>How long should the promise stay under stake?</h2><label>Lifetime in hours <input inputMode="numeric" value={form.expiryHours} onChange={(e) => update("expiryHours", e.target.value)}/></label><div className="expiry-preview">Projected expiry <strong>{new Date(expiry * 1000).toUTCString()}</strong></div></>}
        {step === 7 && <><span className="step-overline">08 / REVIEW</span><h2>These terms are about to lock.</h2><div className="review-lock"><LockKeyhole/><div><small>{form.title || "UNTITLED COVENANT"}</small><blockquote>“{form.promise || "No protected promise entered."}”</blockquote></div></div><dl className="review-grid"><div><dt>Canonical source</dt><dd>{form.canonicalUrl || "—"}</dd></div>{PROTOCOL_VERSION === 2 && <><div><dt>Primary publisher</dt><dd>{form.primaryPublisher || "—"}</dd></div><div><dt>Corroborator</dt><dd>{form.corroboratorUrl || "—"} · {form.corroboratorPublisher}</dd></div>{form.secondCorroboratorUrl && <div><dt>Second corroborator</dt><dd>{form.secondCorroboratorUrl} · {form.secondCorroboratorPublisher}</dd></div>}<div><dt>Required corroborations</dt><dd>{form.minCorroborations}</dd></div>{form.contextUrl && <div><dt>Context only</dt><dd>{form.contextUrl} · {form.contextPublisher}</dd></div>}</>}<div><dt>Beneficiary</dt><dd>{form.beneficiary || "—"}</dd></div><div><dt>Stake</dt><dd>{form.stake} GEN</dd></div><div><dt>Challenge and appeal bond</dt><dd>{(Math.max(.0001, Number(form.stake)/100)).toFixed(4)} GEN each</dd></div><div><dt>Finder reward</dt><dd>{form.rewardPercent}%</dd></div><div><dt>Expiry</dt><dd>{new Date(expiry*1000).toUTCString()}</dd></div></dl><p className="field-note">Signing creates BASELINE_PENDING first. The covenant becomes ACTIVE only after GenLayer verifies a compliant primary source and the frozen evidence policy.</p>{submitStage !== "idle" && <div className="tx-state-rail" aria-live="polite">{submitStages.map((stageName, i) => <div key={stageName} className={`tx-state-step ${i < submitStageIndex ? "done" : i === submitStageIndex ? "current" : ""}`}><span>{i < submitStageIndex || submitStage === "finalized" && i === submitStageIndex ? <Check size={11}/> : String(i+1).padStart(2,"0")}</span><b>{stageName === "wallet" ? "Wallet approval" : stageName === "submitted" ? "Transaction submitted" : stageName === "consensus" ? "Consensus pending" : "Finalized"}</b></div>)}</div>}{tx && <a className="tx-proof" href={`${EXPLORER_URL}/tx/${tx}`} target="_blank" rel="noreferrer">Submitted transaction <ExternalLink size={12}/></a>}</>}
      </motion.div>
    </AnimatePresence></div>

    <div className="composer-actions"><button className="composer-back" disabled={step === 0 || busy} onClick={back}><ArrowLeft size={15}/> Back</button>{step < labels.length - 1 ? <button className="composer-next" onClick={next}>Continue <ArrowRight size={15}/></button> : <button className="composer-next signal-button" disabled={busy || !configured} onClick={() => void submit()}>{submitLabel}<LockKeyhole size={15}/></button>}</div>
  </section>;
}
