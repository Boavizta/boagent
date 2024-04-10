from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "boagent"
    project_version: str = "0.1.0"
    project_description: str = "Boagent is a local API and monitoring agent to help you estimate the environmental impact of your machine, including software activity and hardware embodied impacts."
    tags_metadata: list = [
        {"name": "info", "description": "Returns runtime configuration of Boagent."},
        {"name": "web", "description": "Web UI to explore Boagent metrics."},
        {
            "name": "csv",
            "description": "Internal route. Generates and returns a CSV-formatted dataset with metrics needed by the webUI",
        },
        {
            "name": "metrics",
            "description": "Returns metrics as a Prometheus HTTP exporter.",
        },
        {
            "name": "query",
            "description": "This is the main route. Returns metrics in JSON format.",
        },
    ]
    seconds_in_one_year: int = 31536000
    default_lifetime: float = 5.0
    hardware_file_path: str = "./hardware_data.json"
    power_file_path: str = "./power_data.json"
    hardware_cli: str = "./boagent/hardware/hardware_cli.py"
    boaviztapi_endpoint: str = "http://localhost:5000"
    db_path: str = "../../db/boagent.db"
    public_path: str = "./boagent/public"
    assets_path: str = "./boagent/public/assets/"
    carbon_aware_api_endpoint: str = "https://carbon-aware-api.azurewebsites.net"
    carbon_aware_api_token: str = "token"
    azure_location: str = "northeurope"
