from fastapi import FastAPI
from app.routers import compute, visualize

app = FastAPI()

# Include routers
app.include_router(compute.router, prefix="/compute", tags=["Compute"])
app.include_router(visualize.router, prefix="/visualize", tags=["Visualize"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Web App"}