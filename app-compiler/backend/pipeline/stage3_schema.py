import json
import time
from config import BIG_MODEL
from utils.groq_retry import call_groq_with_retry

SYSTEM_PROMPT = """You are a schema generation engine for a software compiler.

Given an app architecture, generate 4 complete schemas.

Return ONLY valid JSON, no explanation, no markdown, no backticks.

Output this exact structure:
{
  "ui_schema": {
    "pages": [
      {
        "name": "LoginPage",
        "route": "/login",
        "layout": "centered",
        "components": [
          {"type": "form", "id": "login-form", "fields": [{"name": "email", "type": "email", "required": true}, {"name": "password", "type": "password", "required": true}], "submit_action": "POST /api/auth/login"}
        ]
      }
    ]
  },
  "api_schema": {
    "base_url": "/api",
    "auth_method": "JWT",
    "endpoints": [
      {"method": "POST", "path": "/auth/login", "request_body": {"email": "string", "password": "string"}, "response": {"token": "string", "user": "object"}, "status_codes": [200, 401], "middleware": []}
    ]
  },
  "db_schema": {
    "database": "postgresql",
    "tables": [
      {"name": "users", "columns": [{"name": "id", "type": "UUID", "constraints": ["PRIMARY KEY", "DEFAULT gen_random_uuid()"]}, {"name": "email", "type": "VARCHAR(255)", "constraints": ["UNIQUE", "NOT NULL"]}], "indexes": ["email"], "relations": []}
    ]
  },
  "auth_schema": {
    "strategy": "JWT",
    "token_expiry": "24h",
    "roles": ["admin", "user"],
    "permissions": {"admin": ["*"], "user": ["read:own"]},
    "guards": [{"route": "/api/admin/*", "roles": ["admin"]}]
  }
}

Rules:
- UI form fields must match API request_body fields exactly
- API response fields must exist as columns in db_schema tables
- All routes in guards must exist in api_schema endpoints
- Never invent fields not present in the architecture
"""

def run(design: dict) -> dict:
    start = time.time()

    response = call_groq_with_retry(
        model=BIG_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Generate all schemas for this architecture: {json.dumps(design)}"}
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