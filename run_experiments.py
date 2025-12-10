import subprocess
import os
import itertools
from termcolor import colored
import sys

def run_experiment(target, attacker, vulnerability, strategy, enhancements, turns, log_dir):
    cmd = [
        sys.executable, "main.py",
        "--target", target,
        "--attacker", attacker,
        "--vulnerability", vulnerability,
        "--attack-strategy", strategy,
        "--turns", str(turns)
    ]

    if enhancements:
        cmd.append("--enhancements")
        cmd.extend(enhancements)

    # Generate a unique log filename
    enhancement_str = "_".join(enhancements) if enhancements else "none"
    log_filename = f"{vulnerability}_{strategy}_{enhancement_str}.json"
    log_path = os.path.join(log_dir, log_filename)
    
    cmd.extend(["--log-file", log_path])

    print(colored(f"[*] Running Experiment: {vulnerability} | {strategy} | {enhancement_str}", "yellow"))
    
    try:
        # Run the command and capture output (optional: print output to console)
        # Using check=True to raise exception on failure
        result = subprocess.run(cmd, check=True, text=True)
        print(colored(f"[+] Experiment completed. Log: {log_path}\n", "green"))
    except subprocess.CalledProcessError as e:
        print(colored(f"[-] Experiment failed with error code {e.returncode}", "red"))

def main():
    TARGET_MODEL = "llama3"
    ATTACKER_MODEL = "llama3"
    LOG_DIR = os.path.join(os.getcwd(), "results")
    
    # Define experiment parameters
    vulnerabilities = [
        "IllegalActivity", 
        "SQLInjection",
        # "Bias", 
        # "Toxicity"
    ]
    
    strategies = [
        "Linear",
        # "Crescendo",
        # "Tree"
    ]
    
    # Enhancement combinations: None, and single enhancements
    enhancement_options = [
        [],                 # No enhancement
        ["Base64"],
        # ["Leetspeak"],
        # ["Rot13"]
    ]

    TURNS = 3 # Keep low for testing speed

    # Create results directory
    os.makedirs(LOG_DIR, exist_ok=True)

    # Iterate over all combinations
    for vuln in vulnerabilities:
        for strat in strategies:
            for enh in enhancement_options:
                run_experiment(
                    target=TARGET_MODEL,
                    attacker=ATTACKER_MODEL,
                    vulnerability=vuln,
                    strategy=strat,
                    enhancements=enh,
                    turns=TURNS,
                    log_dir=LOG_DIR
                )

    print(colored("[*] All experiments completed.", "magenta", attrs=['bold']))

if __name__ == "__main__":
    main()
