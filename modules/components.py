import streamlit as st

def inject_css():
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
    .stButton{
        display: flex;
        justify-content: center;
        margin: 20px 0;
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
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
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
        <h1 class="header-text">✨ RoomScapes AI</h1>
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
