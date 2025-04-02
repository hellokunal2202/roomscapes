import streamlit as st
import pandas as pd
import os
# Assuming color_util provides categorize_color_family and group_colors_by_family
# No need to import them directly if they are used within modules called below
from modules import color_util

# ---------- Helper Functions ----------
def load_product_data(csv_path):
    """Loads product data, ensuring required columns exist."""
    if not os.path.exists(csv_path):
        st.error(f"❌ Product CSV not found at: {csv_path}")
        st.stop()
    try:
        df = pd.read_csv(csv_path)
        if df.empty:
            st.error("❌ Product CSV is empty!")
            st.stop()
        required_cols = ['product_category', 'color'] # Add 'price' if needed later
        if not all(col in df.columns for col in required_cols):
            missing = [col for col in required_cols if col not in df.columns]
            st.error(f"❌ Missing required columns in CSV: {', '.join(missing)}")
            st.stop()
        # Basic cleaning: remove rows with missing category or color
        df.dropna(subset=['product_category', 'color'], inplace=True)
        # Ensure color column is string type
        df['color'] = df['color'].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"❌ Error reading product CSV: {e}")
        st.stop()


def extract_category_colors(df):
    """
    Extracts available color family names for each product category from the DataFrame.
    Assumes the 'color' column already contains color family names (e.g., "Red", "Blue").
    """
    category_colors = {}
    default_families = ["Red", "Blue", "Green", "Gray", "White", "Black", "Brown", "Beige"] # Define a reasonable default set

    for category in df['product_category'].unique():
        # Get unique, non-empty color family names for the category
        colors = df[df['product_category'] == category]['color'].dropna().unique()
        # Filter out any potential empty strings after stripping
        filtered_colors = sorted([str(c).strip() for c in colors if str(c).strip()])

        if filtered_colors:
            # Create a simple mapping from family name to itself (for consistency if structure changes later)
            # Use the actual available colors as keys
            grouped = {family: [family] for family in filtered_colors}
        else:
            # If a category in the CSV has NO colors listed, provide the default set
            grouped = {family: [family] for family in default_families}

        category_colors[category] = grouped

    # Ensure all expected categories (even if not in CSV) have some colors
    # This might be needed if selected_items can come from detection/recommendation
    # and might not be present in a minimal products.csv
    # For now, we only process categories found in the CSV.

    return category_colors

# ---------- Streamlit App ----------
def main():
    st.set_page_config(page_title="RoomScapes AI - Preferences", layout="wide", initial_sidebar_state="expanded")

    # --- Load CSS (assuming it's mostly static) ---
    st.markdown("""
    <style>
    /* Basic styling from previous version */
    .main { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: #ffffff; }
    .stButton>button { border-radius: 8px; background: #7b00ff; color: white; transition: all 0.3s ease; margin-top: 0.5rem; }
    .stButton>button:hover { background: #9d4edd; transform: translateY(-2px); }
    .glow-card { background: rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 25px; margin: 15px 0; border: 1px solid rgba(255, 255, 255, 0.2); box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2); backdrop-filter: blur(10px); transition: all 0.3s ease; }
    .glow-card:hover { box-shadow: 0 6px 20px rgba(123, 0, 255, 0.3); }
    .section-title { font-size: 24px; font-weight: 700; color: #e0e0ff; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; }
    /* Specific adjustments */
    .stMultiSelect [data-baseweb="tag"] { background-color: #7b00ff; } /* Style selected items */
    </style>
    """, unsafe_allow_html=True)

    st.title("🎨 Customize Your Design Plan")
    st.markdown("Refine your preferences for the selected room elements.", unsafe_allow_html=True)

    # --- Get Data from Session State (Check if essential data exists) ---
    if "selected_items" not in st.session_state or not st.session_state.selected_items:
        st.warning("⚠️ No items selected from the previous step. Please go back and select items to redesign.")
        if st.button("⬅️ Go Back"):
            st.switch_page("main.py") # Or your main page script name
        st.stop()

    # Ensure other necessary states exist, provide defaults if missing
    if "budget" not in st.session_state: st.session_state.budget = 10000
    if "color_prefs" not in st.session_state: st.session_state.color_prefs = {}
    if "allocations" not in st.session_state: st.session_state.allocations = {}
    if "first_change_done" not in st.session_state: st.session_state.first_change_done = False
    # Get dominant colors (provide empty list default)
    dominant_color_families = st.session_state.get('dominant_colors', [])

    # --- Loading Product Data ---
    # Use a path relative to the app or an absolute path if necessary
    df = load_product_data("products.csv") # Make sure this path is correct
    # Get available colors per category from the loaded data
    category_colors = extract_category_colors(df)
    # Get a list of all categories present in the product data
    all_categories_in_csv = list(category_colors.keys())

    # Filter selected items to only those present in the product data (important for color/budget lookup)
    valid_selected_items = [item for item in st.session_state.selected_items if item in all_categories_in_csv]
    invalid_items = [item for item in st.session_state.selected_items if item not in all_categories_in_csv]

    if invalid_items:
        st.warning(f"⚠️ The following selected items were not found in the product data and will be ignored: {', '.join(invalid_items)}")

    # Update session state to only work with valid items found in products.csv
    st.session_state.selected_items = valid_selected_items
    if not valid_selected_items:
        st.error("❌ None of the selected items were found in the product data. Cannot proceed.")
        st.stop()


    # --- Handling Budget Section (remains largely the same) ---
    with st.container():
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">💰 Review Your Budget</div>', unsafe_allow_html=True)

        # Ensure min_budget is reasonable, maybe based on selected items
        min_budget_per_item = 500 # Example minimum cost per item type
        min_budget = max(1000, len(st.session_state.selected_items) * min_budget_per_item)

        new_budget = st.slider(
            "Total Budget (₹)",
            min_value=min_budget,
            max_value=200000, # Or higher if needed
            value=st.session_state.budget,
            step=500,
            format="₹%d",
            help=f"Adjust your total budget. Minimum suggested: ₹{min_budget:,}"
        )

        if new_budget != st.session_state.budget:
            st.session_state.budget = new_budget
            # Reset allocations when budget changes
            st.session_state.allocations = {}
            st.session_state.first_change_done = False
            st.rerun() # Rerun to recalculate allocations

        st.markdown(f'<p style="color: #a0a0ff;">Current Total Budget: ₹{st.session_state.budget:,}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


    # --- Managing Category Display (Show selected, no add/remove here) ---
    with st.container():
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🪄 Your Selected Categories</div>', unsafe_allow_html=True)
        if st.session_state.selected_items:
            # Display selected items simply
            st.markdown("You are customizing preferences for:")
            cols = st.columns(len(st.session_state.selected_items))
            for i, item in enumerate(st.session_state.selected_items):
                 with cols[i]:
                     st.info(f"✔️ {item}") # Just display them
        else:
             # This case should be handled by the check at the start
             st.warning("No valid items selected.")
        st.markdown('</div>', unsafe_allow_html=True)


    # --- Handling Color Preferences (MODIFIED DEFAULTS) ---
    if st.session_state.selected_items:
        with st.container():
            st.markdown('<div class="glow-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🎨 Pick Your Colors</div>', unsafe_allow_html=True)
            st.markdown("Select your preferred color families for each item. Defaults are based on your room's dominant colors.")

            # Use columns for better layout if many items
            num_items = len(st.session_state.selected_items)
            cols = st.columns(min(num_items, 3)) # Max 3 columns

            for i, cat in enumerate(st.session_state.selected_items):
                 with cols[i % 3]: # Cycle through columns
                    st.markdown(f"**{cat}**")

                    # Get available color families for this specific category from product data
                    # Use .get() with a default empty dict for safety
                    available_color_info = category_colors.get(cat, {})
                    available_families_for_cat = sorted(list(available_color_info.keys()))

                    if not available_families_for_cat:
                        st.warning(f"No color options found for {cat} in product data.")
                        continue # Skip to next category if no colors defined

                    # --- MODIFIED DEFAULT LOGIC ---
                    # Initialize color_prefs for this category if not already set
                    if cat not in st.session_state.color_prefs:
                        # Find which dominant colors are actually available for this category
                        preferred_default = [
                            family for family in dominant_color_families
                            if family in available_families_for_cat
                        ]

                        # If any preferred colors match, use them as default.
                        # Otherwise, default to *all* available families for this category.
                        if preferred_default:
                            initial_default_for_cat = preferred_default
                        else:
                            # Fallback: If no dominant colors match, select all available for this category
                            initial_default_for_cat = available_families_for_cat
                            # Alternative fallback: Select just the first available color
                            # initial_default_for_cat = [available_families_for_cat[0]] if available_families_for_cat else []

                        st.session_state.color_prefs[cat] = initial_default_for_cat
                    # --- END OF MODIFIED DEFAULT LOGIC ---

                    # Create the multiselect widget
                    widget_key = f"color_family_{cat}"
                    selected_families = st.multiselect(
                        label=f"Select color families for {cat}", # Use label param
                        options=available_families_for_cat, # Show all available families
                        default=st.session_state.color_prefs[cat], # Use the calculated default
                        key=widget_key,
                        label_visibility="collapsed" # Hide label if markdown title is enough
                    )

                    # Update session state if the selection changes
                    # Allow user to select nothing (empty list)
                    if selected_families != st.session_state.color_prefs[cat]:
                        st.session_state.color_prefs[cat] = selected_families
                        # No need to rerun usually, unless other elements depend *immediately* on this value
                        # st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)


    # --- Managing Budget Allocation (MODIFIED LOGIC) ---
    if st.session_state.selected_items:
        with st.container():
            st.markdown('<div class="glow-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">💸 Allocate Budget</div>', unsafe_allow_html=True)

            selected_categories = st.session_state.selected_items
            total_budget = st.session_state.budget
            num_categories = len(selected_categories)

            # Check if allocations need recalculation (e.g., budget changed, items changed)
            # Check if the set of keys in allocations matches selected_items
            alloc_keys = set(st.session_state.allocations.keys())
            selected_keys = set(selected_categories)
            needs_recalc = (alloc_keys != selected_keys) or (not st.session_state.allocations) or (sum(st.session_state.allocations.values()) != total_budget and not st.session_state.first_change_done)


            if needs_recalc:
                # Calculate default equal allocation
                if num_categories > 0:
                    equal_share = total_budget // num_categories
                    remainder = total_budget % num_categories
                else:
                    equal_share, remainder = 0, 0

                st.session_state.allocations = {}
                for idx, cat in enumerate(selected_categories):
                    # Distribute remainder to the first few items
                    share = equal_share + (1 if idx < remainder else 0)
                    st.session_state.allocations[cat] = share
                st.session_state.first_change_done = False # Reset flag after recalculating


            # Button to restore default equal allocation
            if st.button("🔄 Reset Allocations to Equal Share"):
                # Force recalculation logic above by clearing allocations and flag
                 st.session_state.allocations = {}
                 st.session_state.first_change_done = False
                 st.rerun() # Rerun to trigger the recalculation


            # --- Slider Logic Refined ---
            st.markdown("Adjust how much of your budget goes to each category:")
            current_allocations = st.session_state.allocations.copy()
            changed_category = None
            change_amount = 0

            for cat in selected_categories:
                # Default slider value comes from current state
                current_val = current_allocations.get(cat, 0)
                max_possible_val = total_budget - (sum(current_allocations.values()) - current_val)

                new_val = st.slider(
                    f"{cat}",
                    min_value=0,
                    # Max should not exceed total budget minus allocations for *other* items
                    max_value=total_budget, # Let Streamlit handle the visual max initially
                    value=current_val,
                    step=100, # Smaller step might be better for allocation
                    key=f"budget_{cat}",
                    format="₹%d"
                )

                if new_val != current_val:
                    changed_category = cat
                    change_amount = new_val - current_val
                    st.session_state.first_change_done = True # Mark that user has interacted


            # --- Adjustment Logic ---
            if changed_category is not None:
                new_total = sum(current_allocations.values()) + change_amount
                over_budget = new_total - total_budget

                if over_budget > 0:
                    # Try to reduce from other categories proportionally (or equally)
                    other_cats = [c for c in selected_categories if c != changed_category]
                    total_in_others = sum(current_allocations.get(c, 0) for c in other_cats)

                    reductions = {}
                    reduced_so_far = 0

                    if total_in_others > 0:
                        # Reduce proportionally
                        for c in other_cats:
                            reduction = int(over_budget * (current_allocations.get(c, 0) / total_in_others))
                            reductions[c] = min(reduction, current_allocations.get(c, 0)) # Don't reduce below 0
                            reduced_so_far += reductions[c]

                        # If proportional reduction wasn't enough (due to rounding/minimums), reduce evenly
                        remaining_reduction = over_budget - reduced_so_far
                        if remaining_reduction > 0:
                            cats_with_value = [c for c in other_cats if current_allocations.get(c,0) - reductions.get(c,0) > 0]
                            if cats_with_value:
                                per_cat_extra_reduction = remaining_reduction // len(cats_with_value)
                                remainder_extra = remaining_reduction % len(cats_with_value)
                                for i, c in enumerate(cats_with_value):
                                     extra = per_cat_extra_reduction + (1 if i < remainder_extra else 0)
                                     reduction_val = min(extra, current_allocations.get(c,0) - reductions.get(c,0))
                                     reductions[c] = reductions.get(c, 0) + reduction_val
                                     reduced_so_far += reduction_val


                    # Apply the changes
                    current_allocations[changed_category] += change_amount # Apply the user's intended change first
                    for c, reduction in reductions.items():
                         current_allocations[c] -= reduction

                    # Final check - clamp values and adjust the changed category if still over budget
                    final_total = sum(current_allocations.values())
                    if final_total > total_budget:
                         # Reduce the category the user just changed
                         current_allocations[changed_category] -= (final_total - total_budget)

                else:
                    # If under budget, just apply the change
                     current_allocations[changed_category] += change_amount


                # Update session state and rerun
                st.session_state.allocations = current_allocations
                st.rerun()


            # Displaying summary of current allocations
            st.markdown("---")
            st.markdown("##### Current Allocations:")
            alloc_total = 0
            for cat in selected_categories:
                alloc = st.session_state.allocations.get(cat, 0)
                alloc_total += alloc
                st.markdown(f"- **{cat}**: ₹ {alloc:,}")

            st.markdown(f"**Total Allocated:** ₹ {alloc_total:,} / ₹ {total_budget:,}")
            if alloc_total > total_budget:
                 st.error("Budget exceeded! Adjust sliders.")
            elif alloc_total < total_budget:
                 st.warning(f"₹ {total_budget - alloc_total:,} remaining budget is unallocated.")


            st.markdown('</div>', unsafe_allow_html=True)


    # --- Finalizing ---
    if st.session_state.selected_items:
        st.markdown("---") # Separator before final button
        if st.button("✨ Generate Design Plan", use_container_width=True, type="primary"):
             # Check if budget allocation is valid
            current_total_allocation = sum(st.session_state.allocations.values())
            if current_total_allocation > st.session_state.budget:
                st.error("Cannot generate plan. Your total allocation exceeds the total budget.")
            elif not st.session_state.color_prefs or any(not prefs for prefs in st.session_state.color_prefs.values()):
                 # Check if any category has empty color preferences selected
                 st.warning("⚠️ Please select at least one color family for each category.")
            else:
                # Proceed to generate summary (or next step)
                st.success("🎉 Preferences Confirmed! Preparing Your Design Plan...")
                st.markdown("### Your Design Summary")
                summary = {
                    "selected_categories": st.session_state.selected_items,
                    "color_preferences": st.session_state.color_prefs, # Contains selected color family names per category
                    "budget_allocation": st.session_state.allocations,
                    "total_budget": st.session_state.budget
                }
                st.json(summary) # Display the summary data
                st.balloons()
                # Here you would potentially switch to another page or trigger the actual plan generation
                # st.switch_page("pages/results_page.py")

if __name__ == "__main__":
    # Set CWD if needed, or ensure products.csv is in the right place
    # print(f"Current working directory: {os.getcwd()}")
    main()