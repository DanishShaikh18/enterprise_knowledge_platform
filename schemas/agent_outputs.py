# Schemas for individual agent outputs
from pydantic import BaseModel, Field

class GuardrailOutput(BaseModel):
    is_compliant: bool = Field(description="True if the input query does not violate enterprise safety guidelines.")
    violation_reason: str = Field(default="", description="Reason for violation if non-compliant.")

class ValidationOutput(BaseModel):
    is_valid: bool = Field(description="True if the answer accurately answers the user query based on contexts.")
    feedback: str = Field(default="", description="Feedback to the agent if response requires modification.")
