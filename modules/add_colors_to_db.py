import mysql.connector
import requests
from io import BytesIO
from colorthief import ColorThief
import traceback

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

cursor.execute("SELECT id, image_url FROM products;")
products = cursor.fetchall()
print(f"✅ Found {len(products)} products.")


def get_dominant_colors(image_url, num_colors=3):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            img = BytesIO(response.content)
            color_thief = ColorThief(img)
            palette = color_thief.get_palette(color_count=num_colors)
            hex_colors = ['#%02x%02x%02x' % color for color in palette]
            return hex_colors
        else:
            print(f"❌ Failed to fetch image: {image_url} | Status Code: {response.status_code}")
            return [None] * num_colors
    except Exception as e:
        print(f"❌ Error fetching {image_url}: {e}")
        return [None] * num_colors


for prod in products:
    prod_id, image_url = prod
    print(f"\n🔄 Processing Product ID {prod_id}")

    if not image_url or not image_url.startswith("http"):
        print(f"⚠️ Invalid image URL for product {prod_id}: {image_url}")
        continue

    colors = get_dominant_colors(image_url)
    if colors and None not in colors:
        print(f"🎨 Extracted Colors: {colors}")
        try:
            sql = "UPDATE products SET color1=%s, color2=%s, color3=%s WHERE id=%s"
            cursor.execute(sql, (colors[0], colors[1], colors[2], prod_id))
            print(f"✅ Updated product {prod_id} successfully.")
        except Exception as e:
            print(f"❌ Error updating product {prod_id}:", e)
    else:
        print(f"⚠️ Skipped product {prod_id} due to missing or invalid colors.")

try:
    db.commit()
    print("💾 All changes committed to database.")
except Exception as e:
    print("❌ Commit failed:", e)

cursor.close()
db.close()
print("✅ Script completed.")
