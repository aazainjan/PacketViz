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


def test_flow_contains_interaction_metadata():
    flow = create_flow(
        protocol="TCP",
        packets=7,
        bytes_=512,
    )

    svg = render_flows_svg([flow])

    assert 'class="flow-edge"' in svg
    assert 'data-flow-index="0"' in svg
    assert 'data-source="192.168.1.10"' in svg
    assert 'data-destination="192.168.1.20"' in svg
    assert 'data-protocol="TCP"' in svg
    assert 'data-packets="7"' in svg
    assert 'data-bytes="512"' in svg


def test_nodes_have_interaction_metadata():
    svg = render_flows_svg([create_flow()])

    assert 'class="network-node"' in svg
    assert 'data-node="192.168.1.10"' in svg
    assert 'data-node="192.168.1.20"' in svg


def test_flow_contains_svg_tooltip():
    svg = render_flows_svg([create_flow()])

    assert "<title>" in svg
    assert "192.168.1.10" in svg
    assert "192.168.1.20" in svg
    assert "TCP" in svg
    assert "3 packets" in svg
    assert "260 bytes" in svg


def test_special_characters_are_escaped_in_metadata():
    flow = create_flow(
        source="<source&server>",
        destination='destination"server',
        protocol="TCP&HTTPS",
    )

    svg = render_flows_svg([flow])

    assert "&lt;source&amp;server&gt;" in svg
    assert "destination&quot;server" in svg
    assert "TCP&amp;HTTPS" in svg


def test_svg_contains_hover_styles():
    svg = render_flows_svg([create_flow()])

    assert ".flow-edge:hover" in svg
    assert ".flow-label:hover" in svg
    assert ".network-node:hover" in svg


def test_flow_edges_are_marked_as_interactive():
    svg = render_flows_svg([create_flow()])

    assert 'class="flow-edge"' in svg
    assert "cursor: pointer" in svg


def test_flow_labels_are_interactive():
    svg = render_flows_svg([create_flow()])

    assert 'class="flow-label"' in svg
    assert 'data-flow-label="0"' in svg


def test_network_nodes_are_interactive():
    svg = render_flows_svg([create_flow()])

    assert 'class="network-node"' in svg
    assert 'data-node="192.168.1.10"' in svg
    assert 'data-node="192.168.1.20"' in svg


def test_flow_contains_port_and_time_metadata():
    flow = create_flow()

    svg = render_flows_svg([flow])

    assert 'data-source-port="50000"' in svg
    assert 'data-destination-port="443"' in svg
    assert 'data-start-time="1.0"' in svg
    assert 'data-end-time="1.2"' in svg


def test_flow_edges_have_click_handlers():
    svg = render_flows_svg([create_flow()])

    assert 'onclick="showFlowDetails(0)"' in svg


def test_flow_details_panel_is_rendered():
    svg = render_flows_svg([create_flow()])

    assert 'id="flow-details"' in svg
    assert 'id="details-source"' in svg
    assert 'id="details-destination"' in svg
    assert 'id="details-protocol"' in svg
    assert 'id="details-ports"' in svg
    assert 'id="details-packets"' in svg
    assert 'id="details-bytes"' in svg
    assert 'id="details-time"' in svg


def test_flow_details_javascript_is_rendered():
    svg = render_flows_svg([create_flow()])

    assert "function showFlowDetails(index)" in svg
    assert "function hideFlowDetails()" in svg
    assert 'classList.add("visible")' in svg
    assert 'classList.add("selected")' in svg


def test_nodes_have_flow_statistics():
    flows = [
        create_flow(
            source="192.168.1.10",
            destination="192.168.1.20",
            packets=3,
            bytes_=260,
        ),
        create_flow(
            source="192.168.1.10",
            destination="8.8.8.8",
            protocol="UDP",
            packets=5,
            bytes_=400,
        ),
    ]

    svg = render_flows_svg(flows)

    assert 'data-node="192.168.1.10"' in svg
    assert 'data-flows="2"' in svg
    assert 'data-packets="8"' in svg
    assert 'data-bytes="660"' in svg


def test_node_click_handler_is_rendered():
    svg = render_flows_svg([create_flow()])

    assert "showNodeDetails" in svg
    assert "onclick=" in svg


def test_node_details_panel_is_rendered():
    svg = render_flows_svg([create_flow()])

    assert 'id="node-details"' in svg
    assert 'id="node-details-address"' in svg
    assert 'id="node-details-flows"' in svg
    assert 'id="node-details-packets"' in svg
    assert 'id="node-details-bytes"' in svg
    assert 'id="node-details-connections"' in svg


def test_node_selection_style_is_rendered():
    svg = render_flows_svg([create_flow()])

    assert ".network-node.selected" in svg
    assert 'classList.add("selected")' in svg


def test_node_details_javascript_is_rendered():
    svg = render_flows_svg([create_flow()])

    assert "function showNodeDetails(node)" in svg
    assert "function hideNodeDetails()" in svg
    assert "node-details" in svg


def test_node_peer_information_is_rendered():
    flows = [
        create_flow(
            source="192.168.1.10",
            destination="192.168.1.20",
        ),
        create_flow(
            source="192.168.1.10",
            destination="8.8.8.8",
            protocol="UDP",
        ),
    ]

    svg = render_flows_svg(flows)

    assert "Peers:" in svg
    assert "Connections:" in svg