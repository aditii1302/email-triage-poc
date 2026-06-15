from typing import Protocol
from pydantic import BaseModel


class IntentResult(BaseModel):
    is_actionable: bool
    target_function: str
    confidence: float
    reasoning: str


class ExtractionResult(BaseModel):
    problem_statement: str
    impacted_application: str | None
    impacted_business_unit: str | None
    error_details: str | None
    affected_users: list[str]
    stated_category: str | None
    extraction_confidence: float


class AttachmentContent(BaseModel):
    filename: str
    content: str


class LLMClient(Protocol):
    def classify_intent(
        self,
        thread_text: str,
        recipients: list[str]
    ) -> IntentResult: ...

    def extract(
        self,
        thread_text: str,
        attachments: list[AttachmentContent]
    ) -> ExtractionResult: ...

    def describe_image(
        self,
        image_bytes: bytes,
        hint: str
    ) -> str: ...
