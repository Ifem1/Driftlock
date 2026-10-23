$ErrorActionPreference = "Stop"
$env:GENVM_VERSION = "v0.2.12"

function Invoke-Gate([string]$Name, [scriptblock]$Command) {
    Write-Host "`n== $Name ==" -ForegroundColor Cyan
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE"
    }
}

$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
try {
    Invoke-Gate "Python compile" { python -m compileall -q contracts tests/direct scripts }
    Invoke-Gate "Deployment preflight" { python scripts/preflight.py }
    Invoke-Gate "Secret scan" { python scripts/scan_secrets.py }
    Invoke-Gate "GenVM Registry lint and ABI" { genvm-lint check contracts/drift_registry.py --json }
    Invoke-Gate "GenVM Inspector lint and ABI" { genvm-lint check contracts/source_inspector.py --json }
    Invoke-Gate "GenVM Judge lint and ABI" { genvm-lint check contracts/breach_judge.py --json }
    Invoke-Gate "Direct Mode contract tests" { python -m pytest tests/direct/ -q }
    Invoke-Gate "Frontend tests" { npm --prefix frontend test }
    Invoke-Gate "Frontend typecheck" { npm --prefix frontend run typecheck }
    Invoke-Gate "Frontend lint" { npm --prefix frontend run lint }
    Invoke-Gate "Frontend offline dependency audit" { npm --prefix frontend audit --offline }
    Invoke-Gate "Frontend production build" { npm --prefix frontend run build }
    Write-Host "`nAll local Driftlock V2 gates passed." -ForegroundColor Green
}
finally {
    Pop-Location
}
