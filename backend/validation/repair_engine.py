import json
import time
from config import BIG_MODEL, SMALL_MODEL, MAX_REPAIR_ATTEMPTS
from validation.json_validator import validate_json, extract_json_from_text
from utils.groq_retry import call_groq_with_retry


def _call_with_retry(model: str, messages: list, temperature: float = 0.0, max_tokens: int = 4000) -> str:
    """Call the Groq API with retry and return just the text content."""
    response = call_groq_with_retry(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content.strip()


def repair_json(broken_text: str, stage_name: str) -> tuple[bool, dict | None]:
    """
    Try to fix broken JSON output from a stage.
    Returns (success, parsed_dict)
    """
    prompt = f"""The following output from the {stage_name} stage is not valid JSON.
Fix it and return ONLY valid JSON, no explanation, no markdown, no backticks.

Broken output:
{broken_text}
"""
    for attempt in range(MAX_REPAIR_ATTEMPTS):
        raw = _call_with_retry(
            model=SMALL_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        is_valid, parsed, error = validate_json(raw)
        if is_valid:
            return True, parsed

        # Last resort: extract JSON from anywhere in the text
        is_valid, parsed, error = extract_json_from_text(raw)
        if is_valid:
            return True, parsed

    return False, None


def repair_missing_fields(output: dict, missing_fields: list[str], stage_name: str) -> tuple[bool, dict]:
    """
    Re-call the model to add missing required fields to an output.
    """
    prompt = f"""This JSON output from the {stage_name} stage is missing required fields: {missing_fields}

Current output:
{json.dumps(output, indent=2)}

Add the missing fields with appropriate values and return the complete fixed JSON.
Return ONLY valid JSON, no explanation, no markdown, no backticks.
"""
    for attempt in range(MAX_REPAIR_ATTEMPTS):
        raw = _call_with_retry(
            model=BIG_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        is_valid, parsed, error = validate_json(raw)
        if is_valid and parsed:
            return True, parsed

    return False, output


def repair_cross_layer_issues(schemas: dict, issues: list[str]) -> tuple[bool, dict]:
    """
    Fix cross-layer inconsistencies found by cross_layer.py
    """
    if not issues:
        return True, schemas

    issues_text = "\n".join(f"- {issue}" for issue in issues)

    prompt = f"""These cross-layer inconsistencies were found in the generated schemas:

{issues_text}

Here are the current schemas:
{json.dumps(schemas, indent=2)}

Fix ALL the listed issues. Rules:
- Add missing DB columns for any API fields that don't exist in the DB
- Fix UI form fields to match their API endpoints
- Fix auth guard roles to use only defined roles
- Standardize all field names to snake_case
- Add a "refinement_log" array listing every fix you made

Return ONLY the complete fixed schemas as valid JSON, no explanation, no markdown, no backticks.
"""

    for attempt in range(MAX_REPAIR_ATTEMPTS):
        raw = _call_with_retry(
            model=BIG_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        is_valid, parsed, error = validate_json(raw)
        if is_valid and parsed:
            return True, parsed

    return False, schemas