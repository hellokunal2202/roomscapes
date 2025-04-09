import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import streamlit as st
import numpy as np
from PIL import Image
from streamlit.components.v1 import html

from modules import components, models, utils
from modules.utils import get_dominant_colors
from modules.config import PATHS
from modules.color_util import categorize_color_family

excluded_categories = {"Ceramic floor", "Wooden floor"}

# Custom CSS with animations and modern styling
def inject_custom_css():
    st.markdown("""
    <style>
        /* Modern gradient background */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            background-attachment: fixed;
        }
        
        /* Card styling with animation */
        .card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            transition: all 0.3s ease;
            border: none;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
        }
        
        /* Button styling */
        .stButton>button {
            border-radius: 12px;
            padding: 0.5rem 1rem;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            transition: all 0.3s ease;
            font-weight: 500;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(102, 126, 234, 0.4);
        }
        
        /* Input styling */
        .stNumberInput input, .stTextInput input, .stSelectbox select {
            border-radius: 10px !important;
            border: 1px solid #e0e0e0 !important;
            padding: 0.5rem 1rem !important;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background: white;
            box-shadow: 5px 0 15px rgba(0, 0, 0, 0.05);
            border-right: none;
        }
        
        /* Color swatches */
        .color-swatch {
            height: 50px;
            border-radius: 10px;
            margin: 0.2rem;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        
        .color-swatch:hover {
            transform: scale(1.05);
        }
        
        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .fade-in {
            animation: fadeIn 0.8s ease-out forwards;
        }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .stImage {
                width: 100% !important;
            }
            .card {
                padding: 1rem;
            }
        }
        
        /* Section headings */
        .section-heading {
            font-size: 1.5rem;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 1rem;
            position: relative;
            display: inline-block;
        }
        
        .section-heading:after {
            content: '';
            position: absolute;
            bottom: -5px;
            left: 0;
            width: 50px;
            height: 3px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 3px;
        }
        
        /* Button animation */
        .stButton>button {
            position: relative;
            overflow: hidden;
        }
        
        @keyframes ripple {
            0% {
                transform: scale(0);
                opacity: 0.5;
            }
            100% {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        .ripple-effect {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.7);
            transform: scale(0);
            animation: ripple 600ms linear;
            pointer-events: none;
        }
    </style>
    """, unsafe_allow_html=True)

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
        "dominant_colors": [],
    }

    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Enhanced button with ripple effect
def enhanced_button(label, key=None, disabled=False, use_container_width=False):
    clicked = st.button(
        label, 
        key=key, 
        disabled=disabled,
        use_container_width=use_container_width
    )
    
    if clicked:
        # Add ripple effect animation
        html(f"""
        <script>
            function createRipple(event) {{
                const button = event.currentTarget;
                const circle = document.createElement("span");
                const diameter = Math.max(button.clientWidth, button.clientHeight);
                const radius = diameter / 2;
                
                circle.style.width = circle.style.height = `${{diameter}}px`;
                circle.style.left = `${{event.clientX - button.getBoundingClientRect().left - radius}}px`;
                circle.style.top = `${{event.clientY - button.getBoundingClientRect().top - radius}}px`;
                circle.classList.add("ripple-effect");
                
                const ripple = button.getElementsByClassName("ripple-effect")[0];
                if (ripple) {{
                    ripple.remove();
                }}
                
                button.appendChild(circle);
            }}
            
            const buttons = window.parent.document.querySelectorAll('button');
            buttons.forEach(button => {{
                if (button.innerText.includes("{label}")) {{
                    button.addEventListener("click", createRipple);
                }}
            }});
        </script>
        """)
    return clicked

# Enhanced sidebar controls
def render_sidebar_controls():
    if st.session_state.uploaded_file_path:
        st.markdown("""
        <div class="card">
            <h3 style="text-align:center;">Design Controls</h3>
        </div>
        """, unsafe_allow_html=True)

        st.session_state.budget = st.number_input(
            " Budget (INR)",
            min_value=5000,
            step=500,
            value=st.session_state.budget,
        )

        # Display detected objects section
        if st.session_state.detected_objects:
            st.markdown("##### Identified Categories")
            st.markdown("<p style='color:#4CAF50;font-size:0.9em;'>Categories detected in your image</p>", unsafe_allow_html=True)
            detected_items_display = st.multiselect(
                "Select detected items",
                options=sorted(st.session_state.detected_objects - excluded_categories),
                default=[item for item in st.session_state.selected_items if item in st.session_state.detected_objects],
                key="detected_items_display",
                label_visibility="collapsed"
            )
        else:
            detected_items_display = []
            
        # Display recommended objects section
        if st.session_state.recommended_objects:
            st.markdown("##### Suggested Categories")
            st.markdown("<p style='color:#2196F3;font-size:0.9em;'>Categories suggested from similar rooms</p>", unsafe_allow_html=True)
            recommended_items_display = st.multiselect(
                "Select recommended items",
                options=sorted(st.session_state.recommended_objects - excluded_categories),
                default=[item for item in st.session_state.selected_items if item in st.session_state.recommended_objects],
                key="recommended_items_display",
                label_visibility="collapsed"
            )
        else:
            recommended_items_display = []
                
        # Item mapping dictionary
        item_mapping = {
            "Sofa": "sofa",
            "Curtains": "curtains",
            "Wooden Floor": "wooden-floor",
            "Nightstand": "floor-lamps",
            "Lamp": "floor-lamps",
            "Painting": "painting",
            "Cabinet": "cabinet",
            "Frame": "frame",
            "Table": "center-table",
            "Chair": "chair-wooden",
            "Carpet":"handmade-carpets"
        }
        
        # Combine selections from both sections
        selected_items_display = detected_items_display + [item for item in recommended_items_display if item not in detected_items_display]

        if st.button(" Generate Shopping List"):
            if selected_items_display:
                # Map selected UI names back to internal names for storing
                st.session_state.selected_items = [item_mapping.get(item, item) for item in selected_items_display]

                if st.session_state.uploaded_file_path:
                    hex_colors = get_dominant_colors(
                        st.session_state.uploaded_file_path
                    )
                    color_families = list(set(categorize_color_family(hex_code) for hex_code in hex_colors if hex_code))
                    st.session_state.dominant_colors = color_families

                st.switch_page("pages/2_Preferences.py")
            else:
                st.error(" Select elements to transform!")
                
def render_landing():
    st.markdown("""
    <div style="text-align: center; margin-top: 5rem;">
        <h1 class="fade-in" style="color: #2d3748; margin-bottom: 2rem;">Welcome to RoomScapes AI</h1>
        <p class="fade-in" style="color: #4a5568; margin-bottom: 3rem; font-size: 1.1rem;">
            Transform your space with AI-powered design recommendations
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if enhanced_button("Start Room Analysis", 
                         key="start_analysis", 
                         use_container_width=True):
            st.session_state.landing_done = True
            st.session_state.sidebar_expanded = "expanded"
            st.rerun()

# Enhanced file upload handling
def handle_file_upload():
    st.markdown("""
    <div style="margin: 2rem 0; text-align: center;">
        <h3 class="section-heading">Upload Your Room Image</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create centered layout with proper spacing
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        uploaded_file = st.file_uploader(
            "Upload your room image (PNG, JPG, JPEG)",
            type=['png', 'jpg', 'jpeg'],
            key="file_uploader",
            label_visibility="visible"
        )
    
    # Add bottom spacing
    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
    
    if uploaded_file:
        if uploaded_file != st.session_state.last_uploaded_file:
            process_new_upload(uploaded_file)

def process_new_upload(uploaded_file):
    with st.spinner("🌌 Powering Up the Design Matrix..."):
        try:
            file_path = utils.save_uploaded_file(uploaded_file)
            st.session_state.uploaded_file_path = file_path
            st.session_state.last_uploaded_file = uploaded_file
            reset_detection_state()
            st.rerun()
        except Exception as e:
            st.error(f"Error processing upload: {str(e)}")
            st.session_state.uploaded_file_path = None
            st.session_state.last_uploaded_file = None

def reset_detection_state():
    st.session_state.detected_objects = set()
    st.session_state.recommended_objects = set()
    st.session_state.detected_image = None
    st.session_state.selected_items = []
    st.session_state.dominant_colors = []
    st.session_state.detected_results = None
    st.session_state.result_image = None

# Enhanced image display columns
def display_image_columns(yolo_model):
    with st.container():
        st.markdown("""
        <div class="card fade-in">
            <h3 class="section-heading">Object Detection Results</h3>
        """, unsafe_allow_html=True)

        col_img1, col_img2 = st.columns(2)
        with col_img1:
            st.image(
                Image.open(st.session_state.uploaded_file_path),
                caption="Original Dimension",
                use_column_width=True,
                output_format="PNG"
            )

            if st.session_state.uploaded_file_path:
                try:
                    hex_colors_display = get_dominant_colors(st.session_state.uploaded_file_path)
                    if hex_colors_display:
                        st.markdown("<h6 style='color: #2d3748;'>Dominant Colors</h6>", unsafe_allow_html=True)
                        num_colors = len(hex_colors_display)
                        cols = st.columns(min(num_colors, 6)) 
                        for i, color in enumerate(hex_colors_display):
                            if i < len(cols):
                                with cols[i]:
                                    st.markdown(
                                        f'<div class="color-swatch" style="background-color:{color};"></div>',
                                        unsafe_allow_html=True) 
                                    st.caption(color)
                    else:
                        st.caption("Could not extract dominant colors.")
                except Exception as e:
                    st.error(f"Error extracting colors: {e}")

        if st.session_state.detected_results is None:
            process_object_detection(yolo_model)

        with col_img2:
            if st.session_state.result_image:
                st.image(
                    st.session_state.result_image,
                    caption="AI Vision",
                    use_column_width=True,
                    output_format="PNG"
                )
            else:
                st.caption("Object detection pending or failed.")

        st.markdown("</div>", unsafe_allow_html=True)

def process_object_detection(yolo_model):
    with st.spinner("🔮 Decrypting Your Room's Essence..."):
        try:
            results = utils.detect_objects(
                st.session_state.uploaded_file_path,
                yolo_model
            )
            st.session_state.detected_results = results 
            img_with_boxes = results.plot() 
            img_rgb = img_with_boxes[..., ::-1]
            st.session_state.result_image = Image.fromarray(img_rgb)

            detected_objects = set()
            object_display_mapping = { 
                "sofa": "Sofa",
                "curtains": "Curtains",
                "wooden-floor": "Wooden Floor",
                "floor-lamps": "Nightstand", 
                "painting": "Painting",
                "cabinet": "Cabinet",
                "frame": "Frame",
                "center-table": "Table",
                "chair-wooden": "Chair"
            }

            if results.boxes:
                for box in results.boxes:
                    internal_cls_name = results.names[int(box.cls.numpy()[0])]
                    display_name = object_display_mapping.get(internal_cls_name, internal_cls_name)
                    detected_objects.add(display_name)

            st.session_state.detected_objects = detected_objects if detected_objects else set()

        except Exception as e:
             st.error(f"Object detection failed: {e}")
             st.session_state.detected_results = None
             st.session_state.result_image = None

# Enhanced recommendations section
def display_recommendations(filenames):
    with st.container():
        st.markdown("""
        <div class="card fade-in">
            <h3 class="section-heading">Our Inspirations</h3>
        """, unsafe_allow_html=True)

        if st.session_state.detected_image:
            cols = st.columns(len(st.session_state.detected_image))
            for i, img_name in enumerate(st.session_state.detected_image):
                with cols[i]:
                    try:
                        matching_files = [f for f in filenames if os.path.basename(f) == img_name]
                        if matching_files:
                            img_path = matching_files[0]
                            st.image(
                                img_path,
                                use_column_width=True,
                                caption=f"Inspiration {i+1}",
                                output_format="PNG"
                            )
                        else:
                            st.error(f"Image {img_name} not found.")
                    except Exception as e:
                        st.error(f"Error loading image {img_name}: {str(e)}")
        else:
            st.info("No recommendations generated yet.")

        st.markdown("</div>", unsafe_allow_html=True)

def handle_recommendations(resnet_model, feature_list, filenames):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        button_disabled = st.session_state.uploaded_file_path is None
        if enhanced_button("View Top Similar Rooms", key="find_similar", use_container_width=True, disabled=button_disabled):
            with st.spinner(" Warping Through Design Space..."):
                try:
                    features = utils.feature_extraction(
                        st.session_state.uploaded_file_path,
                        resnet_model
                    )
                    if features is not None:
                        indices = utils.recommend(features, feature_list)
                        recommended_filenames = [os.path.basename(filenames[i]) for i in indices][:5]
                        st.session_state.detected_image = recommended_filenames 
                        st.session_state.recommended_objects = utils.get_recommended_objects(recommended_filenames)
                        st.rerun() 
                    else:
                         st.warning("Could not extract features from the image.")
                except Exception as e:
                    st.error(f"Failed to get recommendations: {str(e)}")

    if st.session_state.detected_image:
        display_recommendations(filenames) 

def process_main_flow(yolo_model, resnet_model, feature_list, filenames):
    handle_file_upload()
    if st.session_state.uploaded_file_path:
        display_image_columns(yolo_model)

        if not st.session_state.detected_objects:
            st.warning("⚠️ No objects detected. Please upload a picture with detectable furniture or decor.")
        else:
            handle_recommendations(resnet_model, feature_list, filenames)

# Main function with enhanced UI
def main():
    init_session()

    st.set_page_config(
        page_title="RoomScapes AI",
        layout="wide",
        initial_sidebar_state=st.session_state.sidebar_expanded,
        page_icon="✨"
    )

    
    inject_custom_css()
    # Removed components.render_header() to eliminate duplicate heading

    def load_models_and_features():
        yolo_model = models.load_yolo()
        resnet_model = models.load_resnet()
        feature_list, filenames = models.load_features()
        return yolo_model, resnet_model, feature_list, filenames

    yolo_model, resnet_model, feature_list, filenames = load_models_and_features()

    with st.sidebar:
        render_sidebar_controls()

    if not st.session_state.landing_done:
        render_landing()
    else:
        process_main_flow(yolo_model, resnet_model, feature_list, filenames)

if __name__ == "__main__":
    main()