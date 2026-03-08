import os

class Settings:
    PROJECT_NAME: str = "Eco-Guard AI"
    API_V1_STR: str = "/api/v1"
    # Placeholder for Earth Engine Project ID
    EE_PROJECT_ID: str = os.getenv("EE_PROJECT_ID", "your-google-cloud-project-id")

settings = Settings()