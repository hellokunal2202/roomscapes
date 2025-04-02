import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import streamlit as st
import numpy as np
from PIL import Image

from modules import components, models, utils
from modules.utils import get_dominant_colors
from modules.config import PATHS
# --- ADD THIS IMPORT ---
from modules.color_util import categorize_color_family # Import the conversion function

# Initialize session state
def init_session():
    session_defaults = {
        "sidebar_expanded": "collapsed",
        "budget": 5000,
        "detected_objects": set(),
        "recommended_objects": set(),
        "selected_items": [],
        "landing_done": False,
        "uploaded_file_path": None,
        "last_uploaded_file": None,
        "detected_results": None,
        "result_image": None,
        "detected_image": None,
        "dominant_colors": [], # Initialize as an empty list
    }

    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Sidebar controls
def render_sidebar_controls():
    if st.session_state.uploaded_file_path:
        st.markdown("""
        <div class="card">
            <h3 style="text-align:center;">Design Controls</h3>
        </div>
        """, unsafe_allow_html=True)

        st.session_state.budget = st.number_input(
            "💰 Budget (INR)",
            min_value=5000,
            step=500,
            value=st.session_state.budget,
        )

        # Define mapping between UI names and internal names
        item_mapping = {
            "Sofa": "sofa",
            "Curtains": "curtains",
            "Wooden Floor": "wooden-floor",
            "Nightstand": "floor-lamps", # Note: Mapped Nightstand to floor-lamps? Verify if correct.
            "Painting": "painting",
            "Cabinet": "cabinet",
            "Frame": "frame",
            "Table": "center-table",
            "Chair": "chair-wooden",
        }

        # Ensure detected and recommended objects are sets
        all_items = st.session_state.detected_objects.union(st.session_state.recommended_objects)

        # Filter selected_items to only include valid options
        valid_selected_items = [item for item in st.session_state.selected_items if item in all_items]

        # Update session state to prevent invalid defaults - Use UI names for multiselect
        # Map internal names back to UI names for default selection display
        reverse_item_mapping = {v: k for k, v in item_mapping.items()}
        display_selected_items = [reverse_item_mapping.get(item, item) for item in valid_selected_items if reverse_item_mapping.get(item, item) in all_items]


        selected_items_display = st.multiselect(
            "🛠️ Redesign Elements",
            options=sorted(all_items), # Show UI names if available, else internal names
            default=display_selected_items, # Default with UI names
            key="items_display" # Use a different key for the display widget
        )

        if st.button("🌟 Generate Shopping List"):
            if selected_items_display:
                # Map selected UI names back to internal names for storing
                st.session_state.selected_items = [item_mapping.get(item, item) for item in selected_items_display]

                # --- MODIFIED SECTION for DOMINANT COLORS ---
                if st.session_state.uploaded_file_path:
                    hex_colors = get_dominant_colors(
                        st.session_state.uploaded_file_path
                    )
                    color_families = list(set(categorize_color_family(hex_code) for hex_code in hex_colors if hex_code))
                    st.session_state.dominant_colors = color_families


                st.switch_page("pages/user_preference.py")
            else:
                st.error("✨ Select elements to transform!")

# Landing page
def render_landing():
    # Centering the button with columns
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("🚀 Let's Go", use_container_width=True):
            st.session_state.landing_done = True
            st.session_state.sidebar_expanded = "expanded"
            st.rerun()

# File upload handling
def handle_file_upload():
    # Center the file uploader using columns
    col1, col2, col3 = st.columns([1, 2, 1]) # Adjust ratio as needed
    with col2:
        uploaded_file = st.file_uploader(
            "Upload Room Image",
            type=['png', 'jpg', 'jpeg'],
            key="file_uploader",
            label_visibility="collapsed"
        )
    if uploaded_file:
        # Process only if it's a new file or no file was previously processed
        if uploaded_file != st.session_state.last_uploaded_file:
             process_new_upload(uploaded_file)
        # elif st.session_state.uploaded_file_path is None: # Handle case where upload happens before landing page interaction maybe?
        #      process_new_upload(uploaded_file)


def process_new_upload(uploaded_file):
    # Check if the uploaded file is different from the last processed one
    # This prevents reprocessing on every rerun if the same file widget value persists
    # if uploaded_file and (st.session_state.last_uploaded_file is None or uploaded_file.id != st.session_state.last_uploaded_file.id):
    with st.spinner("🌌 Powering Up the Design Matrix..."):
        try:
            file_path = utils.save_uploaded_file(uploaded_file)
            st.session_state.uploaded_file_path = file_path
            st.session_state.last_uploaded_file = uploaded_file # Store the file object itself to compare later
            reset_detection_state() # Reset states for the new image
            st.rerun() # Rerun to update the UI immediately after upload and reset
        except Exception as e:
            st.error(f"Error processing upload: {str(e)}")
            st.session_state.uploaded_file_path = None # Reset path on error
            st.session_state.last_uploaded_file = None


def reset_detection_state():
    # Reset states relevant to a specific uploaded image
    st.session_state.detected_objects = set()
    st.session_state.recommended_objects = set()
    st.session_state.detected_image = None
    st.session_state.selected_items = []
    st.session_state.dominant_colors = []
    st.session_state.detected_results = None
    st.session_state.result_image = None
    # Do NOT reset last_uploaded_file here

# Modify your display_image_columns function
def display_image_columns(yolo_model):
    with st.container():
        st.markdown("""
        <div class="animated-section">
            <div class="card">
                <h3 style="margin-top: 0; color: #e0e0ff;">Your Space Unveiled</h3>
        """, unsafe_allow_html=True)

        col_img1, col_img2 = st.columns(2)
        with col_img1:
            st.image(
                Image.open(st.session_state.uploaded_file_path),
                caption="Original Dimension",
                use_column_width=True,
                output_format="PNG"
            )

            # --- THIS SECTION REMAINS UNCHANGED ---
            # It fetches hex codes directly for display purposes
            if st.session_state.uploaded_file_path:
                try:
                    # Get hex colors specifically for display
                    hex_colors_display = get_dominant_colors(st.session_state.uploaded_file_path)
                    if hex_colors_display:
                         st.markdown("<h6>Dominant Colors</h6>", unsafe_allow_html=True)
                         # Dynamically adjust column count based on number of colors (max 5-6 recommended for UI)
                         num_colors = len(hex_colors_display)
                         cols = st.columns(min(num_colors, 6)) # Limit columns for better UI
                         for i, color in enumerate(hex_colors_display):
                             if i < len(cols): # Ensure we don't exceed number of columns
                                 with cols[i]:
                                    st.markdown(
                                            f'<div style="background-color:{color}; height:50px; border-radius:10px;"></div>',
                                            unsafe_allow_html=True) 
                                    st.caption(color)
                    else:
                        st.caption("Could not extract dominant colors.")
                except Exception as e:
                     st.error(f"Error extracting colors: {e}")
            # --- END OF UNCHANGED SECTION ---

        # Run detection only if results aren't already stored for the current image
        if st.session_state.detected_results is None:
             process_object_detection(yolo_model)

        with col_img2:
             # Ensure result image exists before trying to display
            if st.session_state.result_image:
                st.image(
                    st.session_state.result_image,
                    caption="AI Vision",
                    use_column_width=True,
                    output_format="PNG"
                )
            else:
                 # Maybe show a placeholder or a message if detection hasn't run or failed
                 st.caption("Object detection pending or failed.")


        st.markdown("</div></div>", unsafe_allow_html=True)


def process_object_detection(yolo_model):
    with st.spinner("🔮 Decrypting Your Room's Essence..."):
        try:
            results = utils.detect_objects(
                st.session_state.uploaded_file_path,
                yolo_model
            )
            st.session_state.detected_results = results # Store raw results
            img_with_boxes = results.plot() # Generate image with boxes
            # Convert numpy array (BGR) from OpenCV to RGB for PIL/Streamlit
            img_rgb = img_with_boxes[..., ::-1]
            st.session_state.result_image = Image.fromarray(img_rgb) # Store PIL image

            detected_objects = set()
            object_display_mapping = { # Map internal class names to user-friendly names for display
                "sofa": "Sofa",
                "curtains": "Curtains",
                "wooden-floor": "Wooden Floor",
                "floor-lamps": "Nightstand", # Adjust if mapping is different
                "painting": "Painting",
                "cabinet": "Cabinet",
                "frame": "Frame",
                "center-table": "Table",
                "chair-wooden": "Chair",
                 # Add other mappings as needed
            }

            if results.boxes:
                for box in results.boxes:
                    internal_cls_name = results.names[int(box.cls.numpy()[0])]
                    # Use the display name if available, otherwise use internal name
                    display_name = object_display_mapping.get(internal_cls_name, internal_cls_name)
                    detected_objects.add(display_name)

            st.session_state.detected_objects = detected_objects if detected_objects else set() # Store display names

        except Exception as e:
             st.error(f"Object detection failed: {e}")
             st.session_state.detected_results = None # Ensure reset on failure
             st.session_state.result_image = None

# Recommendations
def handle_recommendations(resnet_model, feature_list, filenames):
    # Center the button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
         # Disable button if no file is uploaded
        button_disabled = st.session_state.uploaded_file_path is None
        if st.button("✨ Summon Inspirations", key="find_similar", use_container_width=True, disabled=button_disabled):
            with st.spinner("🌠 Warping Through Design Space..."):
                try:
                    features = utils.feature_extraction(
                        st.session_state.uploaded_file_path,
                        resnet_model
                    )
                    if features is not None:
                        indices = utils.recommend(features, feature_list)
                        # Get base filenames for session state
                        recommended_filenames = [os.path.basename(filenames[i]) for i in indices][:5] # Get top 5 filenames
                        st.session_state.detected_image = recommended_filenames # Store just the filenames

                        # Get recommended objects (assuming this logic exists and works)
                        # Make sure get_recommended_objects expects filenames or full paths
                        # If it expects full paths, construct them:
                        # recommended_fullpaths = [filenames[i] for i in indices][:5]
                        # st.session_state.recommended_objects = utils.get_recommended_objects(recommended_fullpaths)

                        # For now, assuming it works with filenames or you adjust get_recommended_objects
                        st.session_state.recommended_objects = utils.get_recommended_objects(recommended_filenames)

                        # Don't reset selected_items here, let user decide in sidebar
                        # st.session_state.selected_items = []
                        st.rerun() # Rerun to display recommendations
                    else:
                         st.warning("Could not extract features from the image.")
                except Exception as e:
                    st.error(f"Failed to get recommendations: {str(e)}")

    # Display recommendations if they exist in session state
    if st.session_state.detected_image:
        display_recommendations(filenames) # Pass the full list of filenames for lookup


def display_recommendations(filenames):
    with st.container():
        st.markdown("""
        <div class="animated-section">
            <div class="card">
                <h3 style="color: #e0e0ff;">✨ Cosmic Inspirations</h3>
        """, unsafe_allow_html=True)

        # Ensure detected_image has content
        if st.session_state.detected_image:
             cols = st.columns(len(st.session_state.detected_image)) # Create columns based on number of images
             for i, img_name in enumerate(st.session_state.detected_image):
                with cols[i]:
                    try:
                        # Find the full path corresponding to the base filename
                        matching_files = [f for f in filenames if os.path.basename(f) == img_name]
                        if matching_files:
                             img_path = matching_files[0]
                             st.image(
                                img_path,
                                use_column_width=True,
                                caption=f"Vision {i+1}",
                                output_format="PNG"
                             )
                        else:
                             st.error(f"Image {img_name} not found.")
                    except Exception as e:
                        st.error(f"Error loading image {img_name}: {str(e)}")
        else:
             st.info("No recommendations generated yet.")


        st.markdown("</div></div>", unsafe_allow_html=True)


# Main flow
def process_main_flow(yolo_model, resnet_model, feature_list, filenames):
    # Central column for the main content area after landing
    # col1, col2, col3 = st.columns([1, 8, 1]) # Example: Wider central column
    # with col2:
    handle_file_upload()

    if st.session_state.uploaded_file_path:
        display_image_columns(yolo_model)
        handle_recommendations(resnet_model, feature_list, filenames)
    # else:
    #      # Optional: Show a message prompting upload if landing is done but no file uploaded yet
    #      st.info("Upload an image to begin the design process!")


# Main function
def main():
    # Initialize session state first
    init_session()

    # Then set page config
    st.set_page_config(
        page_title="RoomScapes AI",
        layout="wide",
        page_icon="✨",
        initial_sidebar_state=st.session_state.sidebar_expanded
    )

    components.inject_css() # Assuming this injects necessary CSS
    components.render_header() # Assuming this renders a standard header

    # Load models (consider caching these)
    # @st.cache_resource # Use Streamlit's caching for models
    def load_models_and_features():
        yolo_model = models.load_yolo()
        resnet_model = models.load_resnet()
        feature_list, filenames = models.load_features()
        return yolo_model, resnet_model, feature_list, filenames

    yolo_model, resnet_model, feature_list, filenames = load_models_and_features()


    # Sidebar controls
    with st.sidebar:
        render_sidebar_controls()

    # Main content based on landing page state
    if not st.session_state.landing_done:
        render_landing()
    else:
        process_main_flow(yolo_model, resnet_model, feature_list, filenames)


if __name__ == "__main__":
    main()