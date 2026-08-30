from html import escape

from backend.analysis.flows import NetworkFlow


def render_flows_svg(
    flows: list[NetworkFlow],
    width: int = 800,
    row_height: int = 100,
) -> str:
    """
    Render network flows as an interactive SVG visualization.

    Each unique endpoint is displayed as a node, while each flow
    is represented by a directed connection between its endpoints.
    """

    if width <= 0:
        raise ValueError("width must be greater than 0")

    if row_height <= 0:
        raise ValueError("row_height must be greater than 0")

    height = max(row_height, len(flows) * row_height)

    svg = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}">'
        ),
        "<defs>",
        (
            '<marker id="arrow" markerWidth="10" markerHeight="10" '
            'refX="9" refY="3" orient="auto" markerUnits="strokeWidth">'
        ),
        '<path d="M0,0 L0,6 L9,3 z" />',
        "</marker>",
        "<style>",
        """
        .flow-edge {
            transition: stroke-width 0.15s ease, opacity 0.15s ease;
            cursor: pointer;
        }

        .flow-edge:hover {
            stroke-width: 4;
            opacity: 1;
        }

        .flow-edge.selected {
            stroke-width: 5;
        }

        .flow-label {
            cursor: pointer;
            transition: font-weight 0.15s ease, opacity 0.15s ease;
        }

        .flow-label:hover {
            font-weight: bold;
        }

        .network-node {
            cursor: pointer;
        }

        .network-node circle {
            transition: stroke-width 0.15s ease, fill-opacity 0.15s ease;
        }

        .network-node:hover circle {
            stroke-width: 4;
            fill-opacity: 0.2;
        }

        .network-node text {
            pointer-events: none;
        }

        .flow-details {
            display: none;
        }

        .flow-details.visible {
            display: block;
        }

        .details-background {
            fill: white;
            stroke: currentColor;
            stroke-width: 2;
        }

        .details-close {
            cursor: pointer;
        }
        """,
        "</style>",
        "</defs>",
    ]

    if not flows:
        svg.append(
            f'<text x="{width / 2}" y="{height / 2}" '
            'text-anchor="middle">No network flows</text>'
        )
        svg.append("</svg>")
        return "\n".join(svg)

    endpoints: list[str] = []

    for flow in flows:
        if flow.source not in endpoints:
            endpoints.append(flow.source)

        if flow.destination not in endpoints:
            endpoints.append(flow.destination)

    node_positions: dict[str, tuple[float, float]] = {}

    left_x = 120
    right_x = width - 120

    for index, endpoint in enumerate(endpoints):
        y = 60 + (index * row_height)

        if index % 2 == 0:
            node_positions[endpoint] = (left_x, y)
        else:
            node_positions[endpoint] = (right_x, y)

    required_height = max(
        height,
        max(
            (position[1] for position in node_positions.values()),
            default=0,
        )
        + 60,
    )

    if required_height != height:
        height = required_height
        svg[0] = (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}">'
        )

    # Draw flow connections.
    for index, flow in enumerate(flows):
        source_x, source_y = node_positions[flow.source]
        destination_x, destination_y = node_positions[flow.destination]

        label_y = min(source_y, destination_y) - 10

        source = escape(flow.source)
        destination = escape(flow.destination)
        protocol = escape(flow.protocol)

        svg.extend(
            [
                (
                    f'<line class="flow-edge" '
                    f'id="flow-{index}" '
                    f'x1="{source_x}" y1="{source_y}" '
                    f'x2="{destination_x}" y2="{destination_y}" '
                    'stroke="currentColor" stroke-width="2" '
                    'marker-end="url(#arrow)" '
                    f'data-flow-index="{index}" '
                    f'data-source="{source}" '
                    f'data-destination="{destination}" '
                    f'data-protocol="{protocol}" '
                    f'data-packets="{flow.packets}" '
                    f'data-bytes="{flow.bytes}" '
                    f'data-source-port="{flow.source_port}" '
                    f'data-destination-port="{flow.destination_port}" '
                    f'data-start-time="{flow.start_time}" '
                    f'data-end-time="{flow.end_time}" '
                    f'onclick="showFlowDetails({index})">'
                    f'<title>{source} → {destination} '
                    f'({protocol}, {flow.packets} packets, '
                    f'{flow.bytes} bytes)</title>'
                    '</line>'
                ),
                (
                    f'<text class="flow-label" '
                    f'x="{(source_x + destination_x) / 2}" '
                    f'y="{label_y}" text-anchor="middle" '
                    'font-family="sans-serif" font-size="12" '
                    f'data-flow-label="{index}" '
                    f'onclick="showFlowDetails({index})">'
                    f"{protocol} · "
                    f"{flow.packets} packets · "
                    f"{flow.bytes} bytes"
                    "</text>"
                ),
            ]
        )

    # Draw endpoint nodes.
    for endpoint, (x, y) in node_positions.items():
        label = escape(endpoint)

        svg.append(
            (
                f'<g class="network-node" '
                f'data-node="{label}">'
                f'<title>{label}</title>'
                f'<circle cx="{x}" cy="{y}" r="30" '
                'fill="currentColor" fill-opacity="0.1" '
                'stroke="currentColor" stroke-width="2" />'
                f'<text x="{x}" y="{y + 5}" '
                'text-anchor="middle" '
                'font-family="monospace" font-size="12">'
                f"{label}</text>"
                "</g>"
            )
        )

    # Flow details panel.
    panel_x = 20
    panel_y = 20
    panel_width = min(300, width - 40)
    panel_height = 220

    svg.extend(
        [
            (
                f'<g id="flow-details" class="flow-details" '
                f'transform="translate({panel_x},{panel_y})">'
            ),
            (
                f'<rect class="details-background" '
                f'width="{panel_width}" height="{panel_height}" '
                'rx="8" />'
            ),
            (
                '<text x="20" y="30" '
                'font-family="sans-serif" font-size="16" '
                'font-weight="bold">Flow Details</text>'
            ),
            (
                '<text id="details-source" x="20" y="60" '
                'font-family="monospace" font-size="12" />'
            ),
            (
                '<text id="details-destination" x="20" y="82" '
                'font-family="monospace" font-size="12" />'
            ),
            (
                '<text id="details-protocol" x="20" y="104" '
                'font-family="sans-serif" font-size="12" />'
            ),
            (
                '<text id="details-ports" x="20" y="126" '
                'font-family="sans-serif" font-size="12" />'
            ),
            (
                '<text id="details-packets" x="20" y="148" '
                'font-family="sans-serif" font-size="12" />'
            ),
            (
                '<text id="details-bytes" x="20" y="170" '
                'font-family="sans-serif" font-size="12" />'
            ),
            (
                '<text id="details-time" x="20" y="192" '
                'font-family="sans-serif" font-size="12" />'
            ),
            (
                '<text class="details-close" x="270" y="30" '
                'font-family="sans-serif" font-size="16" '
                'onclick="hideFlowDetails()">×</text>'
            ),
            "</g>",
        ]
    )

    # JavaScript for flow inspection.
    svg.extend(
        [
            "<script><![CDATA[",
            """
            function showFlowDetails(index) {
                const edge = document.getElementById("flow-" + index);
                const panel = document.getElementById("flow-details");

                if (!edge || !panel) {
                    return;
                }

                document.querySelectorAll(".flow-edge.selected")
                    .forEach(function (element) {
                        element.classList.remove("selected");
                    });

                edge.classList.add("selected");

                document.getElementById("details-source").textContent =
                    "Source: " + edge.dataset.source;

                document.getElementById("details-destination").textContent =
                    "Destination: " + edge.dataset.destination;

                document.getElementById("details-protocol").textContent =
                    "Protocol: " + edge.dataset.protocol;

                document.getElementById("details-ports").textContent =
                    "Ports: " + edge.dataset.sourcePort +
                    " → " + edge.dataset.destinationPort;

                document.getElementById("details-packets").textContent =
                    "Packets: " + edge.dataset.packets;

                document.getElementById("details-bytes").textContent =
                    "Bytes: " + edge.dataset.bytes;

                document.getElementById("details-time").textContent =
                    "Time: " + edge.dataset.startTime +
                    " → " + edge.dataset.endTime;

                panel.classList.add("visible");
            }

            function hideFlowDetails() {
                const panel = document.getElementById("flow-details");

                if (panel) {
                    panel.classList.remove("visible");
                }

                document.querySelectorAll(".flow-edge.selected")
                    .forEach(function (element) {
                        element.classList.remove("selected");
                    });
            }
            """,
            "]]></script>",
        ]
    )

    svg.append("</svg>")

    return "\n".join(svg)