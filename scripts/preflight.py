"""Static release checks for network and source/deployment consistency."""

import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
active = json.loads((ROOT / "deployments/studionet.json").read_text(encoding="utf-8"))
historical = json.loads((ROOT / "deployments/studionet-v1.json").read_text(encoding="utf-8"))

assert active["chainId"] == historical["chainId"] == 61999
assert active["rpc"] == historical["rpc"] == "https://studio.genlayer.com/api"
assert active["explorer"] == historical["explorer"] == "https://explorer-studio.genlayer.com"
assert historical["contracts"]["registry"]["address"] == "0xb5c8117DC80Dc9d84ECc95dFa139a4f06CD8d299"
assert json.loads((ROOT / "package.json").read_text())["devDependencies"]["genlayer"] == "0.39.1"

if active.get("protocolVersion") == 2:
    for component, file in (("registry", "drift_registry.py"),
                            ("inspector", "source_inspector.py"), ("judge", "breach_judge.py")):
        expected = active["contracts"][component]["sourceSha256"]
        actual = hashlib.sha256((ROOT / "contracts" / file).read_bytes()).hexdigest()
        assert expected == actual, f"V2 {component} deployed-source digest differs from checkout"
else:
    assert active["contracts"] == historical["contracts"], "V1 active manifest diverges from history"

for folder in ("contracts", "frontend", "deploy", "deployments"):
    for parent, dirs, files in os.walk(ROOT / folder):
        dirs[:] = [name for name in dirs if name not in ("node_modules", ".next", "__pycache__")]
        for name in files:
            path = Path(parent) / name
            if path.suffix in (".py", ".ts", ".tsx", ".json"):
                assert "61997" not in path.read_text(encoding="utf-8"), f"wrong chain ID in {path}"

print("preflight: Studionet pin, historical manifest and source configuration verified")
