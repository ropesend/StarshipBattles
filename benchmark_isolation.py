import subprocess
import time
import json
import os
import sys

def run_pytest(n):
    print(f"\n>>> Starting benchmark with n={n} workers...", flush=True)
    start_time = time.perf_counter()
    
    # We use -n {n} to override any pytest.ini settings.
    # --dist=loadscope is often safer for isolation than load.
    # We only target tests/ as requested.
    cmd = [sys.executable, "-m", "pytest", "-n", str(n), "--dist", "loadscope", "tests/"]
    
    # Run the command
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    end_time = time.perf_counter()
    duration = end_time - start_time
    
    fails = []
    # Simple extraction of failed test IDs from pytest short summary
    # Pytest usually lists them as FAILED tests/path/to/test.py::test_name - Reason
    in_summary = False
    for line in result.stdout.splitlines():
        if "=== FAILURES ===" in line:
            in_summary = True
        if "=== SHORT TEST SUMMARY INFO ===" in line:
            in_summary = True
            
        if "FAILED " in line and "::" in line:
            parts = line.split()
            for p in parts:
                if "::" in p:
                    # Clean up the ID
                    test_id = p.strip()
                    if test_id.startswith("FAILED"):
                        continue
                    fails.append(test_id)
                    break
        elif "ERROR " in line and "::" in line:
             # Errors often count as isolation issues
             parts = line.split()
             for p in parts:
                 if "::" in p:
                     fails.append(p.strip())
                     break

    res = {
        "n": n,
        "duration": duration,
        "exit_code": result.returncode,
        "fail_count": len(fails),
        "fails": sorted(list(set(fails)))
    }
    return res

def save_report(data):
    with open("benchmark_report.json", "w") as f:
        json.dump(data, f, indent=4)

def main():
    print("=== TEST ISOLATION & PERFORMANCE BENCHMARK ===")
    print("Target: tests/ (6246 items)")
    print("Range: n=4 to n=16")
    
    all_results = []
    
    for n in range(4, 17):
        res = run_pytest(n)
        all_results.append(res)
        save_report(all_results)
        print(f"Result for n={n}: {res['duration']:.2f}s, Failures: {res['fail_count']}", flush=True)
        
    # Analyze results
    fastest = min(all_results, key=lambda x: x["duration"])
    
    # Isolation analysis: find tests that fail in SOME runs but maybe not others
    # (Though we don't have a single-threaded baseline here to be 100% sure what's legit vs flake)
    # However, any difference in failure sets between N values suggests isolation/timing issues.
    all_fails_global = set()
    for r in all_results:
        for f in r["fails"]:
            all_fails_global.add(f)
            
    isolation_candidates = []
    for f in all_fails_global:
        # Check if it fails in EVERY run
        failed_in_all = all(f in r["fails"] for r in all_results)
        if not failed_in_all:
            isolation_candidates.append(f)

    print("\n=== SUMMARY OVERVIEW ===")
    print(f"Fastest worker count: n={fastest['n']} ({fastest['duration']:.2f}s)")
    
    if isolation_candidates:
        print(f"\nFound {len(isolation_candidates)} tests with potential isolation issues:")
        for f in sorted(isolation_candidates):
            print(f" - {f}")
    else:
        print("\nNo isolation issues detected (failed tests were consistent across all runs).")

if __name__ == "__main__":
    main()
