import json
import time
from config import BIG_MODEL
from utils.groq_retry import call_groq_with_retry

SYSTEM_PROMPT = """You are a schema refinement engine for a software compiler.

You receive all 4 schemas and must check and fix cross-layer inconsistencies.

Return ONLY valid JSON with the same structure as input, no explanation, no markdown, no backticks.

Check these rules:
1. Every UI form field must exist in the corresponding API request_body
2. Every API request_body field must exist as a column in the correct DB table
3. Every API response field must exist as a column in the correct DB table
4. Every auth guard route must exist in api_schema endpoints
5. Every role in permissions must exist in the roles list
6. Fix any naming mismatches (e.g. user_id vs userId — standardize to snake_case)
7. Add any missing foreign key columns to DB tables
8. Document every fix you make in a "refinement_log" array at the root level

Output structure:
{
  "ui_schema": { ...fixed... },
  "api_schema": { ...fixed... },
  "db_schema": { ...fixed... },
  "auth_schema": { ...fixed... },
  "refinement_log": ["Fixed: added user_id to contacts table", "Fixed: renamed userId to user_id in API"]
}
"""

def run(schemas: dict) -> dict:
    start = time.time()

    response = call_groq_with_retry(
        model=BIG_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Refine and fix these schemas: {json.dumps(schemas)}"}
        ],
        temperature=0.1,
        max_tokens=4000
    )

    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    parsed = json.loads(raw)
    latency = (time.time() - start) * 1000

    return {
        "output": parsed,
        "latency_ms": round(latency, 2),
        "success": True
    }