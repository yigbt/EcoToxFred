"""
Recompute goal accuracy of a benchmark run with another judge model, using the stored conversations.
The agent is not invoked again. Results are written to goal_<judge>.jsonl in the run directory.

Run from the repository root:
    python benchmark/rejudge.py benchmark/results/<run> --judge-model gpt-4o
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain_core.messages import messages_from_dict
from openai import AsyncOpenAI
from ragas.llms import llm_factory

from config import config
from graph import connect_to_neo4j
from run_benchmark import build_reference, judge, run_query


async def main(args):
    run_dir = Path(args.run_dir)
    tests = {t["id"]: t for t in json.load(open("test_set.json"))["tests"]}
    graph = connect_to_neo4j()
    gold = {i: run_query(graph, t["cypher"])[0] if t.get("cypher") else None for i, t in tests.items()}
    judge_llm = llm_factory(args.judge_model, client=AsyncOpenAI(api_key=config["OPENAI_API_KEY"]), max_tokens=8192)
    records = [json.loads(line) for line in open(run_dir / "runs.jsonl")]
    if args.only:
        records = [r for r in records if r["id"] in args.only]
    semaphore = asyncio.Semaphore(args.concurrency)

    async def score(record):
        async with semaphore:
            messages = messages_from_dict(json.load(open(run_dir / "messages" / f"{record['id']}_rep{record['repetition']}.json")))
            reference = build_reference(tests[record["id"]], gold[record["id"]])
            try:
                value = await judge(messages, reference, judge_llm) if messages else 0.0
            except Exception as e:
                value = None
                print(f"{record['id']} rep{record['repetition']}: {type(e).__name__}: {e}")
            print(f"{record['id']} rep{record['repetition']}: goal={value}", flush=True)
            return dict(id=record["id"], repetition=record["repetition"], goal_accuracy=value)

    results = await asyncio.gather(*(score(r) for r in records))
    with open(run_dir / f"goal_{args.judge_model}.jsonl", "w") as f:
        f.writelines(json.dumps(r) + "\n" for r in results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run_dir")
    parser.add_argument("--judge-model", default="gpt-4o")
    parser.add_argument("--only", nargs="*")
    parser.add_argument("--concurrency", type=int, default=5)
    asyncio.run(main(parser.parse_args()))
