import streamlit as st
from modules.utils import load_product_data
from modules.color_util import extract_category_colors
from modules.components import render_css_user_pref, render_title_user_pref


    # --- Load CSS ---
    st.markdown("""
    <style>
    .main { background: #fffff; color: #0000000; }
    .stButton>button { border-radius: 8px; background: #7b00ff; color: white; transition: all 0.3s ease; margin-top: 0.5rem; }
    .stButton>button:hover { background: #9d4edd; transform: translateY(-2px); }
    .glow-card { background: rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 25px; margin: 15px 0; border: 1px solid rgba(255, 255, 255, 0.2); box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2); backdrop-filter: blur(10px); transition: all 0.3s ease; }
    .glow-card:hover { box-shadow: 0 6px 20px rgba(123, 0, 255, 0.3); }
    .section-title { font-size: 24px; font-weight: 700; color: #00000; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; }
    .stMultiSelect [data-baseweb="tag"] { background-color: #7b00ff; }
    button[kind="secondary"] { background-color: #ff4b4b !important; color: white !important; border-radius: 5px; padding: 2px 8px !important; margin-left: 10px; font-size: 12px; min-height: 10px !important; line-height: 1.2; }
    button[kind="secondary"]:hover { background-color: #cc0000 !important; }
    </style>
    """, unsafe_allow_html=True)

    st.title(" Customize Your Design Plan")
    st.markdown("Refine your preferences for the selected room elements.", unsafe_allow_html=True)

    # --- Initialize Session State ---

def initialize_session_state():

    if "selected_items" not in st.session_state:
        st.session_state.selected_items = []
    if "color_prefs" not in st.session_state:
        st.session_state.color_prefs = {}
    if "dominant_colors" not in st.session_state:
        st.session_state.dominant_colors = []
    if "budget" not in st.session_state:
        st.session_state.budget = 10000

def budget_section():
    with st.container():
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)

        st.markdown('<div class="section-title"> Review Your Budget</div>', unsafe_allow_html=True)
        min_budget = 1000
        new_budget = st.slider(
            "Total Budget (₹)",
            min_value=min_budget, max_value=200000,
            value=st.session_state.budget, step=500, format="₹%d"
        )

        st.session_state.budget = new_budget
        st.markdown(f'<p style="color: #00000;">Current Total Budget: ₹{st.session_state.budget:,}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def category_selection_section(category_colors):
    all_categories = sorted(list(category_colors.keys()))
    with st.container():
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title"> Manage Categories</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("**Add More Categories:**")
        available_to_add = [cat for cat in all_categories_in_csv if cat not in st.session_state.selected_items]

        if not available_to_add:

            st.caption("All available categories are selected.")
        else:
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                new_cats = st.multiselect("Select categories to add", options=available, label_visibility="collapsed")
            with col2:
                if st.button("➕ Add", key="add_categories", use_container_width=True) and new_cats:
                    for cat in new_cats:
                        if cat not in st.session_state.selected_items:
                            st.session_state.selected_items.append(cat)
                    st.rerun()
        st.markdown("---")
        st.markdown("**Currently Selected:**", unsafe_allow_html=True)
        if not st.session_state.selected_items:
            st.info("No categories selected yet.")
        else:
            num_cols = 3
            cols = st.columns(num_cols)
            for i, item in enumerate(st.session_state.selected_items):
                with cols[i % num_cols]:
                    item_col, btn_col = st.columns([0.85, 0.15])
                    with item_col:
                        st.markdown(f'<div class="stInfo" style="background-color: rgba(123, 0, 255, 0.2); padding: 5px 10px; border-radius: 5px; display: inline-block; width: 95%;">{item}</div>', unsafe_allow_html=True)
                    with btn_col:
                        if st.button("➖", key=f"remove_{item}", help=f"Remove {item}", type="secondary"):
                            st.session_state.selected_items.remove(item)
                            st.session_state.color_prefs.pop(item, None)
                            st.session_state.pop(f"color_family_{item}", None)
                            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

def color_preferences_section(category_colors):
    if st.session_state.selected_items:
        with st.container():
            st.markdown('<div class="glow-card">', unsafe_allow_html=True)

            st.markdown('<div class="section-title"> Pick Your Colors</div>', unsafe_allow_html=True)
            st.markdown("Select preferred color families. By default, only your room's dominant colors (if any) are selected. If no dominant color is available for a category, then all colors are selected by default.")

            for cat in st.session_state.selected_items:
                st.markdown(f"--- \n#### {cat}")
                colors = category_colors.get(cat, [])
                if not colors:
                    st.warning(f"No color options found for {cat}.")
                    st.session_state.color_prefs.pop(cat, None)
                    continue
                defaults = [c for c in st.session_state.dominant_colors if c in colors] or colors
                key = f"color_family_{cat}"
                if key not in st.session_state:
                    st.session_state[key] = defaults
                st.multiselect(f"Select colors for {cat}", options=colors, key=key, label_visibility="collapsed")
                st.session_state.color_prefs[cat] = st.session_state[key]
            st.markdown('</div>', unsafe_allow_html=True)

def generate_packages(category_colors, df):
    if st.session_state.selected_items:
        with st.container():
            st.markdown('<div class="glow-card">', unsafe_allow_html=True)

            st.markdown('<div class="section-title"> Generate Packages</div>', unsafe_allow_html=True)
            st.markdown("When you are satisfied with your category, color selections, and budget, click the button below to generate your design packages.")
            
            if st.button("Generate Packages", use_container_width=True):
                final_package = {"total_budget": st.session_state.budget, "categories": {}}

                for cat in st.session_state.selected_items:
                    available_set = set(category_colors.get(cat, []))
                    selected_set = set(st.session_state.color_prefs.get(cat, []))
                    # If user removed all colors, treat as all available are selected.
                    if not selected_set:
                        selected_set = available_set

            st.markdown('<div class="section-title">🚀 Generate Packages</div>', unsafe_allow_html=True)
            st.markdown("Once you’re happy with your selections, click below to generate your design packages.")

            budget_error_placeholder = st.empty()

            if st.button("Generate Packages", key="generate_final", use_container_width=True):
                selected_categories = st.session_state.selected_items

                # Calculate minimum required budget
                min_required_budget = 0
                missing_categories = []

                for cat in selected_categories:
                    cat_products = df[df['product_category'] == cat]
                    if not cat_products.empty:
                        min_price = cat_products['price'].min()
                        min_required_budget += min_price
                    else:
                        missing_categories.append(cat)

                # Check budget
                if st.session_state.budget < min_required_budget:
                    budget_error_placeholder.error(
                        f"❌ Insufficient budget! Minimum required to cover all selected categories is ₹{min_required_budget:,.2f}, "
                        f"but you only have ₹{st.session_state.budget:,.2f}."
                    )
                    return  
                elif missing_categories:
                    budget_error_placeholder.warning(
                        f"⚠️ No products found for the following categories: {', '.join(missing_categories)}. "
                        f"Please deselect them or upload product data."
                    )
                    return

                # Package is valid
                package = {"total_budget": st.session_state.budget, "categories": {}}
                for cat in selected_categories:
                    available = set(category_colors.get(cat, []))
                    selected = set(st.session_state.get(f"color_family_{cat}", []))
                    if not selected and available:
                        selected = available

                        not_selected = set()
                    else:
                        not_selected = available - selected
                    package["categories"][cat] = {
                        "selected_colors": list(selected),
                        "not_selected_colors": list(not_selected)
                    }

                st.session_state.package_summary = package
                st.success("✅ Packages generated! Redirecting...")
                st.switch_page("pages/page_packages.py")
            
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Select some categories to start customizing your plan.")


def main():
    st.set_page_config(page_title="RoomScapes AI - Preferences", layout="wide", initial_sidebar_state="expanded")
    render_css_user_pref()
    render_title_user_pref()
    initialize_session_state()

    csv_path = "products.csv"
    df = load_product_data(csv_path)
    category_colors = extract_category_colors(df)

    budget_section()
    category_selection_section(category_colors)
    color_preferences_section(category_colors)
    generate_packages(category_colors, df)

if __name__ == "__main__":

    main()




