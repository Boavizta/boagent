from pydantic import BaseSettings
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "boagent"
    PROJECT_VERSION: str = "0.1.0"
    seconds_in_one_year: int = 31536000
    default_lifetime: float = os.getenv("DEFAULT_LIFETIME", 5.0)
    hardware_file_path: str = os.getenv("HARDWARE_FILE_PATH", "./hardware_data.json")
    power_file_path: str = os.getenv("POWER_FILE_PATH", "./power_data.json")
    hardware_cli: str = os.getenv("HARDWARE_CLI", "../hardware/hardware.py")
    boaviztapi_endpoint: str = os.getenv("BOAVIZTAPI_ENDPOINT", "http://localhost:5000")
    db_path: str = os.getenv("BOAGENT_DB_PATH", "../../db/boagent.db")
    public_path: str = os.getenv("BOAGENT_PUBLIC_PATH", "../public")
    assets_path: str = os.getenv("BOAGENT_ASSETS_PATH", "../public/assets")
    carbon_aware_api_endpoint: str = os.getenv("CARBON_AWARE_API_ENDPOINT", "https://carbon-aware-api.azurewebsites.net")
    carbon_aware_api_token: str = os.getenv("CARBON_AWARE_API_TOKEN")
    azure_location: str = os.getenv("AZURE_LOCATION", "northeurope")

    class Config:
        env_file = ".env"


settings = Settings()
