"""
Recompute execution accuracy of a benchmark run from the stored generated Cypher queries,
using the reference queries currently in test_set.json. The agent is not invoked again.

Run from the repository root:
    python benchmark/rescore_execution.py benchmark/results/<run>
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from graph import connect_to_neo4j
from run_benchmark import compare, execute_all, run_query


def main(run_dir):
    run_dir = Path(run_dir)
    tests = {t["id"]: t for t in json.load(open("test_set.json"))["tests"]}
    graph = connect_to_neo4j()
    gold = {i: run_query(graph, t["cypher"])[0] if t.get("cypher") else None for i, t in tests.items()}
    records = [json.loads(line) for line in open(run_dir / "runs.jsonl")]
    changed = 0
    for record in records:
        item = tests[record["id"]]
        if item["check"] == "none" or (gold[item["id"]] is None and item["check"] != "abstain"):
            continue
        agent_rows, _, last_rows = execute_all(graph, record["generated_cyphers"])
        match, recall = compare(gold[item["id"]] or [], agent_rows, item["check"], item.get("answer_columns"), last_rows)
        if match != record["execution_match"]:
            changed += 1
            print(f"{record['id']} rep{record['repetition']}: {record['execution_match']} -> {match}")
        record["execution_match"], record["row_recall"] = match, recall
    (run_dir / "runs.jsonl").rename(run_dir / "runs_original.jsonl")
    with open(run_dir / "runs.jsonl", "w") as f:
        f.writelines(json.dumps(r, default=str) + "\n" for r in records)
    print(f"{changed} execution results changed")


if __name__ == "__main__":
    main(sys.argv[1])
