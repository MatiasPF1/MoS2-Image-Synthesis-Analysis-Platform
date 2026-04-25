from dash import html, dcc

def generation_settings():
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
                    html.Div(
                        [
                            html.I(className="fas fa-folder-open", style={"marginRight": "6px", "color": "#adb5bd"}),
                            html.Span("Outputs saved to: ", style={"color": "#adb5bd", "fontSize": "12px"}),
                            html.Span("/output/batch_<n>/", style={"color": "#e9ecef", "fontSize": "12px", "fontFamily": "monospace"}),
                            html.Br(),
                            html.Span("Mount your folder → ", style={"color": "#adb5bd", "fontSize": "11px"}),
                            html.Span("-v \"<your Downloads/STEM_MOS2>:/output\"", style={"color": "#6ea8fe", "fontSize": "11px", "fontFamily": "monospace"}),
                        ],
                        style={"marginTop": "14px", "padding": "10px", "backgroundColor": "#2b2b2b", "borderRadius": "6px", "lineHeight": "1.8"}
                    )
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
