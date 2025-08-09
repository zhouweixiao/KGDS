# -*- coding: utf-8 -*-

import re
import json
import math
import argparse
from pathlib import Path
from typing import Any, Union, List, Tuple

# ===== Constants =====
PARADIGM_CHOICES = ("ebs-aos", "abs-aos")
MODEL_CHOICES = sorted([
    "gpt-4o", "gpt-4-turbo", "gpt-4o-mini",
    "claude-3-opus", "claude-3.5-sonnet", "claude-3.5-haiku",
    "gemini-1.5-pro", "llama-3.1-405b", "mistral-large",
    "deepseek-v3", "qwen-max", "glm-4-plus"
])
PROMPT_CHOICES = ("structured-prompt", "self-reflection")

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR.parent / "outputs"

# ===== Utility Functions =====
def load_json(file_path: Union[str, Path]) -> Any:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_sorted_result_files(folder_path: Path) -> Tuple[List[Path], List[int]]:
    def extract_index(path: Path) -> int:
        match = re.match(r"^(\d+)\.", path.name)
        return int(match.group(1)) if match else float("inf")

    files = sorted(folder_path.glob("*result.json"), key=extract_index)
    return files, [extract_index(f) for f in files]

def group_paths(file_paths: List[Path], separator: str) -> List[List[Any]]:
    grouped, current_group, current_key = [], [], None
    for path in file_paths:
        key = path.name.split(separator)[1].split('_')[0]
        if key != current_key:
            if current_group:
                grouped.append(current_group)
            current_group, current_key = [load_json(path)], key
        else:
            current_group.append(load_json(path))
    if current_group:
        grouped.append(current_group)
    return grouped

# ===== Metrics =====
def precision_recall_f1(tp: int, fp: int, fn: int) -> Tuple[float, float, float]:
    recall = tp / (tp + fn) if tp + fn else 0.0
    precision = tp / (tp + fp) if tp + fp else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    return recall, precision, f1

def cal_ebs_rpf1(gold: List[str], pred: List[str]) -> Tuple[float, float, float]:
    if not pred:
        return 0.0, 0.0, 0.0
    gold_set, pred_set = set(gold), set(pred)
    tp = len(gold_set & pred_set)
    fp = len(pred_set - gold_set)
    fn = len(gold_set - pred_set)
    return precision_recall_f1(tp, fp, fn)

def cal_abs_rpf1(gold: dict, pred: list) -> Tuple[float, float, float]:
    fact_labels = [af["type"] for item in (gold["BSPAF"] + gold["BNPAF"]) for af in item["atomic_facts"]]
    pred_labels = [p["Inference_Conclusion"] for sublist in pred for p in sublist]
    assert len(fact_labels) == len(pred_labels), "length mismatch"

    need_recall = fact_labels.count(1)
    actually_recall = sum(f == 1 and p == "knowable" for f, p in zip(fact_labels, pred_labels))
    recall_unsup = sum(f == 0 and p == "knowable" for f, p in zip(fact_labels, pred_labels))

    recall = actually_recall / need_recall if need_recall else 0.0
    precision = actually_recall / (recall_unsup + actually_recall) if (recall_unsup + actually_recall) else 0.0
    return recall, precision, (2 * precision * recall / (precision + recall) if precision + recall else 0.0)

def cal_aos_r(ver_res: List[str]) -> float:
    return ver_res.count("knowable") / len(ver_res) if ver_res else 0.0

def geometric_mean(numbers: List[float]) -> float:
    if not numbers:
        raise ValueError("Input list cannot be empty.")
    if any(x < 0 for x in numbers):
        raise ValueError("All numbers must be non-negative.")
    return math.prod(numbers) ** (1 / len(numbers))

def macro_average(data: List[List[float]]) -> List[float]:
    if not data or not all(len(row) == len(data[0]) for row in data):
        raise ValueError("All sublists must have the same length.")
    num_rows = len(data)
    return [round(sum(row[i] * 100 for row in data) / num_rows, 2) for i in range(len(data[0]))]

# ===== Main Evaluation =====
def run_evaluation(cfg: argparse.Namespace) -> List[float]:
    benchmark = load_json(cfg.benchmark_path)
    model_files, indices = get_sorted_result_files(cfg.model_output_path)
    benchmark_filtered = [benchmark[i - 1] for i in indices]

    if cfg.paradigm == "ebs-aos":
        model_data = [load_json(f) for f in model_files]
    else:
        fact_groups = group_paths(get_sorted_result_files(cfg.fact_ver_path)[0], "abs-")
    opinion_groups = group_paths(get_sorted_result_files(cfg.opinion_ver_path)[0], "aos-")

    results = []
    if cfg.paradigm == "ebs-aos":
        assert len(benchmark_filtered) == len(model_data) == len(opinion_groups), "length mismatch"
        for bench, model, opinion in zip(benchmark_filtered, model_data, opinion_groups):
            ebs_r, ebs_p, ebs_f1 = cal_ebs_rpf1(
                [f"<Paragraph_{p['paragraph_index']}>" for p in bench["BSP"]],
                model["Extractive_Background_Summary"]
            )
            aos_r = cal_aos_r([o["Inference_Conclusion"] for o in opinion])
            results.append([ebs_r, ebs_p, ebs_f1, aos_r, geometric_mean([ebs_f1, aos_r])])
    else:
        assert len(benchmark_filtered) == len(fact_groups) == len(opinion_groups), "length mismatch"
        for bench, fact, opinion in zip(benchmark_filtered, fact_groups, opinion_groups):
            abs_r, abs_p, abs_f1 = cal_abs_rpf1(bench, fact)
            aos_r = cal_aos_r([o["Inference_Conclusion"] for o in opinion])
            results.append([abs_r, abs_p, abs_f1, aos_r, geometric_mean([abs_f1, aos_r])])

    return macro_average(results)

# ===== CLI =====
def get_config() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run evaluation for a given model, prompt pattern, and task paradigm.")
    parser.add_argument("--paradigm", type=str, default="ebs-aos", choices=PARADIGM_CHOICES)
    parser.add_argument("--model", type=str, default="gpt-4o", choices=MODEL_CHOICES)
    parser.add_argument("--prompt", type=str, default="structured-prompt", choices=PROMPT_CHOICES)
    args = parser.parse_args()

    args.benchmark_path = BASE_DIR.parent / "benchmark" / "KGDS.json"
    args.model_output_path = OUTPUT_DIR / "paradigms" / args.paradigm / args.prompt / args.model
    if args.paradigm == "abs-aos":
        args.fact_ver_path = OUTPUT_DIR / "verification" / "fact" / args.paradigm / args.prompt / args.model
    args.opinion_ver_path = OUTPUT_DIR / "verification" / "opinion" / args.paradigm / args.prompt / args.model
    return args

# ===== Pretty Print =====
def print_table(headers: List[str], values: List[str], first_col_label: str = "Percentage (%)", color_numbers: bool = True) -> None:
    values[0] = first_col_label

    col_widths = [max(len(str(h)), len(str(v))) for h, v in zip(headers, values)]
    top = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
    mid = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
    bot = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"

    def cell(text: str, width: int, color: bool = False) -> str:
        padded = str(text).center(width)
        return f" \033[92m{padded}\033[0m " if color else f" {padded} "

    print(top)
    print("│" + "│".join(cell(h, w) for h, w in zip(headers, col_widths)) + "│")
    print(mid)
    print("│" + "│".join(cell(v, w, color=(i > 0 and color_numbers)) for i, (v, w) in enumerate(zip(values, col_widths))) + "│")
    print(bot)

def main():
    cfg = get_config()
    results = run_evaluation(cfg)
    label = cfg.paradigm.split('-')[0]

    print(f"\nTask Paradigm : {cfg.paradigm}")
    print(f"Model Name    : {cfg.model}")
    print(f"Prompt Pattern: {cfg.prompt}\n")

    headers = ["Metric", f"{label}_r", f"{label}_p", f"{label}_f1", "aos_r", "plg_gm"]
    values = [""] + [f"{v:.2f}" for v in results]
    print_table(headers, values, first_col_label="Percentage (%)")

if __name__ == "__main__":
    main()
