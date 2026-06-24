# Jsonschema contracts for each stage output
# These are the hard rules every stage must satisfy

INTENT_CONTRACT = {
    "type": "object",
    "required": ["entities", "features", "roles", "auth_required", "payment_required", "app_type", "assumptions"],
    "properties": {
        "entities": {"type": "array", "items": {"type": "string"}},
        "features": {"type": "array", "items": {"type": "string"}},
        "roles": {"type": "array", "items": {"type": "string"}},
        "auth_required": {"type": "boolean"},
        "payment_required": {"type": "boolean"},
        "app_type": {"type": "string"},
        "assumptions": {"type": "array"}
    }
}

DESIGN_CONTRACT = {
    "type": "object",
    "required": ["pages", "api_endpoints", "db_tables", "roles_permissions", "business_logic"],
    "properties": {
        "pages": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "route", "auth_required", "components"]
            }
        },
        "api_endpoints": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["method", "path", "description", "request_fields", "response_fields"]
            }
        },
        "db_tables": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "fields"]
            }
        },
        "roles_permissions": {"type": "object"},
        "business_logic": {"type": "array"}
    }
}

SCHEMA_CONTRACT = {
    "type": "object",
    "required": ["ui_schema", "api_schema", "db_schema", "auth_schema"],
    "properties": {
        "ui_schema": {
            "type": "object",
            "required": ["pages"]
        },
        "api_schema": {
            "type": "object",
            "required": ["endpoints", "auth_method"]
        },
        "db_schema": {
            "type": "object",
            "required": ["tables"]
        },
        "auth_schema": {
            "type": "object",
            "required": ["strategy", "roles", "permissions"]
        }
    }
}

REFINED_CONTRACT = {
    "type": "object",
    "required": ["ui_schema", "api_schema", "db_schema", "auth_schema", "refinement_log"],
    "properties": {
        "refinement_log": {"type": "array", "items": {"type": "string"}}
    }
}

# Map stage name to its contract
CONTRACTS = {
    "intent": INTENT_CONTRACT,
    "design": DESIGN_CONTRACT,
    "schema": SCHEMA_CONTRACT,
    "refined": REFINED_CONTRACT
}