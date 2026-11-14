"""
Summarize a benchmark run created by run_benchmark.py.

Additional judgements created by rejudge.py are included: goal_<judge>.jsonl with the judge of the run is
treated as a repeated judgement (agreement is reported), any other judge as an alternative judge.
Writes summary_by_category.csv and per_question.csv (Supplementary Table S1) into the run directory.

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


def load_judgements(run_dir, runs, judge_model):
    """Add the goal accuracy of every additional judgement as a column and return the column names."""
    columns = []
    for path in sorted(run_dir.glob("goal_*.jsonl")):
        judge = path.stem.removeprefix("goal_")
        column = "goal_accuracy_repeat" if judge == judge_model else f"goal_accuracy_{judge}"
        extra = pd.DataFrame([json.loads(line) for line in open(path)]).rename(columns={"goal_accuracy": column})
        runs = runs.merge(extra, on=["id", "repetition"], how="left")
        columns.append(column)
    if "goal_accuracy_repeat" in runs:
        both = runs.dropna(subset=["goal_accuracy", "goal_accuracy_repeat"])
        agreement = (both["goal_accuracy"] == both["goal_accuracy_repeat"]).mean()
        print(f"Agreement of repeated {judge_model} judgements: {agreement:.3f} over {len(both)} runs")
    return runs, columns


def main(run_dir):
    run_dir = Path(run_dir)
    meta = json.load(open(run_dir / "meta.json"))
    runs = pd.DataFrame([json.loads(line) for line in open(run_dir / "runs.jsonl")])
    runs, judge_columns = load_judgements(run_dir, runs, meta["judge_model"])
    tests = pd.DataFrame(json.load(open("test_set.json"))["tests"])

    def summarize(group):
        summary = {
            "questions": group["id"].nunique(),
            "runs": len(group),
            "tool_selection": rate(group["tool_correct"]),
            "execution_runs": int(group["execution_match"].notna().sum()),
            "execution_accuracy": rate(group["execution_match"]),
            "goal_accuracy": rate(group["goal_accuracy"]),
            "judge_missing": int(group["goal_accuracy"].isna().sum()),
            "agent_errors": int(group["error"].notna().sum()),
            "median_latency_s": group["latency_s"].median(),
        }
        summary.update({column: rate(group[column]) for column in judge_columns})
        return pd.Series(summary)

    by_category = runs.groupby("category").apply(summarize, include_groups=False)
    by_category = by_category.reindex([c for c in CATEGORY_LABELS if c in by_category.index])
    by_category.loc["overall"] = summarize(runs)
    by_category.to_csv(run_dir / "summary_by_category.csv")

    per_question = runs.groupby("id").agg(
        tool_selection=("tool_correct", rate),
        execution_accuracy=("execution_match", rate),
        goal_accuracy=("goal_accuracy", rate),
        **{column: (column, rate) for column in judge_columns},
        median_latency_s=("latency_s", "median"),
    )
    per_question = tests.set_index("id")[["category", "source", "question", "expected_tools", "cypher"]].join(per_question)
    per_question["expected_tools"] = per_question["expected_tools"].str.join(", ")
    per_question = per_question.rename(columns={"cypher": "reference_cypher"})
    per_question.to_csv(run_dir / "per_question.csv")

    print(json.dumps(meta))
    print(by_category.to_string())
    print(per_question.drop(columns=["question", "reference_cypher"]).to_string())


if __name__ == "__main__":
    main(sys.argv[1])
