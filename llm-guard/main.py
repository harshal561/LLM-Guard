from fastapi import FastAPI, Request
import httpx
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine

app = FastAPI()
TARGET_URL = "https://postman-echo.com/post"

# Initialize Presidio engines
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# Custom recognizer for API keys (OpenAI, Google, GitHub, AWS + generic secrets)
api_key_patterns = [
    Pattern(name="openai_key", regex=r"sk-[A-Za-z0-9]{20,}", score=0.9),
    Pattern(name="google_key", regex=r"AIza[A-Za-z0-9_\-]{35}", score=0.9),
    Pattern(name="github_token", regex=r"gh[pousr]_[A-Za-z0-9]{36,}", score=0.9),
    Pattern(name="aws_access_key", regex=r"AKIA[0-9A-Z]{16}", score=0.9),
    Pattern(name="generic_secret", regex=r"\b[A-Za-z0-9_\-]{32,}\b", score=0.4),
]

api_key_recognizer = PatternRecognizer(
    supported_entity="API_KEY",
    patterns=api_key_patterns
)

analyzer.registry.add_recognizer(api_key_recognizer)


@app.post("/chat")
async def proxy_chat(request: Request):
    body = await request.json()
    user_message = body.get("message", "")

    # Step 1: Find sensitive info in the message
    results = analyzer.analyze(
        text=user_message,
        language="en",
        entities=["CREDIT_CARD", "EMAIL_ADDRESS", "PHONE_NUMBER", "US_SSN", "PERSON", "LOCATION", "API_KEY"]
    )

    # Step 2: Redact/hide it
    anonymized = anonymizer.anonymize(text=user_message, analyzer_results=results)
    safe_message = anonymized.text

    # Step 3: Forward the SAFE version onward
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(TARGET_URL, json={"message": safe_message})
            response.raise_for_status()
            upstream_data = response.json()
    except httpx.TimeoutException:
        return {
            "error": "Upstream API timed out",
            "original_message": user_message,
            "safe_message_sent": safe_message
        }
    except httpx.HTTPStatusError as e:
        return {
            "error": f"Upstream API returned an error: {e.response.status_code}",
            "original_message": user_message,
            "safe_message_sent": safe_message
        }
    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}",
            "original_message": user_message,
            "safe_message_sent": safe_message
        }

    return {
        "original_message": user_message,
        "safe_message_sent": safe_message,
        "detected_items": [r.entity_type for r in results],
        "upstream_response": upstream_data
    }