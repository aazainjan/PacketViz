from pathlib import Path

from scapy.all import IP, TCP, UDP, ICMP, rdpcap

from .models import PacketInfo


def parse_pcap(file_path: str | Path) -> list[PacketInfo]:
    """
    Parse a PCAP/PCAPNG file into normalized packet information.
    """

    packets = rdpcap(str(file_path))
    results = []

    for number, packet in enumerate(packets, start=1):
        source = None
        destination = None
        protocol = "OTHER"
        source_port = None
        destination_port = None

        if IP in packet:
            source = packet[IP].src
            destination = packet[IP].dst

            if TCP in packet:
                protocol = "TCP"
                source_port = packet[TCP].sport
                destination_port = packet[TCP].dport

            elif UDP in packet:
                protocol = "UDP"
                source_port = packet[UDP].sport
                destination_port = packet[UDP].dport

            elif ICMP in packet:
                protocol = "ICMP"

            else:
                protocol = packet[IP].proto

        results.append(
            PacketInfo(
                number=number,
                timestamp=float(packet.time),
                length=len(packet),
                source=source,
                destination=destination,
                protocol=str(protocol),
                source_port=source_port,
                destination_port=destination_port,
            )
        )

    return results