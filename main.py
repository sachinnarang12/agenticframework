"""
Multi-Agent Interaction Framework — Entry Point
================================================

Run any of the three example patterns from a single menu.

Usage:
    python main.py
    python main.py --example 1   # debate
    python main.py --example 2   # code pipeline
    python main.py --example 3   # research team
"""

import argparse
import os
import sys

import anthropic
from dotenv import load_dotenv

load_dotenv()


EXAMPLES = {
    "1": ("Two-Agent Debate",       "examples.01_two_agent_debate",  "run_debate"),
    "2": ("Code Review Pipeline",   "examples.02_code_pipeline",     "run_pipeline"),
    "3": ("Research Team",          "examples.03_research_team",     "run_research_team"),
}


def print_menu() -> None:
    print("\n" + "=" * 60)
    print("  Multi-Agent Interaction Framework")
    print("=" * 60)
    print("\n  Choose an example to run:\n")
    for key, (label, _, _) in EXAMPLES.items():
        print(f"    [{key}]  {label}")
    print("\n    [q]  Quit")
    print()


def get_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print(
            "\nERROR: ANTHROPIC_API_KEY is not set.\n"
            "Copy .env.example to .env and add your key, or export it:\n"
            "  export ANTHROPIC_API_KEY=sk-ant-...\n"
        )
        sys.exit(1)
    return anthropic.Anthropic(api_key=api_key)


def run_example(key: str, client: anthropic.Anthropic) -> None:
    if key not in EXAMPLES:
        print(f"Unknown example: {key!r}")
        return

    label, module_path, func_name = EXAMPLES[key]
    print(f"\nRunning: {label}\n")

    import importlib
    module = importlib.import_module(module_path)
    func = getattr(module, func_name)
    func(client)


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-Agent Framework examples")
    parser.add_argument(
        "--example", "-e",
        choices=["1", "2", "3"],
        help="Example number to run directly (1, 2, or 3)",
    )
    args = parser.parse_args()

    client = get_client()

    if args.example:
        run_example(args.example, client)
        return

    # Interactive menu
    while True:
        print_menu()
        choice = input("  Enter choice: ").strip().lower()

        if choice == "q":
            print("Goodbye!")
            break
        elif choice in EXAMPLES:
            run_example(choice, client)
        else:
            print(f"  Invalid choice: {choice!r}")


if __name__ == "__main__":
    main()
