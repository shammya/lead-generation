from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.core.service.processor import process_request
from app.models.schemas import BusinessInput

router = APIRouter()


@router.post("/search", response_class=FileResponse)
async def search_businesses(input_data: BusinessInput):
    location = input_data.location
    business_type = input_data.business_type

    return process_request(location, business_type)
