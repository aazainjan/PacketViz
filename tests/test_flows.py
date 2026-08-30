from collections import defaultdict
from dataclasses import dataclass

from backend.parser.models import PacketInfo


@dataclass
class NetworkFlow:
    """Represents a bidirectional network conversation."""

    source: str
    destination: str
    protocol: str
    source_port: int | None
    destination_port: int | None
    packets: int
    bytes: int
    start_time: float
    end_time: float

    @property
    def duration(self) -> float:
        """Return the duration of the flow in seconds."""
        return self.end_time - self.start_time


def detect_flows(packets: list[PacketInfo]) -> list[NetworkFlow]:
    """
    Group packets into bidirectional network flows.

    Packets are grouped using:
    - source/destination IP addresses
    - source/destination ports
    - transport protocol

    Traffic in either direction belongs to the same flow.
    """

    flows = defaultdict(list)

    for packet in packets:
        if packet.source is None or packet.destination is None:
            continue

        endpoint_a = (
            packet.source,
            packet.source_port,
        )

        endpoint_b = (
            packet.destination,
            packet.destination_port,
        )

        endpoints = tuple(sorted([endpoint_a, endpoint_b]))

        key = (
            endpoints,
            packet.protocol,
        )

        flows[key].append(packet)

    results = []

    for (endpoints, protocol), flow_packets in flows.items():
        first_packet = flow_packets[0]

        results.append(
            NetworkFlow(
                source=first_packet.source,
                destination=first_packet.destination,
                protocol=protocol,
                source_port=first_packet.source_port,
                destination_port=first_packet.destination_port,
                packets=len(flow_packets),
                bytes=sum(packet.length for packet in flow_packets),
                start_time=min(
                    packet.timestamp for packet in flow_packets
                ),
                end_time=max(
                    packet.timestamp for packet in flow_packets
                ),
            )
        )

    return results