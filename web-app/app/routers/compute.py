from fastapi import APIRouter, Depends
from app.models.compute_models import ComputeRequest
from app.services.llm_service import process_companies

router = APIRouter()

@router.post("/")
async def compute_properties(request: ComputeRequest):
    # Trigger the LLM processing
    result = await process_companies(request)
    return {"status": "Processing started", "result": result}