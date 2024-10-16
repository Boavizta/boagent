from pydantic import BaseModel


class WorkloadTime(BaseModel):
    time_percentage: float = 0.0
    load_percentage: float = 0.0


time_workload_example = {
    "time_workload": [
        {"time_percentage": 50, "load_percentage": 0},
        {"time_percentage": 25, "load_percentage": 60},
        {"time_percentage": 25, "load_percentage": 100},
    ]
}
