import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import streamlit as st

if "sidebar_expanded" not in st.session_state:
    st.session_state.sidebar_expanded = "collapsed"

# Set page configuration
st.set_page_config(
    page_title="RoomScapes AI",
    layout="wide",
    page_icon="✨",
    initial_sidebar_state=st.session_state.sidebar_expanded
)

from ultralytics import YOLO
import numpy as np
from PIL import Image
import pandas as pd
import ast
import pickle
import tensorflow
from tensorflow.keras.preprocessing import image
from tensorflow.keras.layers import GlobalMaxPooling2D
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from sklearn.neighbors import NearestNeighbors
from numpy.linalg import norm

# Custom CSS styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Poppins:wght@300;400;600&display=swap');
* { font-family: 'Poppins', sans-serif; }
.stApp {
    background: linear-gradient(135deg, #0d0b24 0%, #1e1a4d 50%, #2a2566 100%);
    color: #e0e0ff;
    overflow-x: hidden;
}
.header-text {
    font-family: 'Orbitron', sans-serif;
    font-size: 4rem !important;
    background: linear-gradient(45deg, #ffea00, #ffd700);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin: 30px 0;
    font-weight: 700;
    text-shadow: 0 0 15px rgba(255,234,0,0.8),
                0 0 30px rgba(255,215,0,0.6),
                0 0 50px rgba(255,200,0,0.4);
}
.card {
    background: rgba(30,25,70,0.85);
    border-radius: 25px;
    padding: 30px;
    margin: 20px 0;
    border: 1px solid rgba(80,60,255,0.3);
    box-shadow: 0 15px 40px rgba(0,0,0,0.3), inset 0 0 10px rgba(80,60,255,0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 50px rgba(0,0,0,0.4), inset 0 0 15px rgba(80,60,255,0.2);
}
.stButton {
    display: flex;
    justify-content: center;
}
.stButton>button {
    background: linear-gradient(45deg, #7b00ff, #00ddeb);
    color: #ffffff;
    border: none;
    border-radius: 50px;
    padding: 15px 35px;
    font-family: 'Orbitron', sans-serif;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 0.4s ease;
    box-shadow: 0 5px 25px rgba(123,0,255,0.5);
}
.stButton>button:hover {
    transform: scale(1.05) translateY(-3px);
    box-shadow: 0 10px 35px rgba(123,0,255,0.7), 0 0 20px rgba(0,221,235,0.5);
    background: linear-gradient(45deg, #00ddeb, #7b00ff);
}
.uploadedImage, [data-testid="stImage"] img {
    border-radius: 20px;
    border: 2px solid rgba(80,60,255,0.5);
    transition: transform 0.4s ease, box-shadow 0.4s ease;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}
.uploadedImage:hover, [data-testid="stImage"] img:hover {
    transform: scale(1.03);
    box-shadow: 0 15px 40px rgba(80,60,255,0.4);
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}
.animated-section { animation: fadeInUp 0.8s ease-out; }
.subtitle {
    color: #b0b0ff;
    font-size: 1.3rem;
    text-align: center;
    margin-bottom: 40px;
    text-shadow: 0 0 10px rgba(80,60,255,0.3);
}
.center-button {
    display: flex;
    justify-content: center;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# Model & Data Initialization
@st.cache_resource
def load_models():
    feature_list = np.array(pickle.load(open('embeddings.pkl', 'rb')))
    filenames = pickle.load(open('filenames.pkl', 'rb'))
    resnet_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224,224,3))
    resnet_model.trainable = False
    resnet_model = tensorflow.keras.Sequential([resnet_model, GlobalMaxPooling2D()])
    yolo_model = YOLO('best.pt')
    return feature_list, filenames, resnet_model, yolo_model

feature_list, filenames, resnet_model, yolo_model = load_models()

# Utility Functions
def save_uploaded_file(uploaded_file):
    try:
        os.makedirs('uploads', exist_ok=True)
        file_path = os.path.join('uploads', uploaded_file.name)
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

@st.cache_data
def feature_extraction(img_path):
    try:
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        expanded_img_array = np.expand_dims(img_array, axis=0)
        preprocessed_img = preprocess_input(expanded_img_array)
        result = resnet_model.predict(preprocessed_img, verbose=0).flatten()
        return result / norm(result)
    except Exception as e:
        st.error(f"Error extracting features: {e}")
        return None

def recommend(features, _feature_list):
    neighbors = NearestNeighbors(n_neighbors=5, algorithm='brute', metric='euclidean')
    neighbors.fit(_feature_list)
    distances, indices = neighbors.kneighbors([features])
    return indices[0]

@st.cache_data
def detect_objects(image_path):
    results = yolo_model.predict(image_path, conf=0.3)[0]
    return results

@st.cache_data
def recommended_objects(detected_img):
    try:
        df = pd.read_csv('detected_objects.csv')
        df['detected_objects'] = df['detected_objects'].apply(ast.literal_eval)
        options = df[df['image'].isin(detected_img)]['detected_objects'].values
        return set().union(*options)
    except Exception as e:
        st.error(f"Error processing recommended objects: {e}")
        return set()

# Main App
def main():
    with st.sidebar:
        if st.session_state.get("uploaded_file_path") is None:
            st.write("Hello user!")
        else:
            st.markdown("""
            <div class="card">
                <h3 style="text-align:center;">Design Controls</h3>
            </div>
            """, unsafe_allow_html=True)
            budget = st.number_input(
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
                default=st.session_state.get("selected_items", []),
                key="items"
            )
            if st.button("🌟 Generate Shopping List",
                        help="Unlock inspirations first" if "detected_image" not in st.session_state else None,
                        disabled="detected_image" not in st.session_state):
                if selected_items:
                    st.session_state.selected_items = selected_items
                    st.switch_page("pages/Recommend_products.py")
                else:
                    st.error("✨ Select elements to transform!")

    # Persistent header
    st.markdown("""
    <div class="animated-section">
        <h1 class="header-text">✨ RoomScapes AI</h1>
        <p class="subtitle">Redesign Your World with Futuristic Flair</p>
    </div>
    """, unsafe_allow_html=True)

    if "landing_done" not in st.session_state:
        st.session_state.landing_done = False

    if not st.session_state.landing_done:
        if st.button("🚀 Let's Go"):
            st.session_state.landing_done = True
            st.session_state.sidebar_expanded = "expanded"  # Expand sidebar
            st.rerun()
        return

    # Initialize session state variables
    if "detected_objects" not in st.session_state:
        st.session_state.detected_objects = set()
    if "recommended_objects" not in st.session_state:
        st.session_state.recommended_objects = set()
    if "selected_items" not in st.session_state:
        st.session_state.selected_items = []

    # Main Content
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state.get("uploaded_file_path") is None:
            uploaded_file = st.file_uploader(
                "Upload Room Image",
                type=['png', 'jpg', 'jpeg'],
                key="file_uploader",
                label_visibility="collapsed"
            )
        else:
            uploaded_file = None

    # Process uploaded file
    if uploaded_file is not None:
        if uploaded_file != st.session_state.get("last_uploaded_file"):
            with st.spinner("🌌 Powering Up the Design Matrix..."):
                file_path = save_uploaded_file(uploaded_file)
                if not file_path:
                    return
                st.session_state.uploaded_file_path = file_path
                st.session_state.last_uploaded_file = uploaded_file
                st.session_state.detected_objects = set()
                st.session_state.recommended_objects = set()
                st.session_state.pop("detected_image", None)
                st.session_state.selected_items = []

    # Display uploaded image and process
    if st.session_state.get("uploaded_file_path") is not None:
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
            if "detected_results" not in st.session_state:
                with st.spinner("🔮 Decrypting Your Room’s Essence..."):
                    results = detect_objects(st.session_state.uploaded_file_path)
                    st.session_state.detected_results = results
                    st.session_state.result_image = results.plot()
                    detected_objects = set()
                    if results.boxes:
                        for box in results.boxes:
                            cls = results.names[int(box.cls.numpy()[0])]
                            detected_objects.add(cls)
                    st.session_state.detected_objects = detected_objects or {"No objects detected"}
            with col_img2:
                st.image(
                    st.session_state.result_image,
                    caption="AI Vision",
                    use_column_width=True,
                    output_format="PNG"
                )
            st.markdown("</div></div>", unsafe_allow_html=True)

        # Recommendation engine
        if st.button("✨ Summon Inspirations", key="find_similar"):
            with st.spinner("🌠 Warping Through Design Space..."):
                features = feature_extraction(st.session_state.uploaded_file_path)
                if features is not None:
                    indices = recommend(features, feature_list)
                    detected_img = [os.path.basename(filenames[i]) for i in indices]
                    st.session_state.detected_image = detected_img[:5]
                    st.session_state.recommended_objects = recommended_objects(detected_img)
                    st.session_state.selected_items = []
                    st.rerun()

        # Display recommendations
        if "detected_image" in st.session_state:
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
                            img_path = filenames[np.where([os.path.basename(x) == img_name for x in filenames])[0][0]]
                            st.image(
                                img_path,
                                use_column_width=True,
                                caption=f"Vision {i+1}",
                                output_format="PNG"
                            )
                        except Exception as e:
                            st.error(f"Error loading image {img_name}: {str(e)}")
                st.markdown("</div></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()