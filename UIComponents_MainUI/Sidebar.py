from dash import html
import dash_bootstrap_components as dbc


sidebar = html.Div(
    [
        # Sidebar Header
        html.Div(
            [
                html.I(className=""),
                html.Span("Functionalities", className="sidebar-header-text")
            ],
            className="sidebar-header"
        ),
        
        html.Hr(className="sidebar-divider"),
        
        # Navigation Items
        html.Div(
            [
                html.Div(
                    [
                        html.I(className="fas fa-microscope sidebar-item-icon"),
                        html.Span("Batch Generation", className="sidebar-item-text")
                    ],
                    id="nav-xyz-generation",
                    className="sidebar-item active-sidebar-item"
                ),
                html.Div(
                    [
                        html.I(className="fas fa-image sidebar-item-icon"),
                        html.Span("STEM Visualization", className="sidebar-item-text")
                    ],
                    id="nav-stem-generation",
                    className="sidebar-item"
                ),
                html.Div(
                    [
                        html.I(className="fas fa-gear sidebar-item-icon"),
                        html.Span("ResUnet For Vacancies and Polymorphs", className="sidebar-item-text")
                    ],
                    id="nav-resunet",
                    className="sidebar-item"
                ),
            ],
            className="sidebar-nav"
        ),
    ],
    className="sidebar"
)
