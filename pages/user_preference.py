import streamlit as st
import pandas as pd
import os
from modules import color_util
from modules.color_util import categorize_color_family, group_colors_by_family

# ---------- Helper Functions ----------
def load_product_data(csv_path):
    if not os.path.exists(csv_path):
        st.error("❌ Product CSV not found!")
        st.stop()
    df = pd.read_csv(csv_path)
    if df.empty:
        st.error("❌ Product CSV is empty!")
        st.stop()
    required_cols = ['product_category', 'color1']
    if not all(col in df.columns for col in required_cols):
        st.error(f"❌ Missing required columns: {', '.join(required_cols)}")
        st.stop()
    return df

def extract_category_colors(df):
    """Extracting colors grouped by color family for each category"""
    category_colors = {}
    for category in df['product_category'].unique():
        # Getting raw hex codes
        colors = df[df['product_category'] == category]['color1'].dropna().unique()
        filtered_colors = [str(c).strip() for c in colors if str(c).strip()]
        
        # Grouping colors into families
        if filtered_colors:
            grouped = group_colors_by_family(filtered_colors)
        else:
            grouped = {"Neutral": ["#FFFFFF"]}  # Defaulting if no colors
            
        category_colors[category] = grouped
        
    return category_colors

# ---------- Streamlit App ----------
def main():
    st.set_page_config(page_title="RoomScapes AI", layout="wide", initial_sidebar_state="expanded")

    # Enhancing CSS for overall styling and color circles
    st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        color: #ffffff;
    }
    .stButton>button {
        border-radius: 8px;
        background: #7b00ff;
        color: white;
        transition: all 0.3s ease;
        margin-top: 0.5rem;
    }
    .stButton>button:hover {
        background: #9d4edd;
        transform: translateY(-2px);
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
    .glow-card:hover {
        box-shadow: 0 6px 20px rgba(123, 0, 255, 0.3);
    }
    .section-title {
        font-size: 24px;
        font-weight: 700;
        color: #e0e0ff;
        margin-bottom: 15px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .color-circle {
        display: inline-block;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        margin-right: 5px;
        vertical-align: middle;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🏠 RoomScapes AI — Design Your Dream Space")
    st.markdown("Transforming your vision into reality with intelligent room design.", unsafe_allow_html=True)

    # ------- Loading CSV -------
    df = load_product_data("products.csv")
    category_colors = extract_category_colors(df)
    all_categories = list(category_colors.keys())

    # ------- Setting Up Session State -------
    if "selected_items" not in st.session_state:
        st.session_state.selected_items = []
    if "budget" not in st.session_state:
        st.session_state.budget = 10000
    if "color_prefs" not in st.session_state:
        st.session_state.color_prefs = {}
    if "allocations" not in st.session_state:
        st.session_state.allocations = {}
    if "first_change_done" not in st.session_state:
        st.session_state.first_change_done = False

    # ------- Handling Budget Section -------
    with st.container():
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">💰 Set Your Budget</div>', unsafe_allow_html=True)

        min_budget = max(1000, len(st.session_state.selected_items) * 1000)
        new_budget = st.slider(
            "Total Budget (₹)",
            min_value=min_budget,
            max_value=200000,
            value=st.session_state.budget,
            step=500,
            format="₹%d"
        )

        if new_budget != st.session_state.budget:
            st.session_state.budget = new_budget
            st.session_state.allocations = {}
            st.session_state.first_change_done = False

        st.markdown(f'<p style="color: #a0a0ff;">Selected: ₹{st.session_state.budget:,}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ------- Managing Category Selection -------
    with st.container():
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🪄 Choose Categories</div>', unsafe_allow_html=True)

        available_categories = [c for c in all_categories if c not in st.session_state.selected_items]
        new_categories = st.multiselect(
            "Select room categories",
            available_categories,
            help="Picking the categories you want to design"
        )

        if st.button("➕ Add Categories", use_container_width=True):
            st.session_state.selected_items.extend(new_categories)
            st.session_state.selected_items = list(set(st.session_state.selected_items))

        if st.session_state.selected_items:
            st.markdown("**Your Selections:**")
            cols = st.columns(4)
            for i, item in enumerate(st.session_state.selected_items):
                with cols[i % 4]:
                    if st.button(f"❌ {item}", key=f"remove_{item}", use_container_width=True):
                        st.session_state.selected_items.remove(item)
                        st.session_state.color_prefs.pop(item, None)
                        st.session_state.allocations.pop(item, None)
                        st.session_state.first_change_done = False
        else:
            st.info("Starting by selecting some categories!")
        st.markdown('</div>', unsafe_allow_html=True)

    # ------- Handling Color Preferences (Dropdown Style) -------
    if st.session_state.selected_items:
        with st.container():
            st.markdown('<div class="glow-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🎨 Pick Your Colors</div>', unsafe_allow_html=True)

            for cat in st.session_state.selected_items:
                st.markdown(f"**{cat}**")
                color_families = category_colors.get(cat, {"Neutral": ["#FFFFFF"]})

                # Ensuring session state is initializing
                if cat not in st.session_state.color_prefs:
                    st.session_state.color_prefs[cat] = []

                # Creating a unique key for the widget
                widget_key = f"color_family_{cat}"

                # Using a placeholder for better reactivity
                container = st.empty()
                
                # Forcing UI update with a placeholder
                with container:
                    selected_families = st.multiselect(
                        f"Select color families for {cat}",
                        options=list(color_families.keys()),
                        default=st.session_state.color_prefs[cat],
                        key=widget_key
                    )

                # Ensuring immediate updating
                if selected_families != st.session_state.color_prefs[cat]:
                    st.session_state.color_prefs[cat] = selected_families
                    st.rerun()  

                # Displaying color swatches
                if selected_families:
                    st.markdown("**Selected Colors:**")
                    for family in selected_families:
                        hex_codes = color_families.get(family, [])
                        st.markdown(f"*{family}*:")
                        cols = st.columns(8)
                        for idx, hex_code in enumerate(hex_codes):
                            with cols[idx % 8]:
                                st.markdown(
                                    f"<div class='color-circle' style='background-color:{hex_code}' title='{hex_code}'></div>",
                                    unsafe_allow_html=True
                                )
                st.write("---")

            st.markdown('</div>', unsafe_allow_html=True)

    # ------- Managing Budget Allocation -------
    if st.session_state.selected_items:
        with st.container():
            st.markdown('<div class="glow-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">💸 Allocate Budget</div>', unsafe_allow_html=True)

            selected_categories = st.session_state.selected_items
            total_budget = st.session_state.budget
            num_categories = len(selected_categories)

            # Calculating default equal allocation
            equal_share = total_budget // num_categories
            remainder = total_budget - (equal_share * num_categories)

            # Initializing allocations if not present or incomplete
            if not st.session_state.allocations or any(cat not in st.session_state.allocations for cat in selected_categories):
                st.session_state.allocations = {
                    cat: equal_share + (remainder if idx == 0 else 0)
                    for idx, cat in enumerate(selected_categories)
                }
                st.session_state.first_change_done = False

            # Resetting button to restore default equal allocation
            if st.button("Reset Allocations to Default"):
                st.session_state.allocations = {
                    cat: equal_share + (remainder if idx == 0 else 0)
                    for idx, cat in enumerate(selected_categories)
                }
                st.session_state.first_change_done = False

            # Displaying sliders for each category
            for cat in selected_categories:
                old_val = st.session_state.allocations.get(cat, 0)
                new_val = st.slider(
                    f"{cat}",
                    min_value=0,
                    max_value=total_budget,
                    value=old_val,
                    step=500,
                    key=f"budget_{cat}"
                )
                # Handling first change logic
                if not st.session_state.first_change_done and new_val != old_val:
                    st.session_state.first_change_done = True
                    st.session_state.allocations[cat] = new_val
                    for other_cat in selected_categories:
                        if other_cat != cat:
                            st.session_state.allocations[other_cat] = 0
                else:
                    # Tentatively updating allocation
                    tentative_allocations = st.session_state.allocations.copy()
                    tentative_allocations[cat] = new_val
                    if sum(tentative_allocations.values()) > total_budget:
                        st.warning("Exceeding total budget is not allowed!")
                        new_val = old_val  # reverting change
                    st.session_state.allocations[cat] = new_val

            # Displaying summary of current allocations
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("### Current Allocations")
            for cat in selected_categories:
                alloc = st.session_state.allocations.get(cat, 0)
                st.markdown(f"- **{cat}**: ₹{alloc:,}")
            st.markdown('</div>', unsafe_allow_html=True)

    # ------- Finalizing -------
    if st.session_state.selected_items:
        if st.button("✨ Generate Design Plan", use_container_width=True):
            # Mapping selected families to actual hex codes
            color_prefs_expanded = {}
            for cat, families in st.session_state.color_prefs.items():
                color_prefs_expanded[cat] = []
                for family in families:
                    color_prefs_expanded[cat].extend(category_colors[cat].get(family, []))
            
            st.success("🎉 Design Plan Generated Successfully!")
            st.markdown("### Your Design Summary")
            summary = {
                "categories": st.session_state.selected_items,
                "color_preferences": color_prefs_expanded,  # Now containing actual hex codes
                "budget_allocation": st.session_state.allocations,
                "total_budget": st.session_state.budget
            }
            st.json(summary)
            st.balloons()

if __name__ == "__main__":
    main()