from pydantic import BaseModel
from typing import Any, Optional

class GenerateRequest(BaseModel):
    prompt: str

class StageResult(BaseModel):
    output: Optional[dict] = None
    latency_ms: float
    success: bool
    error: Optional[str] = None

class ValidationResult(BaseModel):
    repairs_needed: int
    repairs_successful: int
    failure_types: list[str]

class GenerateResponse(BaseModel):
    status: str  # success | partial_success | failed
    stages: dict[str, StageResult]
    validation: ValidationResult
    metadata: dict[str, Any]