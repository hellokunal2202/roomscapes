import streamlit as st
import pandas as pd
import os

# ---------- Helper Functions ----------

def load_product_data(csv_path):
    if not os.path.exists(csv_path):
        st.error("❌ Product CSV not found!")
        st.stop()
    df = pd.read_csv(csv_path)
    if df.empty:
        st.error("❌ Product CSV is empty!")
        st.stop()
    required_cols = ['product_category', 'color1', 'color2', 'color3']
    if not all(col in df.columns for col in required_cols):
        st.error(f"❌ Missing required columns: {', '.join(required_cols)}")
        st.stop()
    return df

def extract_category_colors(df):
    category_colors = {}
    for category in df['product_category'].unique():
        colors = df[df['product_category'] == category][['color1', 'color2', 'color3']].values.flatten()
        filtered_colors = [str(color).strip() for color in colors if pd.notnull(color) and str(color).strip()]
        unique_colors = list(set(filtered_colors)) or ["#FFFFFF"]
        category_colors[category] = unique_colors
    return category_colors

# ---------- Streamlit App ----------

def main():
    st.set_page_config(page_title="RoomScapes AI", layout="wide", initial_sidebar_state="expanded")

    # ------- Enhanced CSS Styling -------
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
        .scrolling-wrapper {
            display: flex;
            overflow-x: auto;
            overflow-y: hidden;
            padding: 10px 0;
            white-space: nowrap;
            -webkit-overflow-scrolling: touch;
        }
        .scrolling-wrapper::-webkit-scrollbar {
            height: 8px;
        }
        .scrolling-wrapper::-webkit-scrollbar-thumb {
            background: #7b00ff;
            border-radius: 4px;
        }
        .color-circle {
            width: 45px;
            height: 45px;
            border-radius: 50%;
            margin: 0 8px;
            border: 3px solid rgba(255, 255, 255, 0.8);
            cursor: pointer;
            display: inline-block;
            transition: all 0.2s ease;
        }
        .color-circle:hover {
            transform: scale(1.15);
            border-color: #7b00ff;
        }
        .color-circle.selected {
            border: 3px solid #7b00ff;
            box-shadow: 0 0 10px rgba(123, 0, 255, 0.7);
        }
        .color-buttons {
            margin-top: 8px;
        }
        .auto-allocated {
            color: #7b00ff;
            font-weight: bold;
            padding: 10px;
            border-radius: 8px;
            background: rgba(123, 0, 255, 0.1);
        }
    </style>
    """, unsafe_allow_html=True)


    st.title("🏠 RoomScapes AI — Design Your Dream Space")
    st.markdown("Transform your vision into reality with intelligent room design.", unsafe_allow_html=True)

    # ------- Load CSV -------
    df = load_product_data("products.csv")
    category_colors = extract_category_colors(df)
    all_categories = list(category_colors.keys())

    # ------- Session State -------
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

    # ------- Budget -------
    with st.container():
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">💰 Set Your Budget</div>', unsafe_allow_html=True)
        
        min_budget = max(1000, len(st.session_state.selected_items) * 1000)
        new_budget = st.slider(
            "Total Budget (₹)", 
            min_value=min_budget, 
            max_value=100000, 
            value=st.session_state.budget, 
            step=500,
            format="₹%d"
        )
        
        if new_budget != st.session_state.budget:
            st.session_state.budget = new_budget
            # When total budget changes, clear allocations so that they reinitialize.
            st.session_state.allocations = {}
            st.session_state.first_change_done = False
            
        st.markdown(f'<p style="color: #a0a0ff;">Selected: ₹{st.session_state.budget:,}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ------- Category Selection -------
    with st.container():
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🪄 Choose Categories</div>', unsafe_allow_html=True)
        
        available_categories = [c for c in all_categories if c not in st.session_state.selected_items]
        new_categories = st.multiselect(
            "Select room categories",
            available_categories,
            help="Pick the categories you want to design"
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
            st.info("Start by selecting some categories!")
        st.markdown('</div>', unsafe_allow_html=True)

    # ------- Color Preferences -------
    if st.session_state.selected_items:
        with st.container():
            st.markdown('<div class="glow-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🎨 Pick Your Colors</div>', unsafe_allow_html=True)
            
            for cat in st.session_state.selected_items:
                st.markdown(f"**{cat}**")
                colors = category_colors.get(cat, ["#FFFFFF"])
                if cat not in st.session_state.color_prefs:
                    st.session_state.color_prefs[cat] = []
                with st.container():
                    st.markdown('<div class="scrolling-wrapper">', unsafe_allow_html=True)
                    cols = st.columns(len(colors))
                    for i, color in enumerate(colors):
                        is_selected = color in st.session_state.color_prefs[cat]
                        css_class = "color-circle selected" if is_selected else "color-circle"
                        if cols[i].button(" ", key=f"{cat}_{color}", help=f"{color}"):
                            if is_selected:
                                st.session_state.color_prefs[cat].remove(color)
                            else:
                                st.session_state.color_prefs[cat].append(color)
                        cols[i].markdown(
                            f"<div class='{css_class}' style='background:{color};'></div>", 
                            unsafe_allow_html=True
                        )
                    st.markdown("</div>", unsafe_allow_html=True)
                    btn1, btn2 = st.columns([1, 1])
                    if btn1.button("✅ Select All", key=f"select_all_{cat}"):
                        st.session_state.color_prefs[cat] = colors.copy()
                    if btn2.button("❌ Clear All", key=f"clear_all_{cat}"):
                        st.session_state.color_prefs[cat] = []
                st.markdown(f"✅ Selected: {', '.join(st.session_state.color_prefs[cat]) or 'None'}")
            st.markdown('</div>', unsafe_allow_html=True)

    # ------- Budget Allocation -------
    if st.session_state.selected_items:
        with st.container():
            st.markdown('<div class="glow-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">💸 Allocate Budget</div>', unsafe_allow_html=True)

            selected_categories = st.session_state.selected_items
            total_budget = st.session_state.budget
            num_categories = len(selected_categories)

            # Calculate default equal allocation.
            equal_share = total_budget // num_categories
            remainder = total_budget - (equal_share * num_categories)

            # Initialize allocations if not present or incomplete.
            if not st.session_state.allocations or any(cat not in st.session_state.allocations for cat in selected_categories):
                st.session_state.allocations = {
                    cat: equal_share + (remainder if idx == 0 else 0)
                    for idx, cat in enumerate(selected_categories)
                }
                st.session_state.first_change_done = False

            # Reset button to restore default equal allocation.
            if st.button("Reset Allocations to Default"):
                st.session_state.allocations = {
                    cat: equal_share + (remainder if idx == 0 else 0)
                    for idx, cat in enumerate(selected_categories)
                }
                st.session_state.first_change_done = False

            # Display sliders for each category.
            for cat in selected_categories:
                old_val = st.session_state.allocations.get(cat, 0)
                # Use static slider endpoint: maximum always equals total_budget.
                new_val = st.slider(
                    f"{cat}",
                    min_value=0,
                    max_value=total_budget,
                    value=old_val,
                    step=500,
                    key=f"budget_{cat}"
                )
                # First change behavior: if no slider has yet been changed and this slider differs, reset others.
                if not st.session_state.first_change_done and new_val != old_val:
                    st.session_state.first_change_done = True
                    st.session_state.allocations[cat] = new_val
                    for other_cat in selected_categories:
                        if other_cat != cat:
                            st.session_state.allocations[other_cat] = 0
                else:
                    # Tentatively update allocation for this category.
                    tentative_allocations = st.session_state.allocations.copy()
                    tentative_allocations[cat] = new_val
                    if sum(tentative_allocations.values()) > total_budget:
                        st.warning("Exceeding total budget is not allowed!")
                        new_val = old_val  # revert change
                    st.session_state.allocations[cat] = new_val

            # Display a summary of the current allocations.
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("### Current Allocations")
            for cat in selected_categories:
                alloc = st.session_state.allocations.get(cat, 0)
                st.markdown(f"- **{cat}**: ₹{alloc:,}")
            st.markdown('</div>', unsafe_allow_html=True)

    # ------- Finalize -------
    if st.session_state.selected_items:
        if st.button("✨ Generate Design Plan", use_container_width=True):
            st.success("🎉 Design Plan Generated Successfully!")
            st.markdown("### Your Design Summary")
            summary = {
                "categories": st.session_state.selected_items,
                "color_preferences": st.session_state.color_prefs,
                "budget_allocation": st.session_state.allocations,
                "total_budget": st.session_state.budget
            }
            st.json(summary)
            st.balloons()

if __name__ == "__main__":
    main()
