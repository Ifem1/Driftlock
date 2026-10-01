import Link from "next/link";

export function SiteFooter() {
  return <footer className="site-footer"><div><div className="brand footer-brand"><span className="brand-mark"/>DRIFTLOCK</div><p>Stake a public promise. Prove when it changes.</p></div><div className="footer-links"><Link href="/covenants">Covenants</Link><Link href="/create">Create</Link><Link href="/protocol">Protocol</Link><Link href="/demo">Live proof</Link></div><div className="footer-meta">GENLAYER STUDIONET<br/>CHAIN 61999<br/>NO OPERATOR VERDICT</div></footer>;
}
