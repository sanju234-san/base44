import json
import time
from config import BIG_MODEL, SMALL_MODEL
from utils.groq_retry import call_groq_with_retry

SYSTEM_PROMPT = """You are an intent extraction engine for a software compiler system.

Extract structured intent from a user's natural language app description.

Return ONLY valid JSON, no explanation, no markdown, no backticks.

Output this exact structure:
{
  "entities": ["list of main data models, e.g. User, Contact, Payment"],
  "features": ["list of features, e.g. login, dashboard, role-based access"],
  "roles": ["list of user roles, e.g. admin, user, premium"],
  "auth_required": true,
  "payment_required": false,
  "app_type": "crm | ecommerce | saas | healthcare | education | other",
  "assumptions": ["list of things you assumed because the prompt was vague"]
}

Rules:
- If prompt is too vague (under 5 meaningful words), set a flag: "too_vague": true
- If prompt has conflicting requirements, list them in "conflicts": []
- Always include assumptions array even if empty
- Never add fields not listed above
"""

def run(prompt: str) -> dict:
    start = time.time()

    if not prompt or len(prompt.strip()) < 5:
        return {
            "output": {"too_vague": True, "assumptions": [], "entities": [], "features": [], "roles": [], "auth_required": False, "payment_required": False, "app_type": "other"},
            "latency_ms": 0,
            "success": True
        }

    response = call_groq_with_retry(
        model=SMALL_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Extract intent from this app description: {prompt}"}
        ],
        temperature=0.1,
        max_tokens=1000
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown if model adds it anyway
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