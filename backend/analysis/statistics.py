from collections import Counter

from backend.parser.models import PacketInfo


def calculate_statistics(packets: list[PacketInfo]) -> dict:
    """Calculate summary statistics for captured network traffic."""

    protocol_counts = Counter(packet.protocol for packet in packets)

    source_counts = Counter(
        packet.source
        for packet in packets
        if packet.source is not None
    )

    destination_counts = Counter(
        packet.destination
        for packet in packets
        if packet.destination is not None
    )

    port_counts = Counter()

    for packet in packets:
        if packet.source_port is not None:
            port_counts[str(packet.source_port)] += 1

        if packet.destination_port is not None:
            port_counts[str(packet.destination_port)] += 1

    return {
        "total_packets": len(packets),
        "total_bytes": sum(packet.length for packet in packets),
        "protocols": dict(protocol_counts),
        "top_sources": dict(source_counts.most_common(10)),
        "top_destinations": dict(destination_counts.most_common(10)),
        "top_ports": dict(port_counts.most_common(10)),
    }