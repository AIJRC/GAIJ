# from fastapi import APIRouter, Request, Form
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates

# router = APIRouter()

# # Initialize templates
# templates = Jinja2Templates(directory="app/templates")

# @router.get("/", response_class=HTMLResponse)
# def show_visualize_form(request: Request):
#     return templates.TemplateResponse("visualize.html", {"request": request})

# @router.post("/")
# async def visualize_nodes(
#     company_id: str = Form(None),
#     property_key: str = Form(None),
#     property_value: str = Form(None)
# ):
#     # Fetch a subgraph based on criteria
#     result = await get_subgraph(company_id, property_key, property_value)
#     return {
#         "status": "Visualization complete",
#         "company_id": company_id,
#         "property_key": property_key,
#         "property_value": property_value,
#         "result": result,
#     }


from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.neo4j_service import get_subgraph

router = APIRouter()

# Initialize templates
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def show_visualize_form(request: Request):
    return templates.TemplateResponse("visualize.html", {"request": request})


@router.post("/")
async def visualize_nodes(
    visualization_type: str = Form(...),
    limit_entries: int = Form(None),
    node_ids: str = Form(None),
    property_key: str = Form(None),
    property_value: str = Form(None),
    relationship_type: str = Form(None),
):
    # Handle different visualization types
    if visualization_type == "full_graph":
        # Return a mock result for full graph with optional limit
        result = {"type": "full_graph", "limit": limit_entries}
    elif visualization_type == "single_node":
        # Return a mock result for single node
        node_list = node_ids.split(",") if node_ids else []
        result = {"type": "single_node", "nodes": node_list}
    elif visualization_type == "property_value":
        # Return a mock result for property-based visualization
        result = {"type": "property_value", "property_key": property_key, "property_value": property_value}
    elif visualization_type == "relationship_type":
        # Return a mock result for relationship-based visualization
        result = {"type": "relationship_type", "relationship_type": relationship_type}
    else:
        result = {"error": "Invalid visualization type"}

    return {
        "status": "Visualization ready",
        "visualization_type": visualization_type,
        "result": result,
    }
