"use client";
import { WalletProvider } from "@/lib/wallet";
import { Toaster } from "sonner";
export function Providers({ children }: { children: React.ReactNode }) {
  return <WalletProvider>{children}<Toaster theme="dark" richColors position="bottom-right"/></WalletProvider>;
}
