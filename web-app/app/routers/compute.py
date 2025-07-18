import asyncio
from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from uuid import uuid4
from datetime import datetime
from app.services.llm_service import process_companies
import csv
from io import StringIO

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

# In-memory job store
jobs = {}

@router.get("/", response_class=HTMLResponse)
def show_compute_form(request: Request):
    return templates.TemplateResponse("compute.html", {"request": request})

@router.post("/")
async def compute_properties(
    task_name: str = Form(None),  # Optional task name
    properties: str = Form(...),
    company_ids: str = Form(None),
    csv_file: UploadFile = File(None),
):
    # Parse properties
    property_list = []
    for p in properties.split(";"):
        key_value = p.split(":")
        if len(key_value) == 2:
            key, value = key_value
            property_list.append({key.strip(): value.strip()})
    
    # Parse company IDs from text input
    company_list = []
    if company_ids:
        company_list = [c.strip() for c in company_ids.split(",")]

    # Parse company IDs from CSV file
    if csv_file:
        contents = await csv_file.read()
        decoded = contents.decode("utf-8")
        reader = csv.reader(StringIO(decoded))
        for row in reader:
            company_list.extend(row)

    # Remove duplicates and empty values
    company_list = list(filter(None, set(company_list)))

    # Create a new job
    job_id = str(uuid4())
    jobs[job_id] = {
        "start_time": datetime.utcnow(),
        "status": "in progress",
        "name": task_name or None,  # Store task name if provided
    }

    # Trigger the job processing asynchronously
    asyncio.create_task(process_job(job_id, {"companies": company_list, "properties": property_list}))
    return {"job_id": job_id, "task_name": task_name, "status": "Processing started"}


@router.get("/jobs")
async def get_jobs():
    now = datetime.utcnow()
    job_list = []

    for job_id, job_data in jobs.items():
        if job_data["status"] == "complete" and "end_time" in job_data:
            # Calculate elapsed time for completed jobs
            elapsed_time = (job_data["end_time"] - job_data["start_time"]).total_seconds()
        else:
            # Calculate elapsed time for in-progress jobs
            elapsed_time = (now - job_data["start_time"]).total_seconds()

        job_list.append({
            "id": job_id,
            "name": job_data.get("name", None),  # Include task name if available
            "elapsed_time": int(elapsed_time),
            "status": job_data["status"]
        })

    return job_list



async def process_job(job_id, request):
    # Call the LLM service to process companies (includes random delay simulation)
    result = await process_companies(request)

    # Update the job status to complete
    jobs[job_id]["status"] = "complete"
    jobs[job_id]["processing_time"] = result["processing_time"]
    jobs[job_id]["end_time"] = datetime.utcnow()  # Record the end time