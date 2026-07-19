# LLM Guard

LLM Guard is a security layer (reverse proxy) that sits between client applications and Large Language Model (LLM) APIs. It intercepts incoming prompts, applies configurable security checks, and forwards only safe requests to the LLM. This approach helps secure AI applications without modifying the underlying LLM or client application.

## Example Use Case

An enterprise deploys an internal AI assistant connected to their proprietary databases. LLM Guard sits directly in front of the AI model as a reverse proxy. Before any prompt reaches the model, sensitive data such as emails, credit card numbers, and API keys are detected and masked — so if an employee accidentally pastes a customer's email or a leaked API key into a prompt, it never reaches the LLM (or any logs) in raw form.


### ✅ Implemented
- 🔒 **Reverse Proxy** — FastAPI-based `/chat` endpoint that intercepts requests and forwards them to a target LLM/API endpoint
- 👤 **PII Detection & Masking** — powered by [Microsoft Presidio](https://microsoft.github.io/presidio/); detects and masks:
  - Email addresses
  - Credit card numbers
  - Phone numbers
  - SSNs
  - Person names & locations
  - API keys (custom recognizer — OpenAI, Google, GitHub, AWS key formats + generic secret pattern)
- ⚠️ **Error Handling** — graceful handling of upstream timeouts and HTTP errors


## Setup

**Requirements:** Python 3.9+

```bash
git clone https://github.com/AnshGautam11/LLM-Guard.git
cd LLM-Guard/llm-guard
pip install -r requirements.txt
python -m spacy download en_core_web_lg
```

## Running

```bash
python -m uvicorn main:app --reload
```

The proxy will be available at `http://127.0.0.1:8000`.

## Usage

Send a POST request to `/chat`:

$body = @{
>>     message = "My email is john@example.com, card is 4111-1111-1111-1111, and my key is sk-abcdefghijklmnopqrstuvwxyz123456"
>> } | ConvertTo-Json
>> 
>> $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/chat" -Method Post -Body $body -ContentType "application/json"
>> $response | ConvertTo-Json -Depth 5

**Response** includes the original message, the masked version actually sent upstream, which entity types were detected, and the upstream response:

```json
{
  "original_message": "...",
  "safe_message_sent": "My email is <EMAIL_ADDRESS> and my card is <CREDIT_CARD>",
  "detected_items": ["EMAIL_ADDRESS", "CREDIT_CARD"],
  "upstream_response": { ... }
}
```

> **Note:** `TARGET_URL` currently points to `https://postman-echo.com/post`, a test echo endpoint, for development purposes. Replace with your actual LLM API endpoint for production use.

## Project Structure
llm-guard/
├── main.py           # FastAPI proxy + PII detection/masking
├── requirements.txt
└── .gitignore

## Tech Stack

- FastAPI — web framework
- httpx — async HTTP client for forwarding requests
- Microsoft Presidio — PII detection & anonymization
- spaCy — NLP backend for Presidio

## Contributors
