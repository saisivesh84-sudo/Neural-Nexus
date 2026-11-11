from contextlib import asynccontextmanager
import secrets
import threading
from urllib.parse import urlparse
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from .config import ROOT, Settings
from .schemas import EmailRequest, Operation
from .services import AIService, ServiceError

settings = Settings()
service = AIService(settings)
csrf_token = secrets.token_urlsafe(32)
request_gate = threading.BoundedSemaphore(2)
app = FastAPI(title='NEURAL NEXUS API', version='1.0.0', docs_url=None, redoc_url=None)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
        "neural-nexus-6lfb.onrender.com",
    ],
)


@app.middleware('http')
async def security(request: Request, call_next):
    if request.method == 'POST':
        if request.headers.get('x-nexus-token') != csrf_token:
            return JSONResponse({'error': {'code': 'session', 'message': 'Reload this page to renew your session.'}}, status_code=403)
        if request.headers.get('origin') and urlparse(request.headers['origin']).netloc != request.headers.get('host'):
            return JSONResponse({'error': {'code': 'origin', 'message': 'Request origin not allowed.'}}, status_code=403)
        if 'application/json' not in request.headers.get('content-type', ''):
            return JSONResponse({'error': {'code': 'content_type', 'message': 'Send a JSON request.'}}, status_code=415)
        # Count streamed bytes before parsing, including requests without Content-Length.
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > 40000:
                return JSONResponse({'error': {'code': 'too_large', 'message': 'Request is too large. Shorten your input.'}}, status_code=413)
        request._body = bytes(body)
    response = await call_next(request)
    response.headers.update({
        'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff',
        'Referrer-Policy': 'no-referrer', 'X-Frame-Options': 'DENY',
        'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'",
    })
    return response


@app.exception_handler(RequestValidationError)
async def invalid_request(request, exc):
    return JSONResponse({'error': {'code': 'validation', 'message': 'Check all fields: email text must be 5-6,000 characters, reply intent at most 2,000, and draft count 1 or 2.'}}, status_code=422)


@app.exception_handler(ServiceError)
async def service_error(request, exc):
    return JSONResponse({'error': {'code': exc.code, 'message': exc.message}}, status_code=exc.status)


@app.get('/api/status')
def status():
    return {'configured': settings.configured, 'model': settings.model, 'session_token': csrf_token,
            'provider': 'Google Gemini', 'live_verified': False, 'max_input': 6000}


@app.post('/api/{operation}')
def process(operation: Operation, payload: EmailRequest):
    if operation == 'reply' and len(payload.intent) < 5:
        raise ServiceError(422, 'intent', 'Describe your intended reply in at least 5 characters.')
    if not request_gate.acquire(blocking=False):
        raise ServiceError(429, 'busy', 'Two AI requests are already running. Wait for them to finish before trying again.')
    try:
        functions = {'generate': service.generate_email, 'grammar': service.correct_grammar,
                     'improve': service.improve_writing, 'tone': service.adjust_tone, 'reply': service.generate_reply}
        return functions[operation](payload)
    finally:
        request_gate.release()


app.mount('/static', StaticFiles(directory=ROOT / 'static'), name='static')


@app.get('/')
def index():
    return FileResponse(ROOT / 'static' / 'index.html')
