from backend.analysis.statistics import calculate_statistics
from backend.parser.models import PacketInfo


def create_packet(
    number: int,
    source: str,
    destination: str,
    protocol: str,
    length: int,
    source_port: int | None = None,
    destination_port: int | None = None,
) -> PacketInfo:
    return PacketInfo(
        number=number,
        timestamp=1000.0 + number,
        length=length,
        source=source,
        destination=destination,
        protocol=protocol,
        source_port=source_port,
        destination_port=destination_port,
    )


def test_total_packets_and_bytes():
    packets = [
        create_packet(
            1,
            "192.168.1.10",
            "192.168.1.20",
            "TCP",
            100,
            5000,
            443,
        ),
        create_packet(
            2,
            "192.168.1.20",
            "192.168.1.10",
            "UDP",
            200,
            53,
            5001,
        ),
    ]

    result = calculate_statistics(packets)

    assert result["total_packets"] == 2
    assert result["total_bytes"] == 300


def test_protocol_counts():
    packets = [
        create_packet(1, "10.0.0.1", "10.0.0.2", "TCP", 100),
        create_packet(2, "10.0.0.1", "10.0.0.2", "TCP", 200),
        create_packet(3, "10.0.0.2", "10.0.0.1", "UDP", 150),
        create_packet(4, "10.0.0.2", "10.0.0.1", "ICMP", 80),
    ]

    result = calculate_statistics(packets)

    assert result["protocols"] == {
        "TCP": 2,
        "UDP": 1,
        "ICMP": 1,
    }


def test_top_sources():
    packets = [
        create_packet(1, "192.168.1.10", "8.8.8.8", "TCP", 100),
        create_packet(2, "192.168.1.10", "8.8.8.8", "TCP", 100),
        create_packet(3, "192.168.1.20", "8.8.8.8", "UDP", 100),
    ]

    result = calculate_statistics(packets)

    assert result["top_sources"]["192.168.1.10"] == 2
    assert result["top_sources"]["192.168.1.20"] == 1


def test_top_destinations():
    packets = [
        create_packet(1, "10.0.0.1", "8.8.8.8", "UDP", 100),
        create_packet(2, "10.0.0.2", "8.8.8.8", "UDP", 100),
        create_packet(3, "10.0.0.3", "1.1.1.1", "TCP", 100),
    ]

    result = calculate_statistics(packets)

    assert result["top_destinations"]["8.8.8.8"] == 2
    assert result["top_destinations"]["1.1.1.1"] == 1


def test_top_ports():
    packets = [
        create_packet(
            1,
            "10.0.0.1",
            "10.0.0.2",
            "TCP",
            100,
            5000,
            443,
        ),
        create_packet(
            2,
            "10.0.0.1",
            "10.0.0.2",
            "TCP",
            100,
            5001,
            443,
        ),
        create_packet(
            3,
            "10.0.0.2",
            "10.0.0.1",
            "UDP",
            100,
            53,
            5002,
        ),
    ]

    result = calculate_statistics(packets)

    assert result["top_ports"]["443"] == 2
    assert result["top_ports"]["5000"] == 1
    assert result["top_ports"]["53"] == 1


def test_empty_capture():
    result = calculate_statistics([])

    assert result["total_packets"] == 0
    assert result["total_bytes"] == 0
    assert result["protocols"] == {}
    assert result["top_sources"] == {}
    assert result["top_destinations"] == {}
    assert result["top_ports"] == {}