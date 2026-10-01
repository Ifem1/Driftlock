import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "@/components/Providers";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";

export const metadata: Metadata = {
  title: "Driftlock — Stake a public promise",
  description: "GenLayer-native stake-backed covenants over changing public information.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body><Providers><div className="site-atmosphere" aria-hidden="true"><i className="ambient-orb ambient-orb-a"/><i className="ambient-orb ambient-orb-b"/><i className="ambient-orb ambient-orb-c"/><span className="atmosphere-grain"/></div><SiteHeader/><main>{children}</main><SiteFooter/></Providers></body></html>;
}
