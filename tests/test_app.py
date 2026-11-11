"""Offline contract tests. SDK mocks are test fixtures, never application fallbacks."""
import json
from types import SimpleNamespace
from unittest.mock import MagicMock
import httpx
import pytest
from fastapi.testclient import TestClient
from google.genai import errors
from app import main
from app.config import Settings
from app.services import AIService, ServiceError
from app.schemas import EmailRequest

client = TestClient(main.app)


def post(operation='generate', data=None, **kwargs):
    headers = {'x-nexus-token': main.csrf_token, **kwargs.pop('headers', {})}
    return client.post('/api/' + operation, json=data or {'text': 'Write a thank-you email.'}, headers=headers, **kwargs)


def fixture_result():
    return {'intent': 'Test fixture', 'drafts': [{'subject': 'Test subject', 'body': 'Test body.'}], 'improvements': ['Test edit.'], 'suggestions': []}


def test_assets_and_privacy_headers():
    response = client.get('/')
    assert response.status_code == 200
    assert 'NEURAL NEXUS' in response.text
    assert response.headers['cache-control'] == 'no-store'
    assert "script-src 'self'" in response.headers['content-security-policy']
    assert client.get('/static/app.js').status_code == 200
    assert client.get('/.env').status_code == 404


def test_status_does_not_expose_key():
    main.settings = Settings(api_key='secret-test-key')
    try:
        response = client.get('/api/status')
        assert response.json()['configured']
        assert 'secret-test-key' not in response.text
    finally:
        main.settings = Settings()


@pytest.mark.parametrize('data', [
    {'text': '    '}, {'text': 'a' * 6001}, {'text': 'valid text', 'tone': 'Angry'},
    {'text': 'valid text', 'alternatives': 3}, {'text': 'valid text', 'extra': 'x'},
    {'text': 'valid text', 'intent': 'a'*2001}, {'text': 'hi\x00there'},
])
def test_invalid_inputs(data):
    r = post(data=data)
    assert r.status_code == 422
    assert 'input' not in r.json().get('detail', {})


def test_reply_requires_intent():
    assert post('reply').status_code == 422


def test_session_origin_and_host():
    assert client.post('/api/generate', json={'text': 'valid input'}).status_code == 403
    assert post(headers={'origin': 'https://example.com'}).status_code == 403
    assert client.get('/', headers={'host': 'attacker.example'}).status_code == 400


def test_payload_limit():
    assert post(data={'text': 'x'*40001}).status_code == 413


def test_missing_key_is_honest(monkeypatch):
    monkeypatch.setattr(main, 'service', AIService(Settings(api_key='')))
    r = post()
    assert r.status_code == 503
    assert r.json()['error']['code'] == 'not_configured'
    assert 'drafts' not in r.json()


@pytest.mark.parametrize('operation,method', [('generate','generate_email'),('grammar','correct_grammar'),('improve','improve_writing'),('tone','adjust_tone'),('reply','generate_reply')])
def test_all_operations_call_sdk_once(monkeypatch, operation, method):
    fake = MagicMock()
    fake.__enter__.return_value = fake
    fake.models.generate_content.return_value = SimpleNamespace(text=json.dumps(fixture_result()), usage_metadata=SimpleNamespace(total_token_count=123), response_id='provider-id')
    factory = MagicMock(return_value=fake)
    monkeypatch.setattr('app.services.genai.Client', factory)
    monkeypatch.setattr(main, 'service', AIService(Settings(api_key='test-only-key')))
    response = post(operation, {'text':'Incoming or original email', 'intent':'Reply with a polite decline'})
    assert response.status_code == 200, response.text
    assert response.json()['meta']['provider'] == 'Google Gemini'
    assert response.json()['meta']['provider_response_id'] == 'provider-id'
    fake.models.generate_content.assert_called_once()
    args = fake.models.generate_content.call_args.kwargs
    assert args['model'] == main.service.settings.model
    assert args['config'].response_mime_type == 'application/json'
    assert 'INPUT DATA' in args['contents']
    assert factory.call_args.kwargs['http_options'].retry_options.attempts == 1


@pytest.mark.parametrize('code,status,error_code', [(429,429,'quota'),(403,503,'credentials'),(404,503,'model'),(400,422,'provider_request'),(503,503,'provider_unavailable')])
def test_provider_errors_are_sanitized(monkeypatch, code, status, error_code):
    fake = MagicMock()
    fake.__enter__.return_value = fake
    fake.models.generate_content.side_effect = errors.APIError(code, {'message':'SECRET_KEY_AND_EMAIL'})
    monkeypatch.setattr('app.services.genai.Client', MagicMock(return_value=fake))
    with pytest.raises(ServiceError) as err:
        AIService(Settings(api_key='test')).generate_email(EmailRequest(text='Please write an email.'))
    assert err.value.status == status and err.value.code == error_code
    assert 'SECRET' not in str(err.value)


@pytest.mark.parametrize('text', ['', '{broken', '{"drafts": []}', json.dumps({**fixture_result(), 'drafts':[{'subject':'','body':'x'}]})])
def test_invalid_ai_output_never_becomes_draft(monkeypatch, text):
    fake = MagicMock()
    fake.__enter__.return_value = fake
    fake.models.generate_content.return_value = SimpleNamespace(text=text)
    monkeypatch.setattr('app.services.genai.Client', MagicMock(return_value=fake))
    with pytest.raises(ServiceError):
        AIService(Settings(api_key='test')).generate_email(EmailRequest(text='Write a polite email.'))


def test_timeout_and_busy(monkeypatch):
    fake = MagicMock()
    fake.__enter__.return_value = fake
    fake.models.generate_content.side_effect = httpx.ReadTimeout('secret')
    monkeypatch.setattr('app.services.genai.Client', MagicMock(return_value=fake))
    with pytest.raises(ServiceError) as err:
        AIService(Settings(api_key='test')).generate_email(EmailRequest(text='Write a polite email.'))
    assert err.value.status == 504
    main.request_gate.acquire(); main.request_gate.acquire()
    try:
        assert post().json()['error']['code'] == 'busy'
    finally:
        main.request_gate.release(); main.request_gate.release()
