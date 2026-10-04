import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import type { DecodedDeployData, GenLayerClient, TransactionHash } from "genlayer-js/types";
import { ExecutionResult, TransactionStatus } from "genlayer-js/types";

function assertSuccessfulFinalization(receipt: any, label: string) {
  if (receipt?.statusName !== TransactionStatus.FINALIZED || receipt?.txExecutionResultName !== ExecutionResult.FINISHED_WITH_RETURN) {
    const status = receipt?.statusName ?? receipt?.status ?? "unknown";
    const execution = receipt?.txExecutionResultName ?? receipt?.txExecutionResult ?? "unknown";
    const reason = receipt?.consensus_data?.leader_receipt?.find((item: any) => item.error)?.error;
    throw new Error(`${label} did not finalize with successful execution (status: ${status}, execution: ${execution})${reason ? `: ${reason}` : "."}`);
  }
}

async function deploy(client: GenLayerClient<any>, file: string, args: unknown[] = []) {
  const code = new Uint8Array(readFileSync(path.resolve(process.cwd(), file)));
  const hash = await client.deployContract({ code, args } as any);
  const receipt: any = await client.waitForTransactionReceipt({
    hash: hash as TransactionHash,
    status: TransactionStatus.FINALIZED,
    retries: 240,
    interval: 5000,
  } as any);
  assertSuccessfulFinalization(receipt, `Deployment for ${file}`);
  const address = (receipt?.txDataDecoded as DecodedDeployData | undefined)?.contractAddress
    || receipt?.data?.contract_address || receipt?.contract_address || receipt?.recipient;
  if (!address) throw new Error(`No contract address returned for ${file}`);
  return { address: String(address), txHash: String(hash), hash: String(hash) };
}

export default async function main(client: GenLayerClient<any>) {
  const chainId = Number((client as any)?.chain?.id);
  if (chainId !== 61999) throw new Error(`Refusing deployment: Driftlock is locked to Studionet 61999, client is ${chainId}`);
  console.log("Driftlock deployment target: Studionet 61999 only");

  // Secure bootstrap: children authenticate one fixed Registry, then Registry binds them exactly once.
  const registry = await deploy(client, "contracts/drift_registry.py", ["", ""]);
  const inspector = await deploy(client, "contracts/source_inspector.py", [registry.address]);
  const judge = await deploy(client, "contracts/breach_judge.py", [registry.address]);

  const configureHash = await (client as any).writeContract({
    address: registry.address,
    functionName: "configure_components",
    args: [inspector.address, judge.address],
    value: 0n,
  });
  const configureReceipt: any = await client.waitForTransactionReceipt({
    hash: configureHash as TransactionHash,
    status: TransactionStatus.FINALIZED,
    retries: 240,
    interval: 5000,
  } as any);
  assertSuccessfulFinalization(configureReceipt, "Component binding");

  const manifest = {
    product: "Driftlock",
    network: "studionet",
    chainId: 61999,
    rpc: "https://studio.genlayer.com/api",
    explorer: "https://explorer-studio.genlayer.com",
    deployedAt: new Date().toISOString(),
    contracts: { registry, inspector, judge, configureTxHash: String(configureHash) },
  };
  mkdirSync(path.resolve(process.cwd(), "deployments"), { recursive: true });
  writeFileSync(path.resolve(process.cwd(), "deployments/studionet.json"), JSON.stringify(manifest, null, 2) + "\n");
  writeFileSync(path.resolve(process.cwd(), "frontend/.env.local"), [
    "NEXT_PUBLIC_GENLAYER_CHAIN_ID=61999",
    "NEXT_PUBLIC_GENLAYER_RPC_URL=https://studio.genlayer.com/api",
    "NEXT_PUBLIC_GENLAYER_EXPLORER=https://explorer-studio.genlayer.com",
    `NEXT_PUBLIC_REGISTRY_ADDRESS=${registry.address}`,
    `NEXT_PUBLIC_INSPECTOR_ADDRESS=${inspector.address}`,
    `NEXT_PUBLIC_JUDGE_ADDRESS=${judge.address}`,
    "",
  ].join("\n"));
  console.log("Wrote deployments/studionet.json and frontend/.env.local");
  return manifest;
}
