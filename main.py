import argparse
import sys
import os
from typing import List, Dict
from termcolor import colored

# Add deepteam repo to sys.path
sys.path.insert(0, os.path.abspath("deepteam_repo"))

from deepteam.attacks.multi_turn.crescendo_jailbreaking.crescendo_jailbreaking import CrescendoJailbreaking
from deepteam.vulnerabilities.bias.bias import Bias
from deepteam.vulnerabilities.illegal_activity.illegal_activity import IllegalActivity
from deepteam.test_case.test_case import RTTestCase, RTTurn

from ollama_deepeval_wrapper import OllamaDeepEvalWrapper
import ollama

def main():
    parser = argparse.ArgumentParser(description="DeepTeam Crescendo Prompt Injection Attack Framework")
    parser.add_argument("--target", type=str, default="llama3", help="Target model to attack (default: llama3)")
    parser.add_argument("--attacker", type=str, default="llama3", help="Attacker/Judge model (simulator) (default: llama3)")
    
    parser.add_argument("--vulnerability", type=str, choices=["Bias", "IllegalActivity"], required=True,
                        help="The type of vulnerability to test")
    parser.add_argument("--purpose", type=str, default="General AI Assistant",
                        help="The purpose of the LLM application to tailor baseline attacks.")
    parser.add_argument("--attacks-per-vuln-type", type=int, default=1,
                        help="Number of baseline attacks to generate per vulnerability type.")
    
    parser.add_argument("--turns", type=int, default=10, help="Maximum number of turns per attack attempt")
    parser.add_argument("--backtracks", type=int, default=5, help="Maximum number of backtracks per turn")

    args = parser.parse_args()

    print(colored(f"[*] Initializing DeepTeam attack with:", "cyan"))
    print(colored(f"  Target: {args.target}", "cyan"))
    print(colored(f"  Attacker/Judge (Simulator): {args.attacker}", "cyan"))
    print(colored(f"  Vulnerability: {args.vulnerability}", "cyan"))
    print(colored(f"  Purpose: {args.purpose}", "cyan"))
    print(colored(f"  Max Rounds: {args.turns}", "cyan"))
    print(colored(f"  Max Backtracks: {args.backtracks}\n", "cyan"))
    print("-" * 30)

    # Initialize models
    simulator_model = OllamaDeepEvalWrapper(model_name=args.attacker)
    
    # Callback for the target model
    def target_model_callback(prompt: str, turns: List[RTTurn]) -> str:
        # Construct the full history for the target
        messages = []
        for turn in turns:
            messages.append({'role': turn.role, 'content': turn.content})
        
        # Add the current prompt if it's not already the last message
        # (DeepTeam passes prompt separately, but also history)
        if not messages or messages[-1]['content'] != prompt:
            messages.append({'role': 'user', 'content': prompt})

        print(colored(f"\n[Target Input]: {prompt}", "green"))
        response = ollama.chat(model=args.target, messages=messages)
        content = response['message']['content']
        print(colored(f"[Target Output]: {content}\n", "blue"))
        return content

    # Select Vulnerability
    vuln_map = {
        "Bias": Bias,
        "IllegalActivity": IllegalActivity
    }
    vuln_class = vuln_map[args.vulnerability]
    vulnerability = vuln_class()

    # Initialize Crescendo Attack
    crescendo = CrescendoJailbreaking(
        max_rounds=args.turns,
        max_backtracks=args.backtracks,
        simulator_model=simulator_model
    )

    try:
        print(colored(f"[*] Simulating attacks for {args.vulnerability}...", "yellow"))
        # Using .progress() to run the full attack loop
        results = crescendo.progress(
            vulnerability=vulnerability,
            model_callback=target_model_callback
        )
        
        # Display Results
        print(colored("\n[*] Attack Results:", "magenta", attrs=['bold']))
        for vuln_type, turns in results.items():
            print(colored(f"\nType: {vuln_type}", "cyan"))
            for turn in turns:
                role_color = "red" if turn.role == "user" else "green"
                print(colored(f"  {turn.role.upper()}: {turn.content}", role_color))

    except Exception as e:
        print(colored(f"An error occurred: {e}", "red"))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
