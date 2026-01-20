from dash import Input, Output, State, html
import base64
import io
from PIL import Image
import numpy as np

########################################################################################################################
#                               Callbakcs For Imafe Upload and Display
#########################################################################################################################

def register_image_upload_callbacks(app):
    """
    Register all callbacks for image upload and display functionality
    """
    @app.callback(
        Output("image-display-column-1", "children"),
        Input("upload-column-1", "contents"),
        State("upload-column-1", "filename"),
        prevent_initial_call=True
    )
    def update_column_1(contents_list, filenames):
        """Handle image uploads for Column 1"""
        return process_uploaded_images(contents_list, filenames)
    
    
    @app.callback(
        Output("image-display-column-2", "children"),
        Input("upload-column-2", "contents"),
        State("upload-column-2", "filename"),
        prevent_initial_call=True
    )
    def update_column_2(contents_list, filenames):
        """Handle image uploads for Column 2"""
        return process_uploaded_images(contents_list, filenames)
    
    
    @app.callback(
        Output("image-display-column-3", "children"),
        Input("upload-column-3", "contents"),
        State("upload-column-3", "filename"),
        prevent_initial_call=True
    )
    def update_column_3(contents_list, filenames):
        """Handle image uploads for Column 3"""
        return process_uploaded_images(contents_list, filenames)

########################################################################################################################
#                             From TIF to PNG Conversion and Display Processing
#########################################################################################################################


def process_uploaded_images(contents_list, filenames):
    """
    Converts TIF to PNG format for browser display
    """
    if contents_list is None:
        return html.P("No images uploaded", className="image-empty-state")
    
    images = []
    for content, filename in zip(contents_list, filenames):
        try:
            # Parse the base64 encoded image
            content_type, content_string = content.split(',')
            decoded = base64.b64decode(content_string)
            
            # Open with PIL and convert TIF to PNG for display
            img = Image.open(io.BytesIO(decoded))
            
            # Convert to RGB if needed (some TIF formats might be grayscale or have alpha)
            if img.mode != 'RGB':
                # For grayscale images, convert to RGB
                if img.mode == 'L' or img.mode == 'I' or img.mode == 'F':
                    # Normalize to 0-255 range if needed
                    img_array = np.array(img)
                    if img_array.max() > 255:
                        img_array = ((img_array - img_array.min()) / (img_array.max() - img_array.min()) * 255).astype(np.uint8)
                    else:
                        img_array = img_array.astype(np.uint8)
                    img = Image.fromarray(img_array)
                
                img = img.convert('RGB')
            
            # Convert to PNG for browser display
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Create display element
            images.append(
                html.Div([
                    html.P(filename, className="image-filename"),
                    html.Img(
                        src=f"data:image/png;base64,{img_str}",
                        className="image-preview"
                    )
                ], className="image-item-container")
            )
        except Exception as e:
            # If conversion fails, show error for this image
            images.append(
                html.Div([
                    html.P(f"⚠️ Error loading {filename}", className="image-error-message")
                ])
            )
    
    return images
