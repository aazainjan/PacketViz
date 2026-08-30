from html import escape

from backend.analysis.flows import NetworkFlow


def render_flows_svg(
    flows: list[NetworkFlow],
    width: int = 800,
    row_height: int = 100,
) -> str:
    """
    Render network flows as a simple SVG visualization.

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

    for index, flow in enumerate(flows):
        y = (index * row_height) + (row_height / 2)

        source = escape(flow.source)
        destination = escape(flow.destination)
        protocol = escape(flow.protocol)

        source_label = source
        destination_label = destination

        svg.extend(
            [
                (
                    f'<line x1="180" y1="{y}" '
                    f'x2="{width - 180}" y2="{y}" '
                    'stroke="currentColor" stroke-width="2" '
                    'marker-end="url(#arrow)" />'
                ),
                (
                    f'<text x="20" y="{y + 5}" '
                    f'font-family="monospace" font-size="14">'
                    f"{source_label}</text>"
                ),
                (
                    f'<text x="{width - 20}" y="{y + 5}" '
                    f'text-anchor="end" '
                    f'font-family="monospace" font-size="14">'
                    f"{destination_label}</text>"
                ),
                (
                    f'<text x="{width / 2}" y="{y - 10}" '
                    f'text-anchor="middle" '
                    f'font-family="sans-serif" font-size="12">'
                    f"{protocol} · {flow.packets} packets · "
                    f"{flow.bytes} bytes</text>"
                ),
            ]
        )

    svg.append("</svg>")

    return "\n".join(svg)