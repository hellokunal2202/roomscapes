import streamlit as st
import pandas as pd
import time

# --- Page Setup ---
# No 'theme' argument here due to potential version incompatibility.
st.set_page_config(
    layout="wide",
    page_title="Product Catalog"
)

# --- Load Data ---
try:
    df = pd.read_csv("products.csv")
except FileNotFoundError:
    st.error("Error: products.csv not found. Please ensure it's in the correct directory.")
    st.stop()

# --- Page Title & Timestamp ---
st.title("Product Catalog")
current_datetime = time.strftime("%A, %B %d, %Y at %I:%M:%S %p %Z")
st.caption(f"Data last accessed on: {current_datetime}")

# --- Custom CSS for Dark Theme & Card Styling ---
# Overriding base styles and applying card effects
st.markdown("""
    <style>
    /* --- Base Theme Overrides (Dark) --- */
    body {
        background-color: #0E1117 !important; /* Dark background */
        color: #FAFAFA !important; /* Light default text */
    }
    /* Make title text stand out */
    .stApp > header {
        background-color: transparent; /* Remove header background if any */
    }
    h1 {
        color: #FAFAFA; /* Ensure title is light */
    }
    /* Target sidebar - selector might need adjustment based on Streamlit version */
    /* Using a more specific selector for the main sidebar content area */
    section[data-testid="stSidebar"] > div:first-child {
        background-color: #1C1F26 !important; /* Darker sidebar background */
    }
    /* Sidebar Header */
     section[data-testid="stSidebar"] h2 {
          color: #FAFAFA;
     }
     /* Sidebar Widget Labels */
     section[data-testid="stSidebar"] .st-emotion-cache-1qg0ysv,
     section[data-testid="stSidebar"] .st-emotion-cache-ue6h4q { /* Common label classes */
         color: #bbb !important;
     }

    /* Attempt to style common widgets */
    .stTextInput input, .stSelectbox select, .stTextArea textarea, .stMultiSelect div[data-baseweb="select"] > div {
        background-color: #262730 !important; /* Dark widget background */
        color: #FAFAFA !important; /* Light widget text */
        border: 1px solid #555 !important; /* Darker border */
        border-radius: 5px;
    }
    /* Slider styling */
    .stSlider [data-baseweb="slider"] {
        color: #FF8C00 !important; /* Try to color the slider track/thumb orange */
    }

    /* Style Load More button for dark theme */
     .stButton>button {
         background-color: #FF8C00 !important; /* Orange background */
         color: #FFFFFF !important; /* White text */
         border: none !important; /* Remove default border */
         border-radius: 5px !important;
         padding: 0.5rem 1rem !important;
     }
     .stButton>button:hover {
          background-color: #E07B00 !important; /* Darker orange on hover */
          color: #FFFFFF !important;
     }
     .stButton>button:focus { /* Ensure focus state looks good */
        box-shadow: 0 0 0 0.2rem rgba(255, 140, 0, 0.5) !important;
        outline: none !important;
     }


    /* --- Product Card Specific CSS (Dark Theme) --- */
    .product-card:hover {
        transform: scale(1.03);
        cursor: pointer;
        box-shadow: 0px 5px 15px rgba(255, 140, 0, 0.4); /* Orangish glow on hover */
    }
    .product-card {
        padding: 15px;
        margin-bottom: 15px;
        background-color: #262730; /* Dark background for cards */
        border: 1px solid #444; /* Darker border for dark theme */
        border-radius: 8px;
        height: 100%;
        display: flex;
        flex-direction: column;
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        color: #FAFAFA; /* Default light text for card */
    }
    .product-link {
        text-decoration: none;
        color: inherit;
        display: block;
        height: 100%;
    }
    .product-content {
        display: flex;
        gap: 15px;
        align-items: flex-start;
        flex-grow: 1;
    }
    .product-image {
         width: 80px;
         height: 80px;
         border-radius: 5px;
         object-fit: contain;
         flex-shrink: 0;
         background-color: #FFF; /* Keep white background for image box */
         padding: 2px;
    }
    .product-details {
        flex-grow: 1;
    }
    .product-details h5 {
         margin: 0 0 5px 0;
         font-weight: bold;
         color: #FAFAFA; /* Light heading color */
    }
     .product-details p {
         margin: 0 0 4px 0;
         font-size: 0.9em;
         color: #bbb; /* Lighter grey for details text */
     }
     .product-description {
         margin: 0;
         font-size: 0.85em;
         color: #999; /* Even lighter grey */
         font-style: italic;
     }
    </style>
""", unsafe_allow_html=True)

# --- Define column names ---
cat_column = 'product_category'
price_column = 'price'
color_column = 'color'
name_column = 'product_name'
img_column = 'image_url'
url_column = 'product_url'
desc_column = 'description'

# Check essential columns
required_columns = [cat_column, price_column, name_column]
missing_cols = [col for col in required_columns if col not in df.columns]
if missing_cols:
    st.error(f"Error: Missing required columns in products.csv: {', '.join(missing_cols)}")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("Filter Products")

# --- 1. Category Filter ---
categories = ["All Categories"] + sorted(df[cat_column].dropna().unique().tolist())
selected_category = st.sidebar.selectbox(
    "Select Category",
    options=categories,
    index=0
)

# Filter by Category for dynamic options
if selected_category == "All Categories":
    category_filtered_df = df.copy()
else:
    category_filtered_df = df[df[cat_column] == selected_category].copy()

# --- 2. Price Filter ---
st.sidebar.markdown("---")
if not category_filtered_df.empty:
    valid_prices = category_filtered_df[price_column].dropna()
    if not valid_prices.empty:
        min_price = int(valid_prices.min())
        max_price = int(valid_prices.max())
        if min_price == max_price: max_price += 1 # Ensure range
        elif max_price < min_price: max_price = min_price + 1 # Safety check
    else: min_price, max_price = 0, 1
else:
    min_price = 0
    max_price = int(df[price_column].dropna().max()) if not df.empty and not df[price_column].dropna().empty else 1000
    max_price = max(min_price + 1, max_price)

price_range = st.sidebar.slider(
    f"Select Price Range (₹)",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price)
)

# Filter further by Price for color options
price_filtered_df = category_filtered_df[
    (category_filtered_df[price_column].fillna(-1) >= price_range[0]) &
    (category_filtered_df[price_column].fillna(-1) <= price_range[1])
]

# --- 3. Color Filter ---
st.sidebar.markdown("---")
has_color_column = color_column in price_filtered_df.columns
available_colors = []
if has_color_column and not price_filtered_df.empty:
    available_colors = sorted(price_filtered_df[color_column].dropna().unique().tolist())

if available_colors:
    selected_colors = st.sidebar.multiselect(
        "Select Color(s)", options=available_colors, default=available_colors
    )
elif has_color_column:
    st.sidebar.info("No color options match filters.")
    selected_colors = []
else:
    st.sidebar.caption("Color filter unavailable.")
    selected_colors = []

# --- 4. Search Filter ---
st.sidebar.markdown("---")
search_term = st.sidebar.text_input(f"Search by Product Name").lower()

# --- Apply ALL Filters ---
final_filtered_df = df.copy() # Start fresh

if selected_category != "All Categories":
    final_filtered_df = final_filtered_df[final_filtered_df[cat_column] == selected_category]

final_filtered_df = final_filtered_df[
    (final_filtered_df[price_column].fillna(-1) >= price_range[0]) &
    (final_filtered_df[price_column].fillna(-1) <= price_range[1])
]

if has_color_column and selected_colors and available_colors:
    if set(selected_colors) != set(available_colors):
         final_filtered_df = final_filtered_df[final_filtered_df[color_column].isin(selected_colors)]

if search_term:
    final_filtered_df = final_filtered_df[
        final_filtered_df[name_column].fillna('').str.lower().str.contains(search_term)
    ]

# --- Pagination Setup ---
ITEMS_PER_PAGE = 8
if 'visible_items' not in st.session_state:
    st.session_state.visible_items = ITEMS_PER_PAGE

current_filter_key = f"{selected_category}-{price_range}-{','.join(sorted(selected_colors))}-{search_term}"
if 'last_filter_key' not in st.session_state or st.session_state.last_filter_key != current_filter_key:
    st.session_state.visible_items = ITEMS_PER_PAGE
    st.session_state.last_filter_key = current_filter_key

visible_df = final_filtered_df.head(st.session_state.visible_items)

# --- Display Results ---
st.subheader(f"Showing {len(visible_df)} of {len(final_filtered_df)} Products")
if len(final_filtered_df) == 0:
    filters_active = (selected_category != "All Categories" or price_range != (min_price, max_price) or search_term or (has_color_column and selected_colors and set(selected_colors) != set(available_colors)))
    if filters_active: st.warning("No products match filters.")
    elif len(df) == 0: st.warning("Product data is empty.")

# Display Product Cards
num_columns = 2
cols = st.columns(num_columns)
col_index = 0
FALLBACK_IMAGE_URL = "https://via.placeholder.com/80x80.png?text=No+Image"

for index, row in visible_df.iterrows():
    with cols[col_index % num_columns]:
        img_url = row.get(img_column, FALLBACK_IMAGE_URL)
        if not isinstance(img_url, str) or not img_url.startswith(('http://', 'https://')):
            img_url = FALLBACK_IMAGE_URL

        # Card Content HTML
        product_content_html = f"""
        <div class="product-content">
            <img src="{img_url}" class="product-image" alt="{row.get(name_column, 'Product image')}" />
            <div class="product-details">
                <h5>{row.get(name_column, 'N/A')}</h5>
                <p><b>Category:</b> {row.get(cat_column, 'N/A')}</p>
                <p><b>Price:</b> ₹{row.get(price_column, 'N/A')}</p>
                {f'<p><b>Color:</b> {row.get(color_column, "N/A")}</p>' if has_color_column and pd.notna(row.get(color_column)) else ''}
                <p class="product-description">{row.get(desc_column, '')}</p>
            </div>
        </div>
        """
        # Final Card HTML with Link
        product_html = f"""
        <div class="product-card" key="prod-{index}">
            <a href="{row.get(url_column, '#' )}" target="_blank" class="product-link">
                 {product_content_html}

        </div>
        """
        st.markdown(product_html, unsafe_allow_html=True)
    col_index += 1

# --- Load More Button ---
st.markdown("<hr style='border-top: 1px solid #444;'>", unsafe_allow_html=True) # Darker separator
if st.session_state.visible_items < len(final_filtered_df):
    buffer_left, button_col, buffer_right = st.columns([1, 1.5, 1])
    with button_col:
        if st.button("Load More Products", key="load_more", use_container_width=True):
            st.session_state.visible_items += ITEMS_PER_PAGE
            # Rerun is automatic