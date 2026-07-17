from fastapi import FastAPI, Request
import httpx

app = FastAPI()

TARGET_URL = "https://postman-echo.com/post"

@app.post("/chat")
async def proxy_chat(request: Request):
    body = await request.json()

    # Pass through UNCHANGED - no masking, no modification
    async with httpx.AsyncClient() as client:
        response = await client.post(TARGET_URL, json=body)

    return response.json()