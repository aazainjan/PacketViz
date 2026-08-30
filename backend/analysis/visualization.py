from html import escape

from backend.analysis.flows import NetworkFlow


def render_flows_svg(
    flows: list[NetworkFlow],
    width: int = 800,
    row_height: int = 100,
) -> str:
    """
    Render network flows as an SVG visualization.

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

    # Draw connections first so nodes appear above them.
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
                    f'x1="{source_x}" y1="{source_y}" '
                    f'x2="{destination_x}" y2="{destination_y}" '
                    'stroke="currentColor" stroke-width="2" '
                    'marker-end="url(#arrow)" '
                    f'data-flow-index="{index}" '
                    f'data-source="{source}" '
                    f'data-destination="{destination}" '
                    f'data-protocol="{protocol}" '
                    f'data-packets="{flow.packets}" '
                    f'data-bytes="{flow.bytes}">'
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
                    f'data-flow-label="{index}">'
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

        svg.extend(
            [
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
                ),
            ]
        )

    svg.append("</svg>")

    return "\n".join(svg)