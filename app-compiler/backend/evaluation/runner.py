import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation.test_prompts import ALL_PROMPTS
from pipeline import stage1_intent, stage2_design, stage3_schema, stage4_refine
from validation.cross_layer import run_all_checks
from validation.repair_engine import repair_cross_layer_issues
import json


def run_single(prompt: str) -> dict:
    start = time.time()
    repairs = 0
    failure_types = []

    try:
        r1 = stage1_intent.run(prompt)
        if not r1["output"] or r1["output"].get("too_vague"):
            return {
                "status": "failed",
                "failure_types": ["too_vague"],
                "latency_ms": round((time.time() - start) * 1000, 2),
                "repairs": 0
            }

        r2 = stage2_design.run(r1["output"])
        if not r2["output"]:
            return {
                "status": "failed",
                "failure_types": ["design_failed"],
                "latency_ms": round((time.time() - start) * 1000, 2),
                "repairs": 0
            }

        r3 = stage3_schema.run(r2["output"])
        if not r3["output"]:
            return {
                "status": "failed",
                "failure_types": ["schema_failed"],
                "latency_ms": round((time.time() - start) * 1000, 2),
                "repairs": 0
            }

        issues = run_all_checks(r3["output"])
        if issues:
            repairs += len(issues)
            success, fixed = repair_cross_layer_issues(r3["output"], issues)
            if success:
                r3["output"] = fixed
            else:
                failure_types.append("cross_layer_repair_failed")

        r4 = stage4_refine.run(r3["output"])
        latency = round((time.time() - start) * 1000, 2)
        unrecovered = [f for f in failure_types if "failed" in f]

        return {
            "status": "success" if not unrecovered else "partial_success",
            "failure_types": failure_types,
            "latency_ms": latency,
            "repairs": repairs
        }

    except Exception as e:
        return {
            "status": "failed",
            "failure_types": [str(e)],
            "latency_ms": round((time.time() - start) * 1000, 2),
            "repairs": 0
        }


def run_evaluation() -> dict:
    results = []
    for item in ALL_PROMPTS:
        print(f"Running {item['id']}/{len(ALL_PROMPTS)}: {item['prompt'][:50]}...")
        result = run_single(item["prompt"])
        results.append({**item, **result})

    total = len(results)
    success = sum(1 for r in results if r["status"] == "success")
    partial = sum(1 for r in results if r["status"] == "partial_success")
    failed = sum(1 for r in results if r["status"] == "failed")
    avg_latency = sum(r.get("latency_ms", 0) for r in results) / total
    total_repairs = sum(r.get("repairs", 0) for r in results)

    return {
        "summary": {
            "total": total,
            "success": success,
            "partial_success": partial,
            "failed": failed,
            "success_rate": round(success / total * 100, 1),
            "avg_latency_ms": round(avg_latency, 2),
            "total_repairs": total_repairs
        },
        "results": results
    }


if __name__ == "__main__":
    report = run_evaluation()
    print(json.dumps(report["summary"], indent=2))
    with open("evaluation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("Saved to evaluation_report.json")