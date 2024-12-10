import httpx

async def process_companies(request):
    # Interact with the LLM API
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8888/process", json=request.dict())
        return response.json()