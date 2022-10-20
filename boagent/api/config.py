from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    seconds_in_one_year: int = 31536000
    default_lifetime: float = os.getenv("DEFAULT_LIFETIME") if os.getenv("DEFAULT_LIFETIME") else 5.0
    hardware_file_path: str = os.getenv("HARDWARE_FILE_PATH") if os.getenv("HARDWARE_FILE_PATH") else "./hardware_data.json"
    power_file_path: str = os.getenv("POWER_FILE_PATH") if os.getenv("POWER_FILE_PATH") else "./power_data.json"
    hardware_cli: str = os.getenv("HARDWARE_CLI") if os.getenv("HARDWARE_CLI") else "../hardware/hardware.py"
    boaviztapi_endpoint: str = os.getenv("BOAVIZTAPI_ENDPOINT") if os.getenv("BOAVIZTAPI_ENDPOINT") else "http://localhost:5000"
    db_path: str = os.getenv("BOAGENT_DB_PATH") if os.getenv("BOAGENT_DB_PATH") else "../../db/boagent.db"

    class Config:
        env_file = ".env"

settings = Settings()
