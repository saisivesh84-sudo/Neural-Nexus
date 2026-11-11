# NEURAL NEXUS
## AI-Powered Smart Email Assistant

A complete local web application with a custom responsive interface, Python FastAPI backend, and real Gemini integration through Google's official `google-genai` SDK. AI generates every email, correction, rewrite, tone transformation, reply, subject line, and explanation. There is no simulated AI mode.

### Windows quick start (PowerShell)

Install **Python 3.12 (64-bit)** with the Python launcher, then extract the project ZIP and open its `neural-nexus` folder in VS Code. Run these commands in that folder:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

**The single required configuration step:** replace `your_gemini_api_key_here` in `.env` with your own Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey), save, and close the editor. Never paste the key into the browser or commit `.env`.

```powershell
.\.venv\Scripts\python.exe run.py
```

Open **http://127.0.0.1:8000**. Stop with `Ctrl+C`. Activation is not required, so PowerShell execution-policy changes are unnecessary. Do not open `index.html` directly. Internet is needed for dependency installation and Gemini requests.

### What you can demonstrate

| Page | Real AI operation |
|---|---|
| Dashboard | Navigation, quick access and eight recent results in tab memory |
| AI Email Generator | Intent-aware email and subject generation with recipient, purpose and tone |
| Grammar Correction | Spelling, grammar and punctuation corrections that preserve original meaning |
| Writing Improvement | Professional rewriting for clarity, structure and concision |
| Tone Adjustment | Formal, Professional, Friendly, Polite or Casual transformation |
| Smart Reply Generator | Reply generation from incoming email and intended response |
| About | Actual architecture, configuration status, privacy and limitations |

All five AI tools support one or two drafts, AI explanations, communication suggestions, sample inputs, character counts, clear, copy, TXT download and regenerate. Selecting a sample fills only input fields. It never creates an output. Switching drafts, copying, downloading and browsing history make no AI requests. Regenerate explicitly makes a new request using the current form values.

### Configuration

| Setting | Default | Meaning |
|---|---|---|
| `GEMINI_API_KEY` | unset | Required server-only Google API credential |
| `GEMINI_MODEL` | `gemini-3.5-flash-lite` | Configurable stable model with structured text output |
| `AI_TIMEOUT_SECONDS` | `60` | SDK timeout, clamped to 10-120 seconds |
| `MAX_OUTPUT_TOKENS` | `4096` | Output budget, clamped to 1024-8192 |

Restart after editing `.env`. Existing process environment variables override `.env`. The model default follows Google's current model documentation checked on November 1, 2026. Availability, quota and pricing depend on your Google project and can change. A configured key indicator does not mean live access has been verified. Only a successful generation verifies access.

### Architecture

```text
Browser: static HTML + CSS + JavaScript modules
    POST /api/{operation} with validated form values
FastAPI: origin/session checks + schema validation + concurrency limit
AIService: dedicated prompt + one official GenAI SDK request
Gemini: intent + email subject/body + explanations + suggestions
AIResult validation -> safe JSON -> text-only browser rendering
```

The backend is deliberately local-only and binds to `127.0.0.1`. It has no database, account system, email integration, sending functionality, background model calls or automatic retries. It is ready for a local college demonstration, not an authenticated public multi-user service.

### Project map

```text
run.py                       Windows/local entry point
app/main.py                  API routes, security and static-file hosting
app/config.py                .env settings
app/schemas.py               Pydantic request/output contracts
app/prompts.py               Five dedicated prompts and shared safeguards
app/services.py              Central Gemini service and sanitized errors
static/index.html            Application shell
static/styles.css            Responsive blue/white design system
static/app.js                Pages, editor state and API interactions
static/icons.js, brand.svg   Original local design assets
tests/test_app.py            Offline contract and failure tests
scripts/live_demo.py         Five-operation genuine AI demonstration
documentation/               PDF report, demo script and testing notes
presentation/                15-slide PowerPoint
screenshots/                 Actual application captures
requirements.txt             Pinned direct runtime dependencies
requirements-lock.txt        Resolved complete runtime dependency versions
requirements-dev.txt         Test dependencies
.env.example                 Configuration template, no real credentials
```

For reproducibility, install `requirements-lock.txt` instead of `requirements.txt`. The lock was resolved and checked on Windows with Python 3.12. Do not copy a virtual environment between machines.

### Automated checks

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

Offline tests replace the SDK only inside tests. They prove request routing, validation, output parsing, secret-safe errors, missing-key handling, headers, and quota/timeout handling. They do not prove live model access or semantic quality.

Optional frontend tests: install Node 24.15+ and run `npm install` followed by `npm test`. Node is not required to run the application.

After configuring your key, run the genuine AI demo (five billable/quota-consuming requests):

```powershell
.\.venv\Scripts\python.exe scripts\live_demo.py
```

The script stops on the first failure and never substitutes a response. It prints live drafts, model name, request identifier and token metadata. To explicitly save evidence:

```powershell
.\.venv\Scripts\python.exe scripts\live_demo.py --save demo-results\live-evidence.json
```

No user key was supplied during delivery. Live Gemini generation is therefore **not verified** in this package. The application, SDK request construction and error behavior are implemented and tested independently. Follow `documentation/DEMO_GUIDE.md` for the five live operations and manual evaluation criteria.

### Privacy, reliability and security

- Email text remains in tab memory, including up to eight recent results. Refreshing clears it. There is no localStorage, sessionStorage or database. Downloaded TXT files and explicitly saved CLI evidence remain on your disk by choice.
- Submitted text is sent to Google for processing, subject to [Gemini API terms](https://ai.google.dev/gemini-api/terms). Local memory-only behavior does not imply Google has no retention policy. Avoid sensitive input in demonstrations.
- Keys stay on the backend. Provider exception bodies are never returned or logged. Input validation messages do not echo submitted text. Uvicorn access logging is disabled in the launcher.
- The backend limits primary input to 6,000 characters, reply intent to 2,000, request bodies to 40 KB, and simultaneous model calls to two. Each click makes one request with no retries.
- Local host validation, same-origin checks and a per-process request token reduce unwanted browser requests. CSP and text escaping prevent AI output from becoming executable HTML.
- AI outputs can still contain errors, unintended assumptions or prompt-injection effects. Prompt safeguards reduce risk but cannot guarantee correctness. Human review remains necessary.

### Troubleshooting

| Symptom | Action |
|---|---|
| `py` is not recognized | Install Python 3.12 with its launcher, then reopen the terminal |
| Setup required | Confirm `.env` is in the same folder as `run.py`, edit the key and restart |
| Rate limit or quota | Check Google AI Studio quota/billing and retry later. The app does not retry automatically |
| Key or model access rejected | Check key restrictions, API access and `GEMINI_MODEL` |
| Incomplete AI result | Shorten input or request one draft. If needed increase the configured output budget |
| Timeout or connection failure | Check internet access, proxy/firewall policy and provider availability |
| Reload session message | Refresh the browser after restarting the backend |
| Port 8000 busy | Stop the previous server or run `.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --no-access-log`, then open port 8001 |
| Clipboard unavailable | Select the output and use `Ctrl+C`, or use TXT download |

### References

- [Google GenAI Python SDK](https://googleapis.github.io/python-genai/)
- [Gemini 3.5 Flash-Lite](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite)
- [Gemini structured outputs](https://ai.google.dev/gemini-api/docs/structured-output)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/latest/)

Team: **NEURAL NEXUS**. Project category: Artificial Intelligence. Domain: Generative AI and Natural Language Processing.
