import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import streamlit as st
import numpy as np
from PIL import Image

from modules import components, models, utils
from modules.utils import get_dominant_colors
from modules.config import PATHS

# Initialize session state
def init_session():
    session_defaults = {
        "sidebar_expanded": "collapsed",
        "detected_objects": set(),
        "recommended_objects": set(),
        "selected_items": [],
        "landing_done": False,
        "uploaded_file_path": None,
        "last_uploaded_file": None,
        "detected_results": None,
        "result_image": None,
        "detected_image": None
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
        
        st.number_input(
            "💰 Budget (INR)",
            min_value=1000,
            step=500,
            value=1000,
            key="budget"
        )
        
        all_items = st.session_state.detected_objects.union(st.session_state.recommended_objects)
        selected_items = st.multiselect(
            "🛠️ Redesign Elements",
            options=sorted(all_items),
            default=st.session_state.selected_items,
            key="items"
        )
        
        if st.button("🌟 Generate Shopping List"):
            if selected_items:
                st.session_state.selected_items = selected_items
                st.switch_page("pages/Recommend_products.py")
            else:
                st.error("✨ Select elements to transform!")

# Landing page
def render_landing():
    if st.button("🚀 Let's Go"):
        st.session_state.landing_done = True
        st.session_state.sidebar_expanded = "expanded"
        st.rerun()

# File upload handling
def handle_file_upload():
    if st.session_state.uploaded_file_path is None:
        uploaded_file = st.file_uploader(
            "Upload Room Image",
            type=['png', 'jpg', 'jpeg'],
            key="file_uploader",
            label_visibility="collapsed"
        )
        if uploaded_file:
            process_new_upload(uploaded_file)

def process_new_upload(uploaded_file):
    if uploaded_file != st.session_state.last_uploaded_file:
        with st.spinner("🌌 Powering Up the Design Matrix..."):
            try:
                file_path = utils.save_uploaded_file(uploaded_file)
                st.session_state.uploaded_file_path = file_path
                st.session_state.last_uploaded_file = uploaded_file
                reset_detection_state()
            except Exception as e:
                st.error(str(e))

def reset_detection_state():
    st.session_state.detected_objects = set()
    st.session_state.recommended_objects = set()
    st.session_state.detected_image = None
    st.session_state.selected_items = []
    st.session_state.detected_results = None
    st.session_state.result_image = None

# # Image processing
# def display_image_columns(yolo_model):
#     with st.container():
#         st.markdown("""
#         <div class="animated-section">
#             <div class="card">
#                 <h3 style="margin-top: 0; color: #e0e0ff;">Your Space Unveiled</h3>
#         """, unsafe_allow_html=True)
        
#         col_img1, col_img2 = st.columns(2)
#         with col_img1:
#             st.image(
#                 Image.open(st.session_state.uploaded_file_path),
#                 caption="Original Dimension",
#                 use_column_width=True,
#                 output_format="PNG"
#             )
        
#         if st.session_state.detected_results is None:
#             process_object_detection(yolo_model)
        
#         with col_img2:
#             st.image(
#                 st.session_state.result_image,
#                 caption="AI Vision",
#                 use_column_width=True,
#                 output_format="PNG"
#             )
        
#         st.markdown("</div></div>", unsafe_allow_html=True)

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
            
            # Add color palette display
            if st.session_state.uploaded_file_path:
                colors = get_dominant_colors(st.session_state.uploaded_file_path)
                st.markdown("### Dominant Colors")
                cols = st.columns(len(colors))
                for i, color in enumerate(colors):
                    with cols[i]:
                        st.markdown(
                            f'<div style="background-color:{color}; height:50px; border-radius:10px;"></div>',
                            unsafe_allow_html=True
                        )
                        st.caption(color)
        
        if st.session_state.detected_results is None:
            process_object_detection(yolo_model)
        
        with col_img2:
            st.image(
                st.session_state.result_image,
                caption="AI Vision",
                use_column_width=True,
                output_format="PNG"
            )
        
        st.markdown("</div></div>", unsafe_allow_html=True)

def process_object_detection(yolo_model):
    with st.spinner("🔮 Decrypting Your Room's Essence..."):
        results = utils.detect_objects(
            st.session_state.uploaded_file_path,
            yolo_model
        )
        st.session_state.detected_results = results
        st.session_state.result_image = results.plot()
        detected_objects = set()
        
        if results.boxes:
            for box in results.boxes:
                cls = results.names[int(box.cls.numpy()[0])]
                detected_objects.add(cls)
        
        st.session_state.detected_objects = detected_objects or {"No objects detected"}

# Recommendations
def handle_recommendations(resnet_model, feature_list, filenames):
    if st.button("✨ Summon Inspirations", key="find_similar"):
        with st.spinner("🌠 Warping Through Design Space..."):
            try:
                features = utils.feature_extraction(
                    st.session_state.uploaded_file_path,
                    resnet_model
                )
                if features is not None:
                    indices = utils.recommend(features, feature_list)
                    detected_img = [os.path.basename(filenames[i]) for i in indices]
                    st.session_state.detected_image = detected_img[:5]
                    st.session_state.recommended_objects = utils.get_recommended_objects(detected_img)
                    st.session_state.selected_items = []
                    st.rerun()
            except Exception as e:
                st.error(str(e))

    if st.session_state.detected_image:
        display_recommendations(filenames)

def display_recommendations(filenames):
    with st.container():
        st.markdown("""
        <div class="animated-section">
            <div class="card">
                <h3 style="color: #e0e0ff;">✨ Cosmic Inspirations</h3>
        """, unsafe_allow_html=True)
        
        cols = st.columns(5)
        for i, img_name in enumerate(st.session_state.detected_image[:5]):
            with cols[i]:
                try:
                    img_path = filenames[np.where(
                        [os.path.basename(x) == img_name for x in filenames]
                    )[0][0]]
                    st.image(
                        img_path,
                        use_column_width=True,
                        caption=f"Vision {i+1}",
                        output_format="PNG"
                    )
                except Exception as e:
                    st.error(f"Error loading image {img_name}: {str(e)}")
        
        st.markdown("</div></div>", unsafe_allow_html=True)

# Main flow
def process_main_flow(yolo_model, resnet_model, feature_list, filenames):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        handle_file_upload()

    if st.session_state.uploaded_file_path:
        display_image_columns(yolo_model)
        handle_recommendations(resnet_model, feature_list, filenames)

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
    
    components.inject_css()
    components.render_header()

    # Load models
    yolo_model = models.load_yolo()
    resnet_model = models.load_resnet()
    feature_list, filenames = models.load_features()

    # Sidebar controls
    with st.sidebar:
        render_sidebar_controls()

    # Main content
    if not st.session_state.landing_done:
        render_landing()
    else:
        process_main_flow(yolo_model, resnet_model, feature_list, filenames)

if __name__ == "__main__":
    main()

