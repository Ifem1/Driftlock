"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ArrowUpRight, Search } from "lucide-react";
import { motion } from "motion/react";
import { listCovenants, protocolConfigured } from "@/lib/protocol";
import type { Covenant } from "@/lib/types";
import { attoToGen, timeLabel } from "@/lib/format";
import { StatusPill } from "@/components/StatusPill";

export default function CovenantsPage() {
  const [items, setItems] = useState<Covenant[]>([]);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("ALL");
  const configured = protocolConfigured();

  useEffect(() => { if (!configured) return; listCovenants().then((x) => setItems(x.items)).catch((e) => setError(String(e?.message || e))); }, [configured]);
  const filtered = useMemo(() => items.filter((c) => (filter === "ALL" || c.status === filter) && `${c.title} ${c.protected_promise}`.toLowerCase().includes(query.toLowerCase())), [items, filter, query]);

  return <section className="page-shell covenants-page">
    <div className="page-intro"><span className="mono-label">COVENANT INDEX / PUBLIC STATE</span><h1>Promises<br/><em>under stake.</em></h1><p>Every live row reads from DriftRegistry on GenLayer Studionet. The source URL and covenant terms are frozen before activation.</p></div>
    {!configured && <div className="deployment-note"><strong>Protocol address not configured.</strong><span>The interface is built; live covenant rows appear after Codex deploys the contracts and writes the production Registry address.</span></div>}
    {error && <div className="error-banner">{error}</div>}
    <div className="index-controls"><label className="index-search"><Search size={15}/><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search covenants"/></label><div className="filter-tabs">{["ALL","ACTIVE","BREACHED","EXPIRED_UNBREACHED"].map((x) => <button key={x} className={filter === x ? "active" : ""} onClick={() => setFilter(x)}>{x.replaceAll("_", " ")}</button>)}</div></div>
    <div className="covenant-index">
      {configured && !items.length && !error && <div className="empty-editorial">No covenants have been created on this Registry yet.</div>}
      {filtered.map((c, index) => <motion.div key={c.id} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * .035 }}><Link href={`/covenants/${c.id}`} className="covenant-row">
        <div className="row-no">{String(index + 1).padStart(2,"0")}</div>
        <div className="row-main"><StatusPill status={c.status}/><h2>{c.title}</h2><p>“{c.protected_promise}”</p></div>
        <div className="row-meta"><span>STAKE<strong>{attoToGen(c.stake_atto)} GEN</strong></span><span>EXPIRES<strong>{timeLabel(c.expires_at)}</strong></span></div>
        <ArrowUpRight className="row-arrow"/>
      </Link></motion.div>)}
    </div>
  </section>;
}
