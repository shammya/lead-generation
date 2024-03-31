from pydantic import BaseModel


class BusinessInput(BaseModel):
    location: str
    business_type: str
