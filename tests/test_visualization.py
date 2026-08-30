import pytest

from backend.analysis.flows import NetworkFlow
from backend.analysis.visualization import render_flows_svg


def create_flow(
    source: str = "192.168.1.10",
    destination: str = "192.168.1.20",
    protocol: str = "TCP",
    packets: int = 3,
    bytes_: int = 260,
) -> NetworkFlow:
    return NetworkFlow(
        source=source,
        destination=destination,
        protocol=protocol,
        source_port=50000,
        destination_port=443,
        packets=packets,
        bytes=bytes_,
        start_time=1.0,
        end_time=1.2,
    )


def test_render_single_flow():
    svg = render_flows_svg([create_flow()])

    assert svg.startswith("<svg")
    assert svg.endswith("</svg>")

    assert "192.168.1.10" in svg
    assert "192.168.1.20" in svg
    assert "TCP" in svg
    assert "3 packets" in svg
    assert "260 bytes" in svg


def test_render_multiple_flows():
    flows = [
        create_flow(),
        create_flow(
            source="10.0.0.1",
            destination="8.8.8.8",
            protocol="UDP",
            packets=5,
            bytes_=400,
        ),
    ]

    svg = render_flows_svg(flows)

    assert "192.168.1.10" in svg
    assert "192.168.1.20" in svg
    assert "10.0.0.1" in svg
    assert "8.8.8.8" in svg
    assert "TCP" in svg
    assert "UDP" in svg


def test_render_empty_flows():
    svg = render_flows_svg([])

    assert svg.startswith("<svg")
    assert svg.endswith("</svg>")
    assert "No network flows" in svg


def test_svg_escapes_endpoint_text():
    flow = create_flow(
        source="<source>",
        destination="destination&server",
    )

    svg = render_flows_svg([flow])

    assert "&lt;source&gt;" in svg
    assert "destination&amp;server" in svg


def test_unique_endpoints_are_rendered_as_nodes():
    flows = [
        create_flow(),
        create_flow(
            source="192.168.1.10",
            destination="8.8.8.8",
            protocol="UDP",
        ),
    ]

    svg = render_flows_svg(flows)

    assert svg.count('data-node="192.168.1.10"') == 1
    assert svg.count('data-node="192.168.1.20"') == 1
    assert svg.count('data-node="8.8.8.8"') == 1


def test_each_flow_is_rendered_as_connection():
    flows = [
        create_flow(),
        create_flow(
            source="10.0.0.1",
            destination="8.8.8.8",
            protocol="UDP",
        ),
    ]

    svg = render_flows_svg(flows)

    assert 'data-flow-index="0"' in svg
    assert 'data-flow-index="1"' in svg


def test_flow_metadata_is_rendered():
    flow = create_flow(
        protocol="ICMP",
        packets=12,
        bytes_=1024,
    )

    svg = render_flows_svg([flow])

    assert "ICMP" in svg
    assert "12 packets" in svg
    assert "1024 bytes" in svg


def test_invalid_width():
    with pytest.raises(ValueError):
        render_flows_svg([], width=0)


def test_invalid_row_height():
    with pytest.raises(ValueError):
        render_flows_svg([], row_height=0)