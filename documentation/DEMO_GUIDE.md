# Live evaluation demonstration

Use non-sensitive sample data. Configure `.env`, start `python run.py`, and open the local dashboard. A key configured indicator means only that a key exists. A returned draft and metadata demonstrate a completed Gemini call.

1. **Generate (about 60 seconds).** Open AI Email Generator, click Try a sample, and show recipient, purpose and tone. Click Generate email. Check the extension request, Friday deadline, greeting, subject and closing. Show intent and explanations. Do not claim the email was sent.
2. **Grammar (about 45 seconds).** Open Grammar Correction and use its sample. Click Correct grammar. Check subject-verb agreement, tense, spelling and punctuation. Verify the model preserved the late-submission meaning rather than adding excuses.
3. **Improve (about 45 seconds).** Open Writing Improvement and load the sample. Click Improve writing. Compare the repeated requests for data with the clearer version. Confirm Wednesday remains the deadline.
4. **Tone (about 45 seconds).** Open Tone Adjustment, use the sample and select Formal. Click Transform tone. Confirm the casual meeting request becomes formal while keeping Thursday at 3 unchanged.
5. **Reply (about 60 seconds).** Open Smart Reply Generator, use the sample and inspect both incoming email and response intent. Generate. Verify the reply proposes Wednesday at 2 PM instead of accepting Tuesday at 10 AM.
6. **Productivity (about 45 seconds).** Copy a result, download TXT, request two alternatives in a new generation, switch drafts without another request, and revisit Dashboard history. Explain that refresh clears tab memory.
7. **Architecture (about 45 seconds).** Show `app/services.py`, `app/prompts.py` and `.env.example` without exposing `.env`. Explain the official SDK call, structured schema, output limits, one request per action and safe quota handling.

## Evaluation rubric

Assess each real result on intent preservation, factual consistency, subject relevance, tone suitability, grammar and clarity. Record observations rather than invented accuracy scores. Generation is nondeterministic, so exact wording will vary. AI explanations are generated summaries, not a verified audit of every edit.

## Evidence

The CLI demo prints all five actual model results and associated request metadata. Local request IDs are application identifiers, not cryptographic evidence. Provider response IDs are included when supplied by the SDK. Capture UI screenshots after successful live generation if the college requires evidence of outputs.

The delivered screenshots show the real UI and sample input states. They are **not evidence of successful live generation**. No key was supplied during construction. No sample output is preloaded into the app.
