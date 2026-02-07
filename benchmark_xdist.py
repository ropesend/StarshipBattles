import subprocess
import time
import json
import os
import sys

def run_pytest(n):
    print(f"--- Running tests with n={n} ---", flush=True)
    start_time = time.time()
    # Override n from pytest.ini using the command line arg
    cmd = [sys.executable, "-m", "pytest", f"-n={n}", "--dist=loadscope", "--junitxml=benchmark_results.xml"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.time()
    duration = end_time - start_time
    
    fails = []
    # Parse pytest output for failed tests
    for line in result.stdout.splitlines():
        if "FAILED " in line and "::" in line:
            parts = line.split()
            for p in parts:
                if "::" in p:
                    fails.append(p)
                    break
        elif line.startswith("FAIL ") or line.startswith("ERROR "):
             fails.append(line)

    res = {
        "n": n,
        "duration": duration,
        "exit_code": result.returncode,
        "fails": sorted(list(set(fails)))
    }
    return res

def save_results(results):
    with open("benchmark_log.json", "w") as f:
        json.dump(results, f, indent=4)

def main():
    results = []
    if os.path.exists("benchmark_log.json"):
        try:
            with open("benchmark_log.json", "r") as f:
                results = json.load(f)
            print(f"Loaded {len(results)} previous results.", flush=True)
        except:
            pass

    # Baseline run
    n1_done = any(r["n"] == 1 for r in results)
    if not n1_done:
        n1_result = run_pytest(1)
        results.append(n1_result)
        save_results(results)
        
        if n1_result["exit_code"] != 0:
            print("!!! Baseline n=1 failed. Stopping benchmark as requested. !!!", flush=True)
            return
        print(f"n=1 passed in {n1_result['duration']:.2f}s.", flush=True)
    else:
        print("n=1 already completed. Skipping to parallel runs.", flush=True)

    for n in range(2, 13):
        if any(r["n"] == n for r in results):
            print(f"n={n} already completed. Skipping.", flush=True)
            continue
            
        res = run_pytest(n)
        results.append(res)
        save_results(results)
        print(f"n={n} completed in {res['duration']:.2f}s with exit code {res['exit_code']}", flush=True)

    # Final summary
    print("\n--- BENCHMARK SUMMARY ---", flush=True)
    print("| n | Duration (s) | Failures |", flush=True)
    print("|---|--------------|----------|", flush=True)
    n1_results = [r for r in results if r["n"] == 1]
    n1_fails = set(n1_results[0]["fails"]) if n1_results else set()
    
    all_fails = set()
    for res in sorted(results, key=lambda x: x["n"]):
        print(f"| {res['n']} | {res['duration']:.2f} | {len(res['fails'])} |", flush=True)
        for f in res["fails"]:
            all_fails.add(f)
    
    if all_fails:
        print("\n--- DETECTED FAILURES (POTENTIALLY FLAKY) ---", flush=True)
        for f in sorted(all_fails):
            if f not in n1_fails:
                print(f"FLAKY: {f}", flush=True)
            else:
                print(f"CONSISTENT FAIL: {f}", flush=True)

if __name__ == "__main__":
    main()
