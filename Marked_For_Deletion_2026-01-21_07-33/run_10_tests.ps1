# Run 10 consecutive test passes to verify 100% stability
$failCount = 0
$passCount = 0

for ($i = 1; $i -le 10; $i++) {
    Write-Host "=== Run $i/10 ===" -ForegroundColor Cyan
    pytest tests/unit/ -n 16 --tb=no -q
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Run $i: PASS" -ForegroundColor Green
        $passCount++
    } else {
        Write-Host "Run $i: FAIL (exit code $LASTEXITCODE)" -ForegroundColor Red
        $failCount++
    }
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Yellow
Write-Host "RESULTS: $passCount/10 perfect runs" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow

if ($failCount -eq 0) {
    Write-Host "SUCCESS: 10/10 consecutive runs passed! 100% stability achieved!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "INCOMPLETE: $failCount failures detected" -ForegroundColor Red
    exit 1
}
