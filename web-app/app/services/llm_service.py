# import httpx

# async def process_companies(request):
#     # Interact with the LLM API
#     async with httpx.AsyncClient() as client:
#         response = await client.post("http://localhost:8888/process", json=request.dict())
#         return response.json()
import asyncio
import random

async def process_companies(request):
    # Simulate a random processing time (10-30 seconds)
    processing_time = random.randint(10, 30)
    await asyncio.sleep(processing_time)

    # Mock response after the delay
    return {
        "status": "success",
        "processing_time": processing_time,
        "message": "Properties processed successfully.",
        "request": request,  # Echo the input request
    }
