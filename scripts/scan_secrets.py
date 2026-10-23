"""Fail on common committed key material without printing secret contents."""

import re
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
tracked = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                                  cwd=root, text=True).splitlines()
patterns = (
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(rb"(?i)(?:private[_-]?key|seed[_-]?phrase|mnemonic)\s*[:=]\s*['\"]?0x[0-9a-f]{64}"),
    re.compile(rb"(?i)(?:vercel[_-]?token|github[_-]?token)\s*[:=]\s*['\"]?[a-z0-9_\-]{20,}"),
)
findings = []
for name in tracked:
    path = root / name
    if not path.is_file() or path.stat().st_size > 2_000_000:
        continue
    data = path.read_bytes()
    if any(pattern.search(data) for pattern in patterns):
        findings.append(name)
if findings:
    raise SystemExit("Potential secret material in: " + ", ".join(findings))
print(f"secret scan: {len(tracked)} repository files checked")
