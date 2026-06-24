"""
Cross-layer consistency checks.
Each function returns a list of issues found.
Empty list = no issues.
"""

def check_api_vs_db(api_schema: dict, db_schema: dict) -> list[str]:
    issues = []

    # Build a flat set of all column names across all tables
    all_columns = set()
    for table in db_schema.get("tables", []):
        for col in table.get("columns", []):
            all_columns.add(col["name"].lower())

    # Check every API endpoint's request and response fields
    for endpoint in api_schema.get("endpoints", []):
        path = endpoint.get("path", "unknown")

        for field in endpoint.get("request_body", {}).keys():
            if field.lower() not in all_columns and field not in ["password", "token", "confirm_password"]:
                issues.append(f"API endpoint {path} has request field '{field}' not found in any DB table")

        for field in endpoint.get("response", {}).keys():
            if field.lower() not in all_columns and field not in ["token", "message", "success", "data"]:
                issues.append(f"API endpoint {path} has response field '{field}' not found in any DB table")

    return issues


def check_ui_vs_api(ui_schema: dict, api_schema: dict) -> list[str]:
    issues = []

    # Build set of all API endpoint paths
    api_paths = set()
    for ep in api_schema.get("endpoints", []):
        method = ep.get("method", "").upper()
        path = ep.get("path", "")
        api_paths.add(f"{method} {path}")
        api_paths.add(f"{method} /api{path}")

    # Build map of API fields per endpoint
    api_fields_map = {}
    for ep in api_schema.get("endpoints", []):
        key = ep.get("path", "")
        api_fields_map[key] = set(ep.get("request_body", {}).keys())

    # Check UI forms
    for page in ui_schema.get("pages", []):
        for component in page.get("components", []):
            if component.get("type") == "form":
                action = component.get("submit_action", "")
                ui_fields = {f["name"] for f in component.get("fields", [])}

                # Try to find matching API endpoint
                matched = False
                for api_path, api_fields in api_fields_map.items():
                    if api_path in action or action.endswith(api_path):
                        matched = True
                        for field in ui_fields:
                            if field not in api_fields and field not in ["confirm_password", "remember_me"]:
                                issues.append(
                                    f"UI form in {page['name']} has field '{field}' not in API endpoint {api_path}"
                                )

    return issues


def check_auth_vs_api(auth_schema: dict, api_schema: dict) -> list[str]:
    issues = []

    api_paths = set()
    for ep in api_schema.get("endpoints", []):
        api_paths.add(ep.get("path", ""))

    defined_roles = set(auth_schema.get("roles", []))

    for guard in auth_schema.get("guards", []):
        route = guard.get("route", "")
        for role in guard.get("roles", []):
            if role not in defined_roles:
                issues.append(f"Guard on route '{route}' references undefined role '{role}'")

    for role in auth_schema.get("permissions", {}).keys():
        if role not in defined_roles:
            issues.append(f"Permission defined for undefined role '{role}'")

    return issues


def run_all_checks(schemas: dict) -> list[str]:
    issues = []

    ui = schemas.get("ui_schema", {})
    api = schemas.get("api_schema", {})
    db = schemas.get("db_schema", {})
    auth = schemas.get("auth_schema", {})

    issues += check_api_vs_db(api, db)
    issues += check_ui_vs_api(ui, api)
    issues += check_auth_vs_api(auth, api)

    return issues