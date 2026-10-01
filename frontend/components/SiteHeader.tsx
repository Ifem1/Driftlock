"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, useReducedMotion } from "motion/react";
import { WalletButton } from "./WalletButton";

const links = [["/covenants", "Covenants"], ["/protocol", "Protocol"], ["/activity", "Activity"]] as const;

export function SiteHeader() {
  const pathname = usePathname();
  const reduce = useReducedMotion();
  const nav = <>{links.map(([href, label]) => <Link key={href} href={href} className={pathname.startsWith(href) ? "active" : ""}>{label}</Link>)}</>;

  return <motion.header
    className="site-header"
    initial={reduce ? false : { y: -18, opacity: 0 }}
    animate={{ y: 0, opacity: 1 }}
    transition={{ duration: reduce ? 0 : .55, ease: [0.16, 1, 0.3, 1] }}
  >
    <div className="site-header-inner">
      <Link href="/" className="brand" aria-label="Driftlock home"><span className="brand-mark"/>DRIFTLOCK</Link>
      <nav className="desktop-nav" aria-label="Primary navigation">{nav}</nav>
      <div className="header-actions"><span className="network-label">STUDIONET / 61999</span><WalletButton/></div>
    </div>
    <nav className="mobile-nav" aria-label="Mobile navigation">{nav}</nav>
  </motion.header>;
}
