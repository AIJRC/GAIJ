from pydantic import BaseModel
from typing import Optional

class VisualizationRequest(BaseModel):
    company_id: Optional[str]
    property_key: Optional[str]
    property_value: Optional[str]