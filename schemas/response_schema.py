from typing import List
from pydantic import BaseModel, Field

class SourceReference(BaseModel):
    """
    Represents a structured citation linking a piece of information 
    in the final answer back to its original origin.
    """
    document_name: str = Field(
        description="The filename or title of the original source document."
    )
    page_number: int = Field(
        description="The exact page number within the document where the supporting context is located."
    )

class ResponseSchema(BaseModel):
    """
    The validated, user-facing output schema representing the final 
    result of the RAG workflow. This schema guarantees a grounded answer 
    paired with explicit source attribution.
    """
    answer: str = Field(
        description="The final, synthesized answer addressing the user's prompt, grounded entirely in the retrieved context."
    )
    sources: List[SourceReference] = Field(
        description="An exhaustive list of references documenting exactly where the context for the answer was found."
    )