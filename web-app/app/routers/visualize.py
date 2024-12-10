from fastapi import APIRouter, Depends
from app.services.neo4j_service import get_subgraph

router = APIRouter()

@router.get("/")
async def visualize_nodes(company_id: str = None, property_key: str = None, property_value: str = None):
    # Fetch a subgraph based on criteria
    result = await get_subgraph(company_id, property_key, property_value)
    return result