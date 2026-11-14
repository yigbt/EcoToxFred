"""
Summarize a benchmark run created by run_benchmark.py.

Writes summary_by_category.csv, per_question.csv (Supplementary Table S1), and benchmark_table.tex
into the run directory.

Run from the repository root:
    python benchmark/summarize.py benchmark/results/<run>
"""

import json
import sys
from pathlib import Path

import pandas as pd

CATEGORY_LABELS = {
    "general_knowledge": "General knowledge",
    "lookup": "Lookup and aggregation",
    "analytical": "Analytical",
    "workshop": "Workshop-derived",
}


def rate(series):
    """Share of True (or 1.0) values among non-missing values."""
    values = series.dropna().astype(float)
    return values.mean() if len(values) else float("nan")


def summarize(group):
    return pd.Series({
        "questions": group["id"].nunique(),
        "runs": len(group),
        "tool_selection": rate(group["tool_correct"]),
        "execution_runs": int(group["execution_match"].notna().sum()),
        "execution_accuracy": rate(group["execution_match"]),
        "goal_accuracy": rate(group["goal_accuracy"]),
        "judge_missing": int(group["goal_accuracy"].isna().sum()),
        "agent_errors": int(group["error"].notna().sum()),
        "median_latency_s": group["latency_s"].median(),
    })


def percent(value):
    return "--" if pd.isna(value) else f"{100 * value:.0f}"


def main(run_dir):
    run_dir = Path(run_dir)
    runs = pd.DataFrame([json.loads(line) for line in open(run_dir / "runs.jsonl")])
    second = sorted(run_dir.glob("goal_*.jsonl"))
    if second:
        repeat = pd.DataFrame([json.loads(line) for line in open(second[0])])
        runs = runs.merge(repeat.rename(columns={"goal_accuracy": "goal_accuracy_repeat"}), on=["id", "repetition"])
        both = runs.dropna(subset=["goal_accuracy", "goal_accuracy_repeat"])
        agreement = (both["goal_accuracy"] == both["goal_accuracy_repeat"]).mean()
        print(f"Judge agreement ({second[0].name}): {agreement:.3f} over {len(both)} runs; "
              f"repeat goal accuracy {both['goal_accuracy_repeat'].mean():.3f}")
    tests = pd.DataFrame(json.load(open("test_set.json"))["tests"])

    by_category = runs.groupby("category").apply(summarize, include_groups=False)
    by_category = by_category.reindex([c for c in CATEGORY_LABELS if c in by_category.index])
    by_category.loc["overall"] = summarize(runs)
    by_category.to_csv(run_dir / "summary_by_category.csv")

    per_question = runs.groupby("id").agg(
        tool_selection=("tool_correct", rate),
        execution_accuracy=("execution_match", rate),
        goal_accuracy=("goal_accuracy", rate),
        median_latency_s=("latency_s", "median"),
    )
    per_question = tests.set_index("id")[["category", "source", "question", "expected_tools", "cypher"]].join(per_question)
    per_question["expected_tools"] = per_question["expected_tools"].str.join(", ")
    per_question = per_question.rename(columns={"cypher": "reference_cypher"})
    per_question.to_csv(run_dir / "per_question.csv")

    rows = []
    for category, r in by_category.iterrows():
        label = CATEGORY_LABELS.get(category, "Overall")
        rows.append(f"        {label} & {int(r.questions)} & {int(r.runs)} & {percent(r.tool_selection)} & "
                    f"{percent(r.execution_accuracy)} ({int(r.execution_runs)}) & {percent(r.goal_accuracy)} & "
                    f"{r.median_latency_s:.0f} \\\\")
    rows.insert(-1, "        \\midrule")
    table = "\n".join([
        "    \\begin{table}[htbp]",
        "        \\centering",
        "        \\caption{Benchmark results per question category.",
        "        Tool selection, execution accuracy, and goal accuracy are given as percentages of runs; the number of",
        "        runs with a reference query is given in parentheses.",
        "        Latency is the median time in seconds from question to final answer.}",
        "        \\label{tab:benchmark}",
        "        \\begin{tabular}{lrrrrrr}",
        "        \\toprule",
        "        Category & Questions & Runs & Tool selection & Execution accuracy & Goal accuracy & Latency \\\\",
        "        \\midrule",
        *rows,
        "        \\bottomrule",
        "        \\end{tabular}",
        "    \\end{table}",
    ])
    (run_dir / "benchmark_table.tex").write_text(table + "\n")
    print(by_category.to_string())
    print(per_question.drop(columns=["question", "reference_cypher"]).to_string())


if __name__ == "__main__":
    main(sys.argv[1])
