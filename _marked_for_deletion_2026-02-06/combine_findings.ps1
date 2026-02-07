# Script to combine all findings from review directories

$outputFile = "combined_findings.md"
$findingsDirs = @(
    "Reviews\results\2026-01-28_consistency_full-codebase-patterns\findings",
    "Reviews\results\2026-01-28_general_full-codebase-legacy-consistency-audit\findings",
    "Reviews\results\2026-01-28_general_maintainability-extensibility\findings"
)

# Clear/create output file
"# Combined Findings Report`n" | Out-File -FilePath $outputFile -Encoding UTF8
"Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n" | Add-Content -Path $outputFile -Encoding UTF8
"---`n" | Add-Content -Path $outputFile -Encoding UTF8

foreach ($dir in $findingsDirs) {
    if (Test-Path $dir) {
        # Add section header for this directory
        $dirName = Split-Path $dir -Parent | Split-Path -Leaf
        "`n# Source: $dirName`n" | Add-Content -Path $outputFile -Encoding UTF8
        "---`n" | Add-Content -Path $outputFile -Encoding UTF8

        # Get all markdown files and append them
        Get-ChildItem -Path $dir -Filter "*.md" | ForEach-Object {
            "`n## File: $($_.Name)`n" | Add-Content -Path $outputFile -Encoding UTF8
            Get-Content $_.FullName | Add-Content -Path $outputFile -Encoding UTF8
            "`n---`n" | Add-Content -Path $outputFile -Encoding UTF8
        }
    } else {
        Write-Warning "Directory not found: $dir"
    }
}

Write-Host "Combined findings saved to: $outputFile"
