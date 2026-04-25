from dash import html, dcc
import os

def _output_path():
    """Returns the actual output path depending on environment."""
    return os.environ.get("OUTPUT_DIR", os.path.join(os.path.expanduser("~"), "Downloads", "STEM_MOS2"))

def generation_settings():
    output_path = _output_path()
    return html.Div(
        [
            # Input Values Display Box - appears first
            values_display(),
            
            # Generation Settings Panel - appears below
            html.Div(
                [
                    html.Div(
                        [
                            html.I(className="fas fa-sliders-h", style={"marginRight": "10px"}),
                            html.Span("Generation Settings")
                        ],
                        className="right-panel-title"
                    ),
                    html.P("Configure batch size and start generation", className="right-panel-subtitle"),

                    # ── Instruction box ──────────────────────────────────────
                    html.Div(
                        [
                            html.P(
                                [
                                    html.Span("1. ", style={"color": "#6ea8fe", "fontWeight": "bold"}),
                                    "Your outputs will be saved to:",
                                    html.Br(),
                                    html.Span(
                                        output_path + ("/batch_<n>/" if os.sep == "/" else "\\batch_<n>\\"),
                                        style={"color": "#e9ecef", "fontFamily": "monospace", "fontSize": "11px", "wordBreak": "break-all"}
                                    ),
                                ],
                                style={"margin": "0 0 8px 0", "fontSize": "12px", "color": "#adb5bd"}
                            ),
                            html.P(
                                [
                                    html.Span("2. ", style={"color": "#6ea8fe", "fontWeight": "bold"}),
                                    html.Span(
                                        "Training Ready files may take a few seconds to appear — the simulation runs in the background after the XYZ files are created.",
                                        style={"color": "#adb5bd"}
                                    ),
                                ],
                                style={"margin": "0", "fontSize": "12px"}
                            ),
                        ],
                        style={
                            "marginBottom": "14px",
                            "padding": "10px 12px",
                            "backgroundColor": "#1e2a38",
                            "border": "1px solid #2d4a6b",
                            "borderRadius": "6px",
                            "lineHeight": "1.7"
                        }
                    ),
                    # ─────────────────────────────────────────────────────────

                    html.Label("Batch Size", className="batch-label"),
                    dcc.Dropdown(
                        id="batch-size-dropdown",
                        options=[
                            {"label": "1 image", "value": 1},
                            {"label": "5 images", "value": 5},
                            {"label": "10 images", "value": 10},
                            {"label": "20 images", "value": 20},
                            {"label": "50 images", "value": 50},
                            {"label": "100 images", "value": 100},
                            {"label": "200 images", "value": 200},
                            {"label": "300 images", "value": 300},
                            {"label": "500 images", "value": 500},
                            {"label": "700 images", "value": 700},
                            {"label": "1000 images", "value": 1000},
                        ],
                        value=1,
                        clearable=False,
                        className="batch-dropdown"
                    ),
                    # Button for Loading Defaults and Generating
                    html.Button(
                        [
                            html.I(className="fas fa-redo", style={"marginRight": "10px"}),
                            "Load Default Values"
                        ],
                        id="load-defaults-btn",
                        className="generate-btn",
                        style={"marginBottom": "15px", "backgroundColor": "#6c757d"}
                    ),
                    # Button to Start Generation
                    html.Button(
                        [
                            html.I(className="fas fa-play", style={"marginRight": "10px"}),
                            "Input the Parameters"
                        ],
                        id="generate-btn",
                        className="generate-btn"
                    ),
                ],
                className="right-panel generation-panel"
            )
        ],
        className="right-panel-container"
    )

def values_display():
    return html.Div(
        [
            html.Div(
                [
                    html.I(className="fas fa-clipboard-list", style={"marginRight": "10px"}),
                    html.Span("Input Values")
                ],
                className="right-panel-title"
            ),
            html.Div(id="values-display-content", className="values-display-box")
        ],
        className="right-panel values-panel"
    )
