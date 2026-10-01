"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "motion/react";
import { WalletButton } from "./WalletButton";

const links = [["/covenants", "Covenants"], ["/protocol", "Protocol"], ["/activity", "Activity"]] as const;

export function SiteHeader() {
  const pathname = usePathname();
  return <motion.header className="site-header" initial={{ y: -20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: .55 }}>
    <div className="site-header-inner">
      <Link href="/" className="brand"><span className="brand-mark"/>DRIFTLOCK</Link>
      <nav className="desktop-nav" aria-label="Primary navigation">
        {links.map(([href, label]) => <Link key={href} href={href} className={pathname.startsWith(href) ? "active" : ""}>{label}</Link>)}
      </nav>
      <div className="header-actions"><span className="network-label">STUDIONET / 61999</span><WalletButton/></div>
    </div>
  </motion.header>;
}
