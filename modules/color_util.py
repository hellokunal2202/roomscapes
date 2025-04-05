import colorsys

def hex_to_rgb(hex_code):
# converting hex color code to RGB tuple
    hex_code = hex_code.lstrip('#')
    if len(hex_code) == 3:
        hex_code = ''.join([c*2 for c in hex_code])
    if len(hex_code) != 6:
        raise ValueError(f"Invalid hex code: {hex_code}")
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def categorize_color_family(hex_code):
    """Categorizing color based on HLS values."""
    r, g, b = hex_to_rgb(hex_code)
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    hue_deg = h * 360

    # Threshold constants
    VERY_LOW_SAT = 0.1   # Achromatic threshold
    LOW_SAT = 0.25       # Desaturated/pastel threshold
    MED_SAT = 0.5        # Medium saturation
    VERY_HIGH_LIGHT = 0.9  # Near-white
    HIGH_LIGHT = 0.75    # Light shades
    LOW_LIGHT = 0.25     # Dark shades
    VERY_LOW_LIGHT = 0.15  # Near-black

    # Achromatic colors
    if s < VERY_LOW_SAT:
        if l < VERY_LOW_LIGHT: return "Black"
        if l > VERY_HIGH_LIGHT: return "White"
        return "Gray"

    # Desaturated and pastel colors
    if s < LOW_SAT:
        if l > HIGH_LIGHT:
            if 0 <= hue_deg < 15 or 345 <= hue_deg < 360: return "Light Pink"
            if 15 <= hue_deg < 45: return "Peach"
            if 45 <= hue_deg < 70: return "Cream"
            if 70 <= hue_deg < 150: return "Mint"
            if 150 <= hue_deg < 190: return "Pale Aqua"
            if 190 <= hue_deg < 255: return "Sky Blue"
            if 255 <= hue_deg < 285: return "Lavender"
            if 285 <= hue_deg < 345: return "Dusty Pink"
        elif LOW_LIGHT < l < HIGH_LIGHT:
            if 15 <= hue_deg < 45: return "Beige"
            if 45 <= hue_deg < 70: return "Taupe"
            if 70 <= hue_deg < 100: return "Olive Drab"
            if 190 <= hue_deg < 255: return "Slate"
            if 255 <= hue_deg < 285: return "Mauve"

    # Medium saturation colors
    if s < MED_SAT:
        if l > HIGH_LIGHT:
            if 15 <= hue_deg < 45: return "Apricot"
            if 70 <= hue_deg < 150: return "Celadon"
            if 150 <= hue_deg < 190: return "Turquoise"
        elif l < LOW_LIGHT:
            if 70 <= hue_deg < 150: return "Dark Olive"
            if 190 <= hue_deg < 255: return "Steel Blue"

    # Chromatic colors with light/dark/vivid variants
    if hue_deg < 15 or hue_deg >= 345:
        if l < LOW_LIGHT: return "Maroon"
        if l > HIGH_LIGHT: return "Blush"
        return "Red" if s > MED_SAT else "Rose"
    elif 15 <= hue_deg < 40:
        if l < LOW_LIGHT: return "Rust"
        if l > HIGH_LIGHT: return "Coral"
        return "Orange" if s > MED_SAT else "Terracotta"
    elif 40 <= hue_deg < 70:
        if l < LOW_LIGHT: return "Bronze"
        if l > HIGH_LIGHT and s > MED_SAT: return "Yellow"
        if l > HIGH_LIGHT: return "Cream"
        return "Gold" if s > 0.6 else "Khaki"
    elif 70 <= hue_deg < 100:
        if l < LOW_LIGHT: return "Dark Green"
        if l > HIGH_LIGHT: return "Mint"
        return "Olive" if s < 0.6 else "Lime"
    elif 100 <= hue_deg < 150:
        if l < LOW_LIGHT: return "Forest Green"
        if l > HIGH_LIGHT: return "Celadon"
        return "Green" if s > MED_SAT else "Sage"
    elif 150 <= hue_deg < 190:
        if l < LOW_LIGHT: return "Teal"
        if l > HIGH_LIGHT: return "Aqua"
        return "Cyan" if s > MED_SAT else "Turquoise"
    elif 190 <= hue_deg < 240:
        if l < LOW_LIGHT: return "Navy"
        if l > HIGH_LIGHT: return "Sky Blue"
        return "Blue" if s > MED_SAT else "Denim"
    elif 240 <= hue_deg < 285:
        if l < LOW_LIGHT: return "Indigo"
        if l > HIGH_LIGHT: return "Lavender"
        return "Purple" if s > MED_SAT else "Mauve"
    elif 285 <= hue_deg < 345:
        if l < LOW_LIGHT: return "Burgundy"
        if l > HIGH_LIGHT: return "Pink"
        return "Magenta" if s > MED_SAT else "Dusty Rose"

    return "Other"  # Fallback (minimized with broader categories)

def group_colors_by_family(color_list):
    families = {}
    for color in color_list:
        try:
            family = categorize_color_family(color)
        except Exception as e:
            family = f"Invalid: {str(e)}"
        families.setdefault(family, []).append(color)
    return families

# Example usage
# if __name__ == "__main__":
#     sample_colors = [
#         "#a9978e", "#211e18" , "#5a3f2c" , "#75502f"
#     ]
    
#     grouped = group_colors_by_family(sample_colors)
    
#     print("Color Family Analysis:")
#     for family in sorted(grouped.keys()):
#         print(f"\n{family} ({len(grouped[family])}):")
#         print('\n'.join(f"  {c}" for c in grouped[family]))


# for user_preference.py
def extract_category_colors(df):
    cat_colors = {}
    grouped = df.groupby('product_category')['color'].agg(lambda x: sorted(list(x.dropna().unique()))).to_dict()
    for category, colors in grouped.items():
        cleaned = [str(c).strip() for c in colors if str(c).strip()]
        if cleaned:
            cat_colors[category] = cleaned
    return cat_colors