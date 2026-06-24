import json

def validate_json(raw: str) -> tuple[bool, dict | None, str | None]:
    """
    Returns (is_valid, parsed_dict, error_message)
    """
    try:
        # Strip markdown code blocks if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            parts = cleaned.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("json"):
                    part = part[4:].strip()
                try:
                    return True, json.loads(part), None
                except:
                    continue

        return True, json.loads(cleaned), None

    except json.JSONDecodeError as e:
        return False, None, f"JSON parse error: {str(e)}"


def extract_json_from_text(text: str) -> tuple[bool, dict | None, str | None]:
    """
    Last resort: try to find JSON object anywhere in the text
    """
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start == -1 or end == 0:
            return False, None, "No JSON object found in text"
        candidate = text[start:end]
        return True, json.loads(candidate), None
    except json.JSONDecodeError as e:
        return False, None, f"Could not extract JSON: {str(e)}"