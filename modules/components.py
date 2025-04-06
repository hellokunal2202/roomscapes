# Description: This file contains the components for the Streamlit app.
import streamlit as st

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Poppins:wght@300;400;600&display=swap');
    * { font-family: 'Poppins', sans-serif; }
    .stApp {
        background-color:#ffffff;
        color: #1e1a4d;
        overflow-x: hidden;
    }
    .header-text {
        font-family: 'Orbitron', sans-serif;
        font-size: 4rem !important;
        color: #000000;
        text-align: center;
        margin: 30px 0;
        font-weight: 700;
        /* Removed gradient and text shadow effects */
    }
   .card {
    # background: #FFFFFF; /* Solid white background to match page */
    border-radius: 8px; /* Less rounded corners for more professional look */
    color: #000000;
    padding: 20px;
    margin: 20px 0;
    border: 1px solid #E0E0E0; /* Light gray border */
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08); /* Subtle shadow */
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

    .card:hover {
        transform: translateY(-3px); /* Subtle lift effect */
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1); /* Slightly stronger shadow on hover */
    }
    .stButton {
        display: flex;
        justify-content: center;
        margin: 20px 0;
         font-family: 'Orbitron', sans-serif;
    }

    .stButton>button {
        background-color: #1969f0; /* Blue background */
        color: #ffff; /* Black text */
        border: none;
        border-radius: 50px;
        padding: 15px 35px;
        font-family: 'Orbitron', sans-serif;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.4s ease;
        box-shadow: 0 5px 15px rgba(30, 136, 229, 0.4);
    }
    .heading-orbitron {
        margin-top: 0;
        margin-bottom: 10px;
        font-size: 1.75rem;
        font-weight: 600;
        font-family: 'Orbitron', sans-serif;
        color: #000000;
    }

    .stButton>button:hover {
        transform: scale(1.05) translateY(-3px);
        box-shadow: 0 8px 20px rgba(30, 136, 229, 0.6);
        color:#fffff;
        background-color: #1976D2; /* Slightly darker blue on hover */
    }
    .uploadedImage, [data-testid="stImage"] img {
        border-radius: 20px;
        border: 2px solid rgba(80,60,255,0.5);
        transition: transform 0.4s ease, box-shadow 0.4s ease;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animated-section {
        animation: fadeInUp 0.8s ease-out;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .color-swatch {
        border-radius: 10px;
        height: 50px;
        margin: 5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .color-swatch:hover {
        transform: scale(1.05);
    }
    .color-palette {
        display: flex;
        justify-content: space-between;
        margin: 15px 0;
    }

    </style>
    """, unsafe_allow_html=True)

def render_header():
    st.markdown("""
    <div class="animated-section">
        <h1 class="header-text"> RoomScapes AI</h1>
        <p class="subtitle">Redesign Your World with Futuristic Flair</p>
    </div>
    """, unsafe_allow_html=True)