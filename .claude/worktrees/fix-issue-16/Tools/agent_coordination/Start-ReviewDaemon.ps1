# Start-ReviewDaemon.ps1
# One-click launcher for the review daemon.
# Run this in a separate terminal to start watching for review requests.
#
# Usage: .\Tools\agent_coordination\Start-ReviewDaemon.ps1

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Starship Battles — Review Daemon  " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Activate venv if it exists
$VenvActivate = Join-Path $ProjectRoot ".venv\Scripts\Activate.ps1"
if (Test-Path $VenvActivate) {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    . $VenvActivate
} else {
    Write-Host "No .venv\ found — using system Python" -ForegroundColor Gray
}

# Verify opencode is available
if (Get-Command opencode -ErrorAction SilentlyContinue) {
    Write-Host "opencode found at: $(Get-Command opencode | Select-Object -ExpandProperty Source)" -ForegroundColor Gray
} else {
    Write-Host "WARNING: opencode not found in PATH — daemon will fail on first request" -ForegroundColor Yellow
}

Write-Host "Starting review daemon..." -ForegroundColor Green
Write-Host "  Watching: AgentCoordination\opencodereview\pending_review_requests\" -ForegroundColor Gray
Write-Host "  Log file: AgentCoordination\opencodereview\local\review_daemon.log" -ForegroundColor Gray
Write-Host "  Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

python Tools/agent_coordination/review_daemon.py @args

Write-Host ""
Write-Host "Review daemon stopped." -ForegroundColor Yellow
