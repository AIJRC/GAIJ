from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# Import routers
from app.routers import compute, visualize

app = FastAPI()

# Dummy data for node properties and relationships

dummy_node_types = [
    {"name": "Company", "count": 1000},
    {"name": "Person", "count": 30},
]
dummy_node_properties = [
    {"name": "Name", "count": 500},
    {"name": "Address", "count": 450},
    {"name": "Industry", "count": 300},
    {"name": "Location", "count": 400},
]

dummy_relationship_types = [
    {"type": "EMPLOYS", "count": 1200},
    {"type": "PARTNER_WITH", "count": 700},
    {"type": "ACQUIRED", "count": 150},
    {"type": "IS_SUBSIDIARY", "count": 300},
]


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(compute.router, prefix="/compute", tags=["Compute"])
app.include_router(visualize.router, prefix="/visualize", tags=["Visualize"])

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "node_types": dummy_node_types,
        "node_properties": dummy_node_properties,
        "relationship_types": dummy_relationship_types,
        })
