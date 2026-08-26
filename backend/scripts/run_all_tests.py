import subprocess
import sys

def run_script(script_name):
    print(f"\n==================================================")
    print(f"RUNNING: {script_name}")
    print(f"==================================================")
    result = subprocess.run([sys.executable, f"scripts/{script_name}"], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("ERRORS/WARNINGS:")
        print(result.stderr)
        
    if result.returncode != 0:
        print(f"\n[FAIL] {script_name} failed with exit code {result.returncode}")
        return False
    print(f"[PASS] {script_name} completed successfully")
    return True

def main():
    scripts_to_run = [
        "test_policy_engine.py",
        "test_triage_engine.py",
        "test_optimization_engine.py",
        "test_cdss_engine.py",
        "seed_resources.py",
        "test_e2e.py",
        "test_edge_cases.py"
    ]
    
    all_passed = True
    for script in scripts_to_run:
        if not run_script(script):
            all_passed = False
            break
            
    print(f"\n==================================================")
    if all_passed:
        print("FINAL VERIFICATION: PASS")
    else:
        print("FINAL VERIFICATION: FAIL")
    print(f"==================================================")
    
if __name__ == "__main__":
    main()
