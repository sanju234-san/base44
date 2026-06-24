import json
import time
from utils.groq_retry import call_groq_with_retry

STAGE2_MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """You are a system architect for a software compiler.

Given structured app intent, generate a complete app architecture.

Return ONLY valid JSON, no explanation, no markdown, no backticks.

Output this exact structure:
{
  "pages": [
    {"name": "LoginPage", "route": "/login", "auth_required": false, "components": ["LoginForm"]}
  ],
  "api_endpoints": [
    {"method": "POST", "path": "/api/auth/login", "description": "Authenticate user", "request_fields": ["email", "password"], "response_fields": ["token", "user"], "auth_required": false, "roles": []}
  ],
  "db_tables": [
    {"name": "users", "fields": [{"name": "id", "type": "uuid", "primary_key": true}, {"name": "email", "type": "string", "unique": true}], "relations": []}
  ],
  "roles_permissions": {
    "admin": ["read", "write", "delete"],
    "user": ["read"]
  },
  "business_logic": [
    "Premium users can access /dashboard/analytics",
    "Admins can delete any record"
  ]
}

Rules:
- Every page must map to at least one API endpoint
- Every API endpoint must reference fields that exist in db_tables
- Include created_at and updated_at in every table
- id field must always be uuid type and primary_key true
- Relations format: {"table": "contacts", "type": "one_to_many", "foreign_key": "user_id"}
"""

def run(intent: dict) -> dict:
    start = time.time()

    response = call_groq_with_retry(
        model=STAGE2_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Generate app architecture for this intent: {json.dumps(intent)}"}
        ],
        temperature=0.1,
        max_tokens=3000
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown code fences if present
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
        "model": STAGE2_MODEL,
        "success": True
    }