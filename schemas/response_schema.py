# Pydantic schemas for structured LLM response
from pydantic import BaseModel, Field
from typing import List

class AnswerSchema(BaseModel):
    answer: str = Field(description="Direct, concise response to the user query based on documentation.")
    citations: List[str] = Field(description="Document sources or section headers used to justify the answer.")
    requires_followup: bool = Field(description="Flag to indicate if further clarification/approval is needed.")
