import time
from typing import List, Dict
from googlemaps import Client

from app.core.global_objects import settings


class GooglePlacesAPI:
    def __init__(self):
        self.client = Client(settings.google_places_api_key)

    # def search_businesses(self, location: str, business_type: str):
    #     place = self.client.places(query=business_type, location=location)
    #     place_details = self.client.place(place_id=place_id)
    #
    #     return results["results"]

    # Function to search for businesses and fetch their details with pagination
    def search_businesses_details(self, location: str, business_type: str) -> List[Dict]:
        businesses_details = []

        search_results = self.client.places(query=business_type, location=location)
        businesses_details.extend(self.process_search_results(search_results))

        while 'next_page_token' in search_results:
            time.sleep(2)  # Important: Wait for the next_page_token to become valid
            search_results = self.client.places(query=business_type, location=location,
                                                page_token=search_results['next_page_token'])
            businesses_details.extend(self.process_search_results(search_results))

        return businesses_details

    def process_search_results(self, search_results) -> List[Dict]:
        temp_details = []
        for result in search_results['results']:
            place_id = result['place_id']
            place_details = self.client.place(place_id=place_id)  # Fetch place details

            business_details = {
                'Business Name': place_details['result'].get('name', ''),
                'Phone Number': place_details['result'].get('formatted_phone_number', 'Not available'),
                'Website': place_details['result'].get('website', 'Not available'),
                'Address': place_details['result'].get('formatted_address', 'Not available'),
                "Email": "",
                "Facebook": "",
            }
            temp_details.append(business_details)

        return temp_details
