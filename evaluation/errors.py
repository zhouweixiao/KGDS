# -*- coding: utf-8 -*-

import argparse
from typing import List, Dict
from collections import Counter
from paradigms import load_json, get_sorted_result_files
from paradigms import PARADIGM_CHOICES, MODEL_CHOICES, PROMPT_CHOICES, OUTPUT_DIR

# ===== Metric =====
def calculate_proportions(items: List[str]) -> Dict[str, float]:
    total = len(items)
    if total == 0:
        return {}

    counts = Counter(items)
    proportions = {k: round((v / total) * 100, 2) for k, v in counts.items()}

    diff = round(100 - sum(proportions.values()), 2)
    if diff:
        min_key = min(proportions, key=proportions.get)
        proportions[min_key] += diff

    return dict(sorted(proportions.items()))

# ===== Main Evaluation =====
def run_evaluation(cfg: argparse.Namespace) -> List[float]:
    model_files, _ = get_sorted_result_files(cfg.opinion_det_path)
    conclusions = [load_json(f)['Detection_Conclusion'] for f in model_files]
    proportions = calculate_proportions(conclusions)

    error_keys = ['Error Type5', 'Error Type4', 'Error Type3', 'Error Type2', 'Error Type1']
    return [proportions.get(k, 0.0) for k in error_keys]

# ===== CLI =====
def get_config() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run evaluation for a given model, prompt pattern, and task paradigm."
    )
    parser.add_argument("--paradigm", default="ebs-aos", choices=PARADIGM_CHOICES)
    parser.add_argument("--model", default="gpt-4o", choices=MODEL_CHOICES)
    parser.add_argument("--prompt", default="structured-prompt", choices=PROMPT_CHOICES)
    args = parser.parse_args()

    args.opinion_det_path = OUTPUT_DIR / "detection" / "opinion" / args.paradigm / args.prompt / args.model
    return args

# ===== Pretty Print =====
def print_table(headers: List[str], values: List[str], first_col_label: str = "Percentage (%)") -> None:
    values[0] = first_col_label
    col_widths = [max(len(str(h)), len(str(v))) for h, v in zip(headers, values)]

    def cell(text: str, width: int, color: bool = False) -> str:
        padded = str(text).center(width)
        return f"\033[92m{padded}\033[0m" if color else padded

    def row(cells: List[str], colors: List[bool] = None) -> str:
        return "│ " + " │ ".join(
            cell(c, w, colors and colors[i]) for i, (c, w) in enumerate(zip(cells, col_widths))
        ) + " │"

    top = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
    mid = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
    bot = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"

    print(top)
    print(row(headers))
    print(mid)
    print(row(values, colors=[False] + [True] * (len(values) - 1)))
    print(bot)

def main():
    cfg = get_config()
    results = run_evaluation(cfg)

    print(f"\nTask Paradigm : {cfg.paradigm}")
    print(f"Model Name    : {cfg.model}")
    print(f"Prompt Pattern: {cfg.prompt}\n")

    headers = ["Metric", "OFI", "OSD", "IRU", "IRIC", "OM"]
    values = [""] + [f"{v:.2f}" for v in results]
    print_table(headers, values)

if __name__ == "__main__":
    main()
