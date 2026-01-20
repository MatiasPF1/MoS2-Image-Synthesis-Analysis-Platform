from dash import html, dcc


########################################################################################################################
#                               File Input Panel Component - TIF Image Columns
#########################################################################################################################


def file_input_panel():
    """
    Panel with 3 clickable columns for uploading and visualizing TIF images
    """
    return html.Div(
        [
            html.H3("STEM Image Visualization", className="image-viz-title"),
            
            # Three column layout
            html.Div(
                [
                    # Column 1
                    create_image_column("column-1", "Column 1"),
                    
                    # Column 2
                    create_image_column("column-2", "Column 2"),
                    
                    # Column 3
                    create_image_column("column-3", "Column 3"),
                ],
                className="image-columns-grid"
            )
        ],
        id="file-input-panel",
        className="material-panel"
    )


def create_image_column(column_id, column_title):
    """
    Creates a single clickable column for TIF image upload and display
    """
    return html.Div(
        [
            html.H4(column_title, className="image-column-title"),
            
            # Upload area
            dcc.Upload(
                id=f"upload-{column_id}",
                children=html.Div([
                    html.I(className="fas fa-cloud-upload-alt image-upload-icon"),
                    html.P("Click or drag TIF images here", className="image-upload-text")
                ], className="image-upload-content"),
                className="image-upload-area",
                multiple=True,
                accept=".tif,.tiff"
            ),
            
            # Image display area
            html.Div(
                id=f"image-display-{column_id}",
                className="image-display-area"
            )
        ],
        className="image-column"
    )
