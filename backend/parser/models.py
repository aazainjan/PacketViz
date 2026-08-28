from dataclasses import dataclass
from typing import Optional


@dataclass
class PacketInfo:
    """Normalized information extracted from a network packet."""

    number: int
    timestamp: float
    length: int
    source: Optional[str]
    destination: Optional[str]
    protocol: str
    source_port: Optional[int]
    destination_port: Optional[int]