from fastapi import FastAPI, Request
import httpx
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

app = FastAPI()

TARGET_URL = "https://postman-echo.com/post"

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

@app.post("/chat")
async def proxy_chat(request: Request):
    body = await request.json()
    user_message = body.get("message", "")

    # Step 1: Find sensitive info in the message
    results = analyzer.analyze(text=user_message, language="en", entities=["CREDIT_CARD", "EMAIL_ADDRESS", "PHONE_NUMBER", "US_SSN", "PERSON", "LOCATION"])

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