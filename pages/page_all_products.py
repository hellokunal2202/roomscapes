import streamlit as st
import pandas as pd

# Load data
df = pd.read_csv("products.csv")

# Page title
st.title("Showing all product")

# Custom CSS for cursor pointer and hover effect
st.markdown("""
    <style>
    .product-card:hover {
        
        cursor: pointer;
        border-radius: 10px;
    }
    .product-card {
        padding: 10px;
        transition: background-color 0.2s ease;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar filters ---
st.sidebar.header("Filter Products")

# Category Filter
category_filter = st.sidebar.multiselect(
    "Select Category",
    options=df['product_category'].unique(),
    default=df['product_category'].unique()
)

# Price Filter
min_price = int(df['price'].min())
max_price = int(df['price'].max())
price_range = st.sidebar.slider("Select Price Range", min_price, max_price, (min_price, max_price))

# Search Filter
search_term = st.sidebar.text_input("Search by Product Name").lower()

# Filter logic
filtered_df = df[
    (df['product_category'].isin(category_filter)) &
    (df['price'] >= price_range[0]) &
    (df['price'] <= price_range[1]) &
    (df['product_name'].str.lower().str.contains(search_term))
]

# Pagination
ITEMS_PER_PAGE = 10
if 'visible_items' not in st.session_state:
    st.session_state.visible_items = ITEMS_PER_PAGE

visible_df = filtered_df.head(st.session_state.visible_items)

st.subheader(f"Showing {len(visible_df)} of {len(filtered_df)} Products")

# --- Display Product Cards ---
for _, row in visible_df.iterrows():
    product_html = f"""
    <a href="{row['product_url']}" target="_blank" style="text-decoration: none; color: inherit;">
        <div class="product-card">
            <div style="display: flex; gap: 20px; align-items: center;">
                <img src="{row['image_url']}" width="100" style="border-radius: 8px;" />
                <div>
                    <h4 style="margin: 0;">{row['product_name']}</h4>
                    <p style="margin: 0;"><b>Category:</b> {row['product_category']}</p>
                    <p style="margin: 0;"><b>Price:</b> ₹{row['price']}</p>
                    <p style="margin: 0;"><b>Color:</b> {row['color']}</p>
                    <p style="margin: 0;"><b>Description:</b> {row['description']}</p>
                </div>
            </div>
        </div>
    </a>
    <hr>
    """
    st.markdown(product_html, unsafe_allow_html=True)

# --- Load More Button ---
if st.session_state.visible_items < len(filtered_df):
    if st.button("Load More"):
        st.session_state.visible_items += ITEMS_PER_PAGE
