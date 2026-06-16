import json
import re
import requests
from pathlib import Path
from backend.app.config import settings
from backend.app.interfaces.llm_client import (
    AttachmentContent,
    ExtractionResult,
    IntentResult,
)

PROMPTS_DIR = Path(__file__).resolve().parents[1] / 'prompts'


def _load_prompt(filename: str) -> str:
    return (PROMPTS_DIR / filename).read_text(encoding='utf-8')


def _clean_json(text: str) -> str:
    text = re.sub(r'```json|```', '', text).strip()
    return text


def _call_ollama(prompt: str, model: str) -> str:
    response = requests.post(
        f'{settings.OLLAMA_BASE_URL}/api/generate',
        json={
            'model': model,
            'prompt': prompt,
            'stream': False,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()['response']


def _parse_json_with_retry(raw: str, model: str) -> dict:
    try:
        return json.loads(_clean_json(raw))
    except json.JSONDecodeError:
        repair_prompt = (
            'The following text is not valid JSON. '
            'Return only valid JSON, no explanation, no markdown backticks:\n' + raw
        )
        repaired = _call_ollama(repair_prompt, model)
        return json.loads(_clean_json(repaired))


class OllamaLLMClient:

    def classify_intent(
        self,
        thread_text: str,
        recipients: list[str],
    ) -> IntentResult:
        template = _load_prompt('intent_v1.txt')
        prompt = template.format(
            recipients=', '.join(recipients),
            thread_text=thread_text,
        )
        raw = _call_ollama(prompt, settings.OLLAMA_TEXT_MODEL)
        data = _parse_json_with_retry(raw, settings.OLLAMA_TEXT_MODEL)
        return IntentResult(**data)

    def extract(
        self,
        thread_text: str,
        attachments: list[AttachmentContent],
    ) -> ExtractionResult:
        if attachments:
            attachment_section = 'Attachment contents:\n' + '\n'.join(
                f'--- {a.filename} ---\n{a.content}' for a in attachments
            )
        else:
            attachment_section = ''

        template = _load_prompt('extraction_v1.txt')
        prompt = template.format(
            thread_text=thread_text,
            attachment_section=attachment_section,
        )
        raw = _call_ollama(prompt, settings.OLLAMA_TEXT_MODEL)
        data = _parse_json_with_retry(raw, settings.OLLAMA_TEXT_MODEL)
        return ExtractionResult(**data)

    def describe_image(
        self,
        image_bytes: bytes,
        hint: str = '',
    ) -> str:
        import base64
        template = _load_prompt('image_description_v1.txt')
        prompt = template.format(hint=hint)
        image_b64 = base64.b64encode(image_bytes).decode()
        response = requests.post(
            f'{settings.OLLAMA_BASE_URL}/api/generate',
            json={
                'model': settings.OLLAMA_VISION_MODEL,
                'prompt': prompt,
                'images': [image_b64],
                'stream': False,
            },
            timeout=120,
        )
        response.raise_for_status()
        return response.json()['response']
