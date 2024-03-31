import csv
from typing import List, Dict


def generate_csv(businesses: List[Dict], file_path: str):
    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "Business Name",
            "Phone Number",
            "Address",
            "Email",
            "Social Links",
            "Website",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for business in businesses:
            writer.writerow(business)

    return file_path
