from pydantic import BaseSettings

class Settings(BaseSettings):
    seconds_in_one_year: int = 31536000
    default_lifetime: float = 5.0
    hardware_file_name: str = "./hardware_data.json"
    power_file_name: str = "./power_data.json"
    hardware_cli: str = "../hardware/hardware.py"
    boaviztapi_endpoint: str = "http://localhost:5000"

    class Config:
        env_file = ".env"

settings = Settings()
