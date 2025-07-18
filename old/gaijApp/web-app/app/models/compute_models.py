from pydantic import BaseModel
from typing import List

class ComputeRequest(BaseModel):
    companies: List[str]
    properties: List[str]