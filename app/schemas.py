from pydantic import BaseModel
from typing import List, Optional

class EmailRequest(BaseModel):
    email: str

class BulkEmailRequest(BaseModel):
    emails: List[str]

class EmailResponse(BaseModel):
    email: str
    valid_format: bool
    has_mx_records: bool
    is_temp: bool
    domain_exists: bool
    smtp_valid: Optional[bool] = None
    smtp_details: Optional[str] = None
    score: float