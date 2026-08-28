from scapy.all import Ether, ICMP, IP, TCP, UDP, wrpcap

from backend.parser.pcap import parse_pcap


def test_parse_tcp_packet(tmp_path):
    """The parser should correctly extract TCP packet information."""

    pcap_file = tmp_path / "tcp.pcap"

    packet = (
        IP(src="192.168.1.10", dst="192.168.1.20")
        / TCP(sport=12345, dport=443)
    )

    wrpcap(str(pcap_file), [packet])

    result = parse_pcap(pcap_file)

    assert len(result) == 1

    parsed = result[0]

    assert parsed.number == 1
    assert parsed.source == "192.168.1.10"
    assert parsed.destination == "192.168.1.20"
    assert parsed.protocol == "TCP"
    assert parsed.source_port == 12345
    assert parsed.destination_port == 443
    assert parsed.length > 0


def test_parse_udp_packet(tmp_path):
    """The parser should correctly extract UDP packet information."""

    pcap_file = tmp_path / "udp.pcap"

    packet = (
        IP(src="10.0.0.1", dst="8.8.8.8")
        / UDP(sport=53000, dport=53)
    )

    wrpcap(str(pcap_file), [packet])

    result = parse_pcap(pcap_file)

    assert len(result) == 1

    parsed = result[0]

    assert parsed.protocol == "UDP"
    assert parsed.source_port == 53000
    assert parsed.destination_port == 53


def test_parse_icmp_packet(tmp_path):
    """The parser should correctly identify ICMP packets."""

    pcap_file = tmp_path / "icmp.pcap"

    packet = IP(
        src="192.168.1.10",
        dst="8.8.8.8",
    ) / ICMP()

    wrpcap(str(pcap_file), [packet])

    result = parse_pcap(pcap_file)

    assert len(result) == 1

    parsed = result[0]

    assert parsed.source == "192.168.1.10"
    assert parsed.destination == "8.8.8.8"
    assert parsed.protocol == "ICMP"
    assert parsed.source_port is None
    assert parsed.destination_port is None


def test_parse_multiple_packets(tmp_path):
    """The parser should preserve packet order and numbering."""

    pcap_file = tmp_path / "multiple.pcap"

    packets = [
        IP(src="192.168.1.10", dst="192.168.1.20")
        / TCP(sport=1000, dport=80),
        IP(src="192.168.1.20", dst="192.168.1.10")
        / UDP(sport=53, dport=5000),
        IP(src="192.168.1.10", dst="8.8.8.8")
        / ICMP(),
    ]

    wrpcap(str(pcap_file), packets)

    result = parse_pcap(pcap_file)

    assert len(result) == 3
    assert [packet.number for packet in result] == [1, 2, 3]
    assert [packet.protocol for packet in result] == ["TCP", "UDP", "ICMP"]


def test_parse_non_ip_packet(tmp_path):
    """The parser should handle packets that do not contain IPv4."""

    pcap_file = tmp_path / "non_ip.pcap"

    packet = Ether(src="00:11:22:33:44:55", dst="ff:ff:ff:ff:ff:ff")

    wrpcap(str(pcap_file), [packet])

    result = parse_pcap(pcap_file)

    assert len(result) == 1

    parsed = result[0]

    assert parsed.source is None
    assert parsed.destination is None
    assert parsed.protocol == "OTHER"
    assert parsed.source_port is None
    assert parsed.destination_port is None


def test_packet_metadata(tmp_path):
    """The parser should preserve basic packet metadata."""

    pcap_file = tmp_path / "metadata.pcap"

    packet = (
        IP(src="10.0.0.1", dst="10.0.0.2")
        / TCP(sport=5000, dport=80)
    )

    wrpcap(str(pcap_file), [packet])

    result = parse_pcap(pcap_file)

    parsed = result[0]

    assert parsed.number == 1
    assert isinstance(parsed.timestamp, float)
    assert parsed.timestamp > 0
    assert isinstance(parsed.length, int)
    assert parsed.length > 0