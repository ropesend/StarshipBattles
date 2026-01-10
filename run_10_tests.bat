@echo off
setlocal enabledelayedexpansion
set FAIL_COUNT=0
set PASS_COUNT=0

for /L %%i in (1,1,10) do (
    echo === Run %%i/10 ===
    pytest tests/unit/ -n 16 --tb=no -q
    if errorlevel 1 (
        echo Run %%i: FAIL
        set /a FAIL_COUNT+=1
    ) else (
        echo Run %%i: PASS
        set /a PASS_COUNT+=1
    )
    echo.
)

echo ========================================
echo RESULTS: !PASS_COUNT!/10 perfect runs
echo ========================================

if !FAIL_COUNT! EQU 0 (
    echo SUCCESS: 10/10 consecutive runs passed! 100%% stability achieved!
    exit /b 0
) else (
    echo INCOMPLETE: !FAIL_COUNT! failures detected
    exit /b 1
)
