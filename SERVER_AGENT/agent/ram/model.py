from dataclasses import dataclass
from typing import Optional


# TODO: To be replaced by ComponentRAM from openapi client.

@dataclass()
class MemoryDevice:
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    size_gb: Optional[int] = None
    type_: Optional[str] = None
    speed_mt_s: Optional[int] = None
    form_factor: Optional[str] = None

