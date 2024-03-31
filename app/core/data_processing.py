from typing import Dict, List
import re


def extract_business_data(business: Dict) -> Dict:
    business_data = {
        "Business Name": business.get("name", ""),
        "Phone Number": business.get("formatted_phone_number", ""),
        "Address": business.get("formatted_address", ""),
        "Email": "",
        "Social Links": [],
        "Website": business.get("website", "")
    }

    website = business_data.get("Website", "")
    business_data["Email"] = extract_email(website)
    business_data["Social Links"] = extract_social_links(website)

    return business_data


def extract_email(website: str) -> str:
    email_pattern = r"[\w\.-]+@[\w\.-]+"
    match = re.search(email_pattern, website)
    return match.group() if match else ""


def extract_social_links(website: str) -> List[str]:
    social_patterns = [
        r"(https?://(www\.)?facebook\.com/[^\s]+)",
        r"(https?://(www\.)?twitter\.com/[^\s]+)",
        r"(https?://(www\.)?instagram\.com/[^\s]+)",
    ]
    social_links = []
    for pattern in social_patterns:
        matches = re.findall(pattern, website)
        social_links.extend(matches)
    return social_links
