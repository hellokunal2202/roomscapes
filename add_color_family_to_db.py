import mysql.connector
import traceback
from modules.color_util import categorize_color_family  # Importing from your separate file

# ---------- Step 1: Connect to DB ----------
print("🔄 Connecting to MySQL database...")

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Pujan@111",
        database="product_db"
    )
    print("✅ Connected to MySQL successfully!")
except Exception as e:
    print("❌ Could not connect to MySQL:", e)
    traceback.print_exc()
    exit()

cursor = db.cursor()

# ---------- Step 2: Get Products with Hex Colors ----------
cursor.execute("SELECT id, color FROM products;")  # Fetch id and color (hex) instead of image_url
products = cursor.fetchall()
print(f"✅ Found {len(products)} products.")

# ---------- Step 3: Process Products ----------
for prod in products:
    prod_id, hex_color = prod
    print(f"\n🔄 Processing Product ID {prod_id}")

    if not hex_color or not hex_color.startswith("#"):
        print(f"⚠️ Invalid hex color for product {prod_id}: {hex_color}")
        continue

    try:
        color_name = categorize_color_family(hex_color)  # Convert hex to color family name
        print(f"🎨 Hex Color: {hex_color} -> {color_name}")
        sql = "UPDATE products SET color=%s WHERE id=%s"
        cursor.execute(sql, (color_name, prod_id))
        print(f"✅ Updated product {prod_id} with color: {color_name}")
    except Exception as e:
        print(f"❌ Error updating product {prod_id}:", e)

# ---------- Step 4: Commit and Close ----------
try:
    db.commit()
    print("💾 All changes committed to database.")
except Exception as e:
    print("❌ Commit failed:", e)

cursor.close()
db.close()
print("✅ Script completed.")