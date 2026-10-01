"use client";

import { createContext, createElement, useCallback, useContext, useEffect, useRef, useState } from "react";

export const CHAIN_ID = 61999;
export const CHAIN_HEX = `0x${CHAIN_ID.toString(16)}`;
export const RPC_URL = process.env.NEXT_PUBLIC_GENLAYER_RPC_URL || "https://studio.genlayer.com/api";
export const EXPLORER_URL = process.env.NEXT_PUBLIC_GENLAYER_EXPLORER || "https://explorer-studio.genlayer.com";

export type Eip1193Provider = {
  request: (args: { method: string; params?: unknown[] | Record<string, unknown> }) => Promise<unknown>;
  on?: (event: string, listener: (...args: unknown[]) => void) => void;
  removeListener?: (event: string, listener: (...args: unknown[]) => void) => void;
};

declare global { interface Window { ethereum?: Eip1193Provider } }

export function injectedProvider(): Eip1193Provider | null {
  return typeof window === "undefined" ? null : window.ethereum || null;
}

export function normalizeAccounts(result: unknown): string[] {
  return Array.isArray(result) ? result.filter((x): x is string => typeof x === "string") : [];
}

export function sameWallet(left?: string | null, right?: string | null): boolean {
  return !!left && !!right && left.toLowerCase() === right.toLowerCase();
}

export type ClipboardWriter = { writeText: (value: string) => Promise<void> };

export function isStudionetChain(chainId?: number | null): boolean {
  return chainId === CHAIN_ID;
}

export async function copyWalletAddress(address: string, clipboard?: ClipboardWriter | null): Promise<void> {
  if (!address) throw new Error("No wallet address to copy");
  const writer = clipboard === undefined
    ? (typeof navigator === "undefined" ? null : navigator.clipboard)
    : clipboard;
  if (!writer?.writeText) throw new Error("Clipboard is not available");
  await writer.writeText(address);
}

export async function ensureStudionet(): Promise<void> {
  const provider = injectedProvider();
  if (!provider) throw new Error("No injected EIP-1193 wallet found");
  const current = await provider.request({ method: "eth_chainId" });
  if (typeof current === "string" && parseInt(current, 16) === CHAIN_ID) return;
  try {
    await provider.request({ method: "wallet_switchEthereumChain", params: [{ chainId: CHAIN_HEX }] });
  } catch (error: unknown) {
    const code = typeof error === "object" && error && "code" in error ? Number((error as { code?: unknown }).code) : 0;
    if (code !== 4902) throw error;
    await provider.request({
      method: "wallet_addEthereumChain",
      params: [{
        chainId: CHAIN_HEX,
        chainName: "GenLayer Studionet",
        nativeCurrency: { name: "GEN", symbol: "GEN", decimals: 18 },
        rpcUrls: [RPC_URL],
        blockExplorerUrls: [EXPLORER_URL],
      }],
    });
  }
}

type WalletState = {
  address: string | null;
  chainId: number | null;
  ready: boolean;
  connected: boolean;
  correctNetwork: boolean;
  hasProvider: boolean;
  connect: () => Promise<string>;
  disconnect: () => void;
  refresh: () => Promise<void>;
  switchNetwork: () => Promise<void>;
};

const WalletContext = createContext<WalletState | null>(null);

function useWalletState(): WalletState {
  const [address, setAddress] = useState<string | null>(null);
  const [chainId, setChainId] = useState<number | null>(null);
  const [ready, setReady] = useState(false);
  const disconnected = useRef(false);
  const generation = useRef(0);

  const refresh = useCallback(async () => {
    const provider = injectedProvider();
    if (!provider) { setAddress(null); setChainId(null); setReady(true); return; }
    const own = ++generation.current;
    try {
      const [rawAccounts, rawChain] = await Promise.all([
        provider.request({ method: "eth_accounts" }),
        provider.request({ method: "eth_chainId" }),
      ]);
      if (own !== generation.current) return;
      const accounts = normalizeAccounts(rawAccounts);
      setAddress(disconnected.current ? null : accounts[0] || null);
      setChainId(typeof rawChain === "string" ? parseInt(rawChain, 16) : null);
    } finally { setReady(true); }
  }, []);

  useEffect(() => {
    void refresh();
    const provider = injectedProvider();
    if (!provider?.on) return;
    const listener = () => { void refresh(); };
    provider.on("accountsChanged", listener);
    provider.on("chainChanged", listener);
    return () => {
      provider.removeListener?.("accountsChanged", listener);
      provider.removeListener?.("chainChanged", listener);
    };
  }, [refresh]);

  const connect = useCallback(async () => {
    const provider = injectedProvider();
    if (!provider) throw new Error("Install or open an injected EIP-1193 wallet to continue");
    disconnected.current = false;
    const xs = normalizeAccounts(await provider.request({ method: "eth_requestAccounts" }));
    if (!xs[0]) throw new Error("No wallet account was returned");
    await ensureStudionet();
    await refresh();
    return xs[0];
  }, [refresh]);

  const disconnect = useCallback(() => {
    disconnected.current = true;
    generation.current += 1;
    setAddress(null);
  }, []);

  return {
    address, chainId, ready, connected: !!address, correctNetwork: isStudionetChain(chainId),
    hasProvider: !!injectedProvider(), connect, disconnect, refresh, switchNetwork: ensureStudionet,
  };
}

export function WalletProvider({ children }: { children: React.ReactNode }) {
  return createElement(WalletContext.Provider, { value: useWalletState() }, children);
}

export function useInjectedWallet(): WalletState {
  const value = useContext(WalletContext);
  if (!value) throw new Error("useInjectedWallet must be used inside WalletProvider");
  return value;
}
