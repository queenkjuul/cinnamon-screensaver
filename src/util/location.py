from dataclasses import dataclass
from typing import NamedTuple, Optional

@dataclass
class LocationData:
    lat: float
    lon: float
    city: Optional[str] = None
    country: Optional[str] = None
    timeZone: Optional[str] = None
    entryText: Optional[str] = None
