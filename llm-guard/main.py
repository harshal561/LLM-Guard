from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import uuid
import time
from datetime import datetime

from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine

from firewall import apply_firewall
from ml_detector import detect_jailbreak


class ChatRequest(BaseModel):
    message: str


app = FastAPI()

TARGET_URL = "https://postman-echo.com/post"

# Initialize Presidio
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# Custom recognizer for API Keys
api_key_patterns = [
    Pattern(name="openai_key", regex=r"sk-[A-Za-z0-9]{20,}", score=0.9),
    Pattern(name="google_key", regex=r"AIza[A-Za-z0-9_\-]{35}", score=0.9),
    Pattern(name="github_token", regex=r"gh[pousr]_[A-Za-z0-9]{36,}", score=0.9),
    Pattern(name="aws_access_key", regex=r"AKIA[0-9A-Z]{16}", score=0.9),
    Pattern(name="generic_secret", regex=r"\b[A-Za-z0-9_\-]{32,}\b", score=0.4),
]

api_key_recognizer = PatternRecognizer(
    supported_entity="API_KEY",
    patterns=api_key_patterns,
)

analyzer.registry.add_recognizer(api_key_recognizer)


@app.get("/")
async def root():
    return {"message": "LLM Guard API is running"}

@app.post("/chat")
async def proxy_chat(request: ChatRequest):

    start_time = time.time()

    user_message = request.message

    # Firewall Check
    is_safe, reason = apply_firewall(user_message)

    if not is_safe:
        return {
            "status": "Blocked",
<<<<<<< HEAD
=======
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
>>>>>>> 0c5d9cc28be49b5a3204758c6f29fdcffde404bf
            "error": "Request blocked by firewall",
            "reason": reason,
        }

    # ML Jailbreak Detection
    ml_prediction = detect_jailbreak(user_message)

    # Detect Sensitive Information
    results = analyzer.analyze(
        text=user_message,
        language="en",
        entities=[
            "CREDIT_CARD",
            "EMAIL_ADDRESS",
            "PHONE_NUMBER",
            "US_SSN",
            "PERSON",
            "LOCATION",
            "API_KEY",
        ],
    )

    # Mask Sensitive Information
    anonymized = anonymizer.anonymize(
        text=user_message,
        analyzer_results=results,
    )

    safe_message = anonymized.text

    # Risk Level
    risk_level = "LOW"

    if len(results) >= 3:
        risk_level = "HIGH"
    elif len(results) >= 1:
        risk_level = "MEDIUM"

    if ml_prediction == "JAILBREAK":
        risk_level = "HIGH"

    # Forward Safe Prompt
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                TARGET_URL,
                json={"message": safe_message},
            )

            response.raise_for_status()
            upstream_data = response.json()

    except httpx.TimeoutException:
        return {
            "status": "Failed",
<<<<<<< HEAD
=======
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
>>>>>>> 0c5d9cc28be49b5a3204758c6f29fdcffde404bf
            "error": "Upstream API timed out",
            "original_message": user_message,
            "safe_message_sent": safe_message,
        }

    except httpx.HTTPStatusError as e:
        return {
            "status": "Failed",
<<<<<<< HEAD
=======
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
>>>>>>> 0c5d9cc28be49b5a3204758c6f29fdcffde404bf
            "error": f"Upstream API returned {e.response.status_code}",
            "original_message": user_message,
            "safe_message_sent": safe_message,
        }

    except Exception as e:
        return {
            "status": "Failed",
<<<<<<< HEAD
=======
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
>>>>>>> 0c5d9cc28be49b5a3204758c6f29fdcffde404bf
            "error": str(e),
            "original_message": user_message,
            "safe_message_sent": safe_message,
        }

    processing_time = round(time.time() - start_time, 4)

    return {
<<<<<<< HEAD
        "status": "Processed Successfully",
=======
        "request_id": str(uuid.uuid4()),
        "status": "Processed Successfully",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "processing_time_seconds": processing_time,
>>>>>>> 0c5d9cc28be49b5a3204758c6f29fdcffde404bf
        "risk_level": risk_level,
        "total_sensitive_items": len(results),
        "original_message": user_message,
        "safe_message_sent": safe_message,
        "detected_items": [r.entity_type for r in results],
        "ml_prediction": ml_prediction,
        "upstream_response": upstream_data,
    }