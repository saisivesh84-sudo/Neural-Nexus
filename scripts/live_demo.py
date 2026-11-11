"""Run five REAL Gemini operations. Requires .env; no mocks or fallback responses."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.config import Settings
from app.services import AIService, ServiceError
from app.schemas import EmailRequest

CASES = [
    ('generate_email', 'Generate', {'text':'Write an email to my professor asking for a two-day extension on the AI assignment because I was unwell. I can submit it by Friday.', 'recipient':'Professor', 'purpose':'Request', 'tone':'Polite'}),
    ('correct_grammar', 'Grammar', {'text':'Dear team, I has finished the report yesterday. Please checks the document and let me knows if there is any mistakes. Thank you for you help.'}),
    ('improve_writing', 'Improve', {'text':'Hi, we need the data. We need it for the report and the report cannot be done without the data. Please send it by Wednesday. Thanks.'}),
    ('adjust_tone', 'Tone', {'text':'Hey, I can’t make the meeting tomorrow. Can we do Thursday at 3 PM instead? Let me know.', 'tone':'Formal'}),
    ('generate_reply', 'Reply', {'text':'Thank you for your application. Can you attend an interview on Tuesday at 10 AM? Please confirm your availability.', 'intent':'Thank them and explain I have an exam. Ask if Wednesday at 2 PM is possible.', 'tone':'Professional'}),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--save', type=Path, help='Explicitly save results to a chosen JSON file. Otherwise no content is written to disk.')
    args = parser.parse_args()
    settings = Settings()
    if not settings.configured:
        print('NOT RUN: Set GEMINI_API_KEY in .env first. No requests were made.')
        return 2
    service = AIService(settings)
    results = []
    for method, label, values in CASES:
        try:
            result = getattr(service, method)(EmailRequest(**values))
            results.append({'operation':label, 'result':result})
            print(f'\nPASS: {label} / {result["meta"]["model"]} / request {result["meta"]["request_id"]}')
            print(json.dumps(result, indent=2, ensure_ascii=True))
        except ServiceError as exc:
            print(f'FAILED: {label}: {exc.message}\nStopped to avoid unnecessary API calls.')
            return 1
    if args.save:
        args.save.parent.mkdir(parents=True, exist_ok=True)
        args.save.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8')
    print('\nAll five real API operations completed. Review semantic accuracy manually.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
