import time
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from models import GenerateRequest
from pipeline import stage1_intent, stage2_design, stage3_schema, stage4_refine
from validation.json_validator import validate_json, extract_json_from_text
from validation.schema_contracts import CONTRACTS
from validation.cross_layer import run_all_checks
from validation.repair_engine import repair_json, repair_missing_fields, repair_cross_layer_issues
import jsonschema

app = FastAPI(title="App Compiler API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def run_stage(stage_fn, input_data, stage_name: str, contract: dict) -> tuple[dict, list[str]]:
    failure_types = []
    repairs_needed = 0
    repairs_successful = 0

    try:
        result = stage_fn(input_data)
        output = result["output"]
        latency = result["latency_ms"]
    except json.JSONDecodeError as e:
        failure_types.append("invalid_json")
        repairs_needed += 1
        try:
            result = stage_fn(input_data)
            output = result["output"]
            latency = result["latency_ms"]
            repairs_successful += 1
        except Exception:
            return {
                "output": None,
                "latency_ms": 0,
                "success": False,
                "error": f"JSON repair failed: {str(e)}",
                "repairs_needed": repairs_needed,
                "repairs_successful": repairs_successful
            }, failure_types
    except Exception as e:
        failure_types.append("stage_exception")
        return {
            "output": None,
            "latency_ms": 0,
            "success": False,
            "error": str(e),
            "repairs_needed": repairs_needed,
            "repairs_successful": repairs_successful
        }, failure_types

    try:
        jsonschema.validate(instance=output, schema=contract)
    except jsonschema.ValidationError as e:
        failure_types.append("schema_validation_failed")
        repairs_needed += 1
        missing = [e.message]
        success, repaired = repair_missing_fields(output, missing, stage_name)
        if success:
            output = repaired
            repairs_successful += 1
        else:
            failure_types.append("repair_failed")

    return {
        "output": output,
        "latency_ms": latency,
        "success": True,
        "error": None,
        "repairs_needed": repairs_needed,
        "repairs_successful": repairs_successful
    }, failure_types


@app.post("/generate")
async def generate(request: GenerateRequest):
    total_start = time.time()
    all_failure_types = []
    total_repairs_needed = 0
    total_repairs_successful = 0

    # Stage 1
    stage1_result, failures = run_stage(
        stage1_intent.run, request.prompt, "intent", CONTRACTS["intent"]
    )
    all_failure_types += failures
    total_repairs_needed += stage1_result.get("repairs_needed", 0)
    total_repairs_successful += stage1_result.get("repairs_successful", 0)

    if not stage1_result["success"] or not stage1_result["output"]:
        return {
            "status": "failed",
            "stages": {"intent": stage1_result},
            "validation": {"repairs_needed": total_repairs_needed, "repairs_successful": total_repairs_successful, "failure_types": all_failure_types},
            "metadata": {"total_latency_ms": round((time.time() - total_start) * 1000, 2), "error": "Pipeline failed at Stage 1"}
        }

    intent = stage1_result["output"]

    if intent.get("too_vague"):
        return {
            "status": "failed",
            "stages": {"intent": stage1_result},
            "validation": {"repairs_needed": 0, "repairs_successful": 0, "failure_types": ["too_vague"]},
            "metadata": {
                "total_latency_ms": round((time.time() - total_start) * 1000, 2),
                "error": "Prompt is too vague. Please describe your app in more detail.",
                "assumptions": []
            }
        }

    # Stage 2
    stage2_result, failures = run_stage(
        stage2_design.run, intent, "design", CONTRACTS["design"]
    )
    all_failure_types += failures
    total_repairs_needed += stage2_result.get("repairs_needed", 0)
    total_repairs_successful += stage2_result.get("repairs_successful", 0)

    if not stage2_result["success"] or not stage2_result["output"]:
        return {
            "status": "failed",
            "stages": {"intent": stage1_result, "design": stage2_result},
            "validation": {"repairs_needed": total_repairs_needed, "repairs_successful": total_repairs_successful, "failure_types": all_failure_types},
            "metadata": {"total_latency_ms": round((time.time() - total_start) * 1000, 2), "error": "Pipeline failed at Stage 2"}
        }

    design = stage2_result["output"]

    # Stage 3
    stage3_result, failures = run_stage(
        stage3_schema.run, design, "schema", CONTRACTS["schema"]
    )
    all_failure_types += failures
    total_repairs_needed += stage3_result.get("repairs_needed", 0)
    total_repairs_successful += stage3_result.get("repairs_successful", 0)

    if not stage3_result["success"] or not stage3_result["output"]:
        return {
            "status": "failed",
            "stages": {"intent": stage1_result, "design": stage2_result, "schema": stage3_result},
            "validation": {"repairs_needed": total_repairs_needed, "repairs_successful": total_repairs_successful, "failure_types": all_failure_types},
            "metadata": {"total_latency_ms": round((time.time() - total_start) * 1000, 2), "error": "Pipeline failed at Stage 3"}
        }

    schemas = stage3_result["output"]

    # Cross-layer check
    issues = run_all_checks(schemas)
    if issues:
        all_failure_types.append("cross_layer_inconsistency")
        total_repairs_needed += len(issues)
        success, schemas = repair_cross_layer_issues(schemas, issues)
        if success:
            total_repairs_successful += len(issues)
        else:
            all_failure_types.append("cross_layer_repair_failed")

    stage3_result["output"] = schemas

    # Stage 4
    stage4_result, failures = run_stage(
        stage4_refine.run, schemas, "refined", CONTRACTS["refined"]
    )
    all_failure_types += failures
    total_repairs_needed += stage4_result.get("repairs_needed", 0)
    total_repairs_successful += stage4_result.get("repairs_successful", 0)

    if not stage4_result["success"] or not stage4_result["output"]:
        all_failure_types.append("refinement_failed")
        final_output = schemas
    else:
        final_output = stage4_result["output"]

    unrecovered = [f for f in all_failure_types if "repair_failed" in f or "exception" in f]
    status = "success" if not unrecovered else "partial_success"

    total_latency = round((time.time() - total_start) * 1000, 2)

    return {
        "status": status,
        "stages": {
            "intent": stage1_result,
            "design": stage2_result,
            "schema": stage3_result,
            "refined": stage4_result
        },
        "final_output": final_output,
        "validation": {
            "repairs_needed": total_repairs_needed,
            "repairs_successful": total_repairs_successful,
            "failure_types": list(set(all_failure_types))
        },
        "metadata": {
            "total_latency_ms": total_latency,
            "assumptions": intent.get("assumptions", []),
            "conflicts": intent.get("conflicts", []),
            "app_type": intent.get("app_type", "unknown")
        }
    }


@app.post("/simulate")
async def simulate(request: Request):
    body = await request.json()
    schema = body.get("schema", {})
    report = []
    issues = []
    score = 0
    total = 0

    db_tables = {t["name"] for t in schema.get("db_schema", {}).get("tables", [])}
    api_endpoints = schema.get("api_schema", {}).get("endpoints", [])
    ui_pages = schema.get("ui_schema", {}).get("pages", [])
    auth_roles = set(schema.get("auth_schema", {}).get("roles", []))

    for ep in api_endpoints:
        total += 1
        path_parts = ep.get("path", "").strip("/").split("/")
        matched = any(part in db_tables or part + "s" in db_tables for part in path_parts)
        if matched:
            score += 1
            report.append(f"✓ {ep['method']} {ep['path']} → DB table resolved")
        else:
            issues.append(f"✗ {ep['method']} {ep['path']} → no matching DB table")

    for page in ui_pages:
        total += 1
        if page.get("route"):
            score += 1
            report.append(f"✓ Page {page['name']} → route {page['route']} defined")
        else:
            issues.append(f"✗ Page {page['name']} has no route")

    permission_roles = set(schema.get("auth_schema", {}).get("permissions", {}).keys())
    for role in permission_roles:
        total += 1
        if role in auth_roles:
            score += 1
            report.append(f"✓ Role '{role}' → permissions defined")
        else:
            issues.append(f"✗ Role '{role}' in permissions but not in roles list")

    for table in schema.get("db_schema", {}).get("tables", []):
        total += 1
        has_pk = any(
            "PRIMARY KEY" in " ".join(col.get("constraints", []))
            for col in table.get("columns", [])
        )
        if has_pk:
            score += 1
            report.append(f"✓ Table '{table['name']}' → primary key present")
        else:
            issues.append(f"✗ Table '{table['name']}' missing primary key")

    success_rate = round((score / total * 100), 1) if total > 0 else 0
    executable = success_rate >= 80

    return {
        "executable": executable,
        "success_rate": success_rate,
        "score": f"{score}/{total}",
        "verdict": "App would boot successfully" if executable else "App has critical issues",
        "checks_passed": report,
        "issues": issues
    }


@app.get("/evaluate")
async def evaluate():
    from evaluation.runner import run_evaluation
    report = run_evaluation()
    return report


@app.get("/health")
def health():
    return {"status": "ok"}