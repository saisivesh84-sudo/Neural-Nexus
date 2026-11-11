"""All intelligent operations call Google's official GenAI SDK. No fallback text."""
import time
import uuid
import httpx
from google import genai
from google.genai import types, errors
from pydantic import ValidationError
from .config import Settings
from .prompts import SYSTEM, build_prompt
from .schemas import AIResult, EmailRequest


class ServiceError(Exception):
    def __init__(self, status: int, code: str, message: str):
        self.status, self.code, self.message = status, code, message
        super().__init__(message)


class AIService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def _run(self, operation: str, request: EmailRequest) -> dict:
        if not self.settings.configured:
            raise ServiceError(503, 'not_configured', 'Add GEMINI_API_KEY to the project .env file, then restart the server. No AI request was made.')
        start = time.monotonic()
        try:
            with genai.Client(api_key=self.settings.api_key, http_options=types.HttpOptions(
                timeout=self.settings.timeout_seconds * 1000,
                retry_options=types.HttpRetryOptions(attempts=1),
            )) as client:
                response = client.models.generate_content(
                    model=self.settings.model,
                    contents=build_prompt(operation, request),
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM,
                        temperature=0.2 if operation == 'grammar' else 0.7,
                        max_output_tokens=self.settings.max_output_tokens,
                        response_mime_type='application/json',
                        response_schema=AIResult,
                    ),
                )
            if not response.text:
                raise ServiceError(422, 'no_output', 'Gemini did not return a usable response. Try less sensitive wording or a shorter input.')
            result = AIResult.model_validate_json(response.text)
            if len(result.drafts) != request.alternatives:
                raise ValueError('Unexpected draft count')
            usage = response.usage_metadata
            return {**result.model_dump(), 'meta': {
                'provider': 'Google Gemini', 'model': self.settings.model,
                'request_id': str(uuid.uuid4()),
                'provider_response_id': getattr(response, 'response_id', None),
                'elapsed_ms': round((time.monotonic() - start) * 1000),
                'total_tokens': getattr(usage, 'total_token_count', None),
                'operation': operation,
            }}
        except ServiceError:
            raise
        except errors.APIError as exc:
            print("GEMINI ERROR:", exc.code, exc.message)
            code = exc.code
            if code == 429:
                raise ServiceError(429, 'quota', 'Gemini rate limit or quota reached. Check your Google AI Studio quota or billing, then try again later.') from None
            if code in (401, 403):
                raise ServiceError(503, 'credentials', 'Gemini rejected the credentials or project access. Check the server API key and model permissions.') from None
            if code == 404:
                raise ServiceError(503, 'model', 'The configured Gemini model is unavailable. Set GEMINI_MODEL to a model enabled for your project and restart.') from None
            if code == 400:
                raise ServiceError(422, 'provider_request', 'Gemini could not process this request. Check the configured model supports structured text output, or simplify the input.') from None
            raise ServiceError(503, 'provider_unavailable', 'Gemini is temporarily unavailable. Your content has not been saved. Try again later.') from None
        except (httpx.TimeoutException, TimeoutError):
            raise ServiceError(504, 'timeout', 'The AI request timed out. Try again with a shorter email. No automatic retry was made.') from None
        except (ValidationError, ValueError):
            raise ServiceError(502, 'invalid_output', 'Gemini returned an incomplete or invalid result. Try again or request one draft with shorter input.') from None
        except Exception:
            # Deliberately never expose SDK messages, credentials, or submitted content.
            raise ServiceError(503, 'connection', 'Unable to complete the AI request. Check internet access and server configuration, then try again.') from None

    def generate_email(self, request):
        return self._run('generate', request)

    def correct_grammar(self, request):
        return self._run('grammar', request)

    def improve_writing(self, request):
        return self._run('improve', request)

    def adjust_tone(self, request):
        return self._run('tone', request)

    def generate_reply(self, request):
        return self._run('reply', request)
