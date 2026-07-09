from enum import Enum
from typing import List, Union
from boagent.api.models import WorkloadTime

type TimeWorkload = Union[
    dict[str, float], dict[str, List[dict[str, WorkloadTime]]], None
]
type AveragePower = Union[float, None]

MetricType = Enum("Metric", [("Gauge", "gauge"), ("Counter", "counter")])
CriteriaChoice = Enum(
    "CriteriaChoice", [("MainCriteria", "main"), ("AllCriteria", "all")]
)
