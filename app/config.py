"""Server-only environment configuration. Never serialize Settings."""
import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / '.env', override=False)


@dataclass(frozen=True)
class Settings:
    api_key: str = field(default_factory=lambda: os.getenv('GEMINI_API_KEY', '').strip(), repr=False)
    model: str = field(default_factory=lambda: os.getenv('GEMINI_MODEL', 'gemini-3.5-flash-lite').strip())
    timeout_seconds: int = field(default_factory=lambda: max(10, min(120, int(os.getenv('AI_TIMEOUT_SECONDS', '60')))))
    max_output_tokens: int = field(default_factory=lambda: max(1024, min(8192, int(os.getenv('MAX_OUTPUT_TOKENS', '4096')))))

    @property
    def configured(self):
        return bool(self.api_key and self.api_key != 'your_gemini_api_key_here')
