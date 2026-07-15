from fastapi import FastAPI, Request
import httpx
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

app = FastAPI()

TARGET_URL = "https://httpbin.org/post"

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
    async with httpx.AsyncClient() as client:
        response = await client.post(TARGET_URL, json={"message": safe_message})

    return {
        "original_message": user_message,
        "safe_message_sent": safe_message,
        "detected_items": [r.entity_type for r in results],
        "upstream_response": response.json()
    }