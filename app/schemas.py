from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Operation = Literal['generate', 'grammar', 'improve', 'tone', 'reply']
Tone = Literal['Formal', 'Professional', 'Friendly', 'Polite', 'Casual']


class EmailRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    text: str = Field(min_length=5, max_length=6000)
    intent: str = Field(default='', max_length=2000)
    tone: Tone = 'Professional'
    recipient: Literal['Colleague', 'Professor', 'Manager', 'Client', 'Recruiter', 'Friend', 'Other'] = 'Colleague'
    purpose: Literal['General', 'Request', 'Follow-up', 'Application', 'Apology', 'Thank you', 'Invitation'] = 'General'
    alternatives: int = Field(default=1, ge=1, le=2)

    @field_validator('text', 'intent')
    @classmethod
    def reject_control_characters(cls, value):
        if any(ord(c) < 32 and c not in '\n\r\t' for c in value):
            raise ValueError('Use readable text without control characters.')
        return value


class Draft(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    subject: str = Field(min_length=1, max_length=180)
    body: str = Field(min_length=1, max_length=10000)


class AIResult(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    intent: str = Field(min_length=1, max_length=400)
    drafts: list[Draft] = Field(min_length=1, max_length=2)
    improvements: list[str] = Field(max_length=5)
    suggestions: list[str] = Field(max_length=3)

    @model_validator(mode='after')
    def limit_explanations(self):
        if any(len(s) > 500 for s in self.improvements + self.suggestions):
            raise ValueError('Explanation too long')
        return self
