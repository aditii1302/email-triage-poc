import json
import re
import requests
from backend.app.config import settings
from backend.app.interfaces.llm_client import (
    AttachmentContent,
    ExtractionResult,
    IntentResult,
)


def _clean_json(text: str) -> str:
    text = re.sub(r"```json|```", "", text).strip()
    return text


def _call_ollama(prompt: str, model: str) -> str:
    response = requests.post(
        f"{settings.OLLAMA_BASE_URL}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["response"]


def _parse_json_with_retry(raw: str, prompt: str, model: str) -> dict:
    try:
        return json.loads(_clean_json(raw))
    except json.JSONDecodeError:
        repair_prompt = (
            f"The following text is not valid JSON. "
            f"Return only valid JSON, no explanation, no markdown:\n{raw}"
        )
        repaired = _call_ollama(repair_prompt, model)
        return json.loads(_clean_json(repaired))


class OllamaLLMClient:

    def classify_intent(
        self,
        thread_text: str,
        recipients: list[str],
    ) -> IntentResult:
        prompt = f"""You are an email triage assistant.
Analyze the following email thread and determine if it requires action from a support team.

Recipients: {', '.join(recipients)}

Email thread:
{thread_text}

Respond with ONLY a JSON object in this exact format:
{{
    "is_actionable": true or false,
    "target_function": "IT_SUPPORT or BUSINESS or NONE",
    "confidence": 0.0 to 1.0,
    "reasoning": "brief explanation"
}}"""

        raw = _call_ollama(prompt, settings.OLLAMA_TEXT_MODEL)
        data = _parse_json_with_retry(raw, prompt, settings.OLLAMA_TEXT_MODEL)
        return IntentResult(**data)

    def extract(
        self,
        thread_text: str,
        attachments: list[AttachmentContent],
    ) -> ExtractionResult:
        attachment_text = ""
        if attachments:
            attachment_text = "\n\nAttachment contents:\n" + "\n".join(
                f"--- {a.filename} ---\n{a.content}" for a in attachments
            )

        prompt = f"""You are an email triage assistant.
Extract structured information from the following support email thread.

Email thread:
{thread_text}
{attachment_text}

Respond with ONLY a JSON object in this exact format:
{{
    "problem_statement": "1-2 sentence summary of the issue",
    "impacted_application": "name of the affected application or null",
    "impacted_business_unit": "business unit or null",
    "error_details": "any error codes or messages or null",
    "affected_users": ["list of affected user emails"],
    "stated_category": "category if mentioned in email or null",
    "extraction_confidence": 0.0 to 1.0
}}"""

        raw = _call_ollama(prompt, settings.OLLAMA_TEXT_MODEL)
        data = _parse_json_with_retry(raw, prompt, settings.OLLAMA_TEXT_MODEL)
        return ExtractionResult(**data)

    def describe_image(
        self,
        image_bytes: bytes,
        hint: str = "",
    ) -> str:
        import base64
        image_b64 = base64.b64encode(image_bytes).decode()
        response = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": settings.OLLAMA_VISION_MODEL,
                "prompt": f"Describe the error shown in this screenshot, including any error codes, application names, and dialog text. {hint}",
                "images": [image_b64],
                "stream": False,
            },
            timeout=120,
        )
        response.raise_for_status()
        return response.json()["response"]
