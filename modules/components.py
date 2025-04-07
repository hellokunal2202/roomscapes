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

import streamlit as st

def render_css_user_pref():
    st.markdown("""
    <style>
    .main { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: #ffffff; }
    .stButton>button:not([kind="secondary"]) {
        border-radius: 8px !important;
        background: #7b00ff !important;
        color: white !important;
        transition: all 0.3s ease !important;
        margin-top: 0.5rem !important;
        padding: 0.75rem 1.5rem !important;
        font-size: 1rem !important;
        font-weight: bold !important;
        border: none !important;
        line-height: 1.5 !important;
        min-height: 48px !important;
    }
    .stButton>button:not([kind="secondary"]):hover {
        background: #9d4edd !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(123, 0, 255, 0.4) !important;
    }
    .stButton>button:not([kind="secondary"]):focus {
        box-shadow: 0 0 0 3px rgba(123, 0, 255, 0.5) !important;
        outline: none !important;
    }
    .glow-card { 
        background: rgba(255, 255, 255, 0.1); 
        border-radius: 15px; 
        padding: 25px; 
        margin: 15px 0; 
        border: 1px solid rgba(255, 255, 255, 0.2); 
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2); 
        backdrop-filter: blur(10px); 
        transition: all 0.3s ease; 
    }
    .glow-card:hover { box-shadow: 0 6px 20px rgba(123, 0, 255, 0.3); }
    .section-title { font-size: 24px; font-weight: 700; color: #e0e0ff; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; }
    .stMultiSelect [data-baseweb="tag"] { background-color: #7b00ff; }
    button[kind="secondary"] {
        background-color: #ff4b4b !important;
        color: white !important;
        border-radius: 5px !important;
        padding: 2px 8px !important;
        margin-left: 10px !important;
        font-size: 12px !important;
        min-height: 24px !important;
        line-height: 1.2 !important;
        border: none !important;
        box-shadow: none !important;
        vertical-align: middle;
    }
    button[kind="secondary"]:hover { background-color: #cc0000 !important; }
    .stInfo { vertical-align: middle; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

def render_title_user_pref():
    st.title("🎨 Customize Your Design Plan")
    st.markdown("Let's fine-tune your preferences for a perfect design.")
