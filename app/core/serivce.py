from app.core.csv_generator import generate_csv
from app.core.data_processing import extract_business_data
from app.core.global_objects import settings
from app.core.google_api import GooglePlacesAPI
from fastapi.responses import FileResponse


def process_request(location: str, business_type: str):
    api = GooglePlacesAPI()
    businesses = api.search_businesses_details(location, business_type)
    print(businesses)
    processed_businesses = [extract_business_data(b) for b in businesses]

    file_path = generate_csv(processed_businesses, settings.base_dir+"output.csv")

    return FileResponse(path=file_path, filename="output.csv", media_type="text/csv")
