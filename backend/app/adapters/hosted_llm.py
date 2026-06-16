"""
Hosted LLM adapter stub.
Set LLM_PROVIDER=hosted in .env to use this instead of Ollama.
Replace the NotImplementedError bodies with calls to your cloud LLM endpoint.
"""
from backend.app.interfaces.llm_client import AttachmentContent, ExtractionResult, IntentResult


class HostedLLMClient:

    def classify_intent(self, thread_text: str, recipients: list[str]) -> IntentResult:
        # TODO: POST to hosted LLM endpoint with intent classification prompt
        raise NotImplementedError('Hosted LLM not configured. Set LLM_PROVIDER=ollama or implement this method.')

    def extract(self, thread_text: str, attachments: list[AttachmentContent]) -> ExtractionResult:
        # TODO: POST to hosted LLM endpoint with extraction prompt
        raise NotImplementedError('Hosted LLM not configured. Set LLM_PROVIDER=ollama or implement this method.')

    def describe_image(self, image_bytes: bytes, hint: str = '') -> str:
        # TODO: POST to hosted vision LLM endpoint with base64 image
        raise NotImplementedError('Hosted LLM not configured. Set LLM_PROVIDER=ollama or implement this method.')
