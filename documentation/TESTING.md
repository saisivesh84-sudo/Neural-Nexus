# Verification record

Date: November 1, 2026. Environment: Windows, Python 3.12, Node 24.

## Completed

- 28 Python tests passed. Tests cover five separate operations reaching the official SDK once, output schema checks, malformed and empty output, invalid input, reply intent validation, no-key behavior, quota/access/model/provider errors, timeout handling, concurrency limit, body-size limit, origin/session protection and privacy headers.
- Isolated JavaScript DOM tests passed for sample inputs, generation response rendering, HTML escaping, two-draft selection, copying, TXT download creation, regeneration, history restoration, error recovery, clear, navigation during an in-flight request, reply intent and history clearing.
- JavaScript syntax checked with Node.
- Browser verification covered the real dashboard and every module, sample loading, character counters, missing-key error, clear and mobile navigation. Desktop and 390-pixel mobile viewport checks found no horizontal overflow in inspected views. Screenshots are actual captures, not design mockups.
- Package creation excludes .env, virtual environments, caches and test-generated content.

The Python tests use SDK mocks only inside tests. JavaScript tests use an isolated DOM and fixture responses only inside tests. The running application has no fake AI mode and no fallback email templates.

## External verification pending

No Gemini API key was supplied. Live AI output quality, actual credentials/model access, latency and quota availability are not verified. Run `scripts/live_demo.py` or the five-step UI demonstration after configuring your key. The CLI stops at the first failure instead of using fake data.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

Optional frontend tests require Node 22.22.2+ or Node 24.15+ (Node 24 recommended):

```powershell
npm install
npm test
```

Node is required only for frontend developer tests, not to run the application. The test library version is pinned. Starlette emits a deprecation warning about its httpx test transport with the current pinned stack; tests still pass.
