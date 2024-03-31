from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import FileResponse

from app.core.serivce import process_request
from app.models.schemas import BusinessInput
from app.core.google_api import GooglePlacesAPI
from app.core.data_processing import extract_business_data
from app.core.csv_generator import generate_csv

router = APIRouter()


@router.post("/search", response_class=FileResponse)
async def search_businesses(input_data: BusinessInput):
    location = input_data.location
    business_type = input_data.business_type

    return process_request(location, business_type)
