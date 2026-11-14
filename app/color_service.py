"""
VAYELLE — Color Service (Module 1: Color Exploration and Suggestions)
Author: Miftahul Islam Prangon (ID: 24101537)

Provides:
1. Integration with The Color API (https://www.thecolorapi.com/)
2. Graceful offline/timeout fallbacks using mathematical color harmony
3. Color conversions (HEX <-> RGB <-> HSL)
4. Palette scheme generation (Complementary, Analogous, Triadic, Monochromatic, Split-Complementary)
5. Curated shoe color combination suggestions
6. WCAG 2.1 contrast ratio and accessibility compliance analysis (AA / AAA)
"""

import math
import logging
import requests
from typing import Dict, List, Any, Tuple, Optional

logger = logging.getLogger(__name__)

COLOR_API_BASE = "https://www.thecolorapi.com"
API_TIMEOUT = 3.0  # seconds

# Curated, footwear-tailored classic combinations
CURATED_SHOE_SUGGESTIONS = [
    {
        "name": "Onyx & Snow",
        "description": "Timeless, clean contrast ideal for streetwear and court silhouettes.",
        "primary": "#171717",
        "secondary": "#FFFFFF",
        "accent": "#E55B3C",
        "tags": ["Streetwear", "Minimalist", "High Contrast"]
    },
    {
        "name": "Black & Gold",
        "description": "Luxury aesthetic pairing deep matte blacks with radiant warm gold accents.",
        "primary": "#121212",
        "secondary": "#D4AF37",
        "accent": "#F5F5DC",
        "tags": ["Luxury", "Statement", "Retro"]
    },
    {
        "name": "Navy & White",
        "description": "Crisp maritime palette offering balanced elegance for casual and lifestyle sneakers.",
        "primary": "#1D2A44",
        "secondary": "#F8F7F3",
        "accent": "#BFD7E6",
        "tags": ["Casual", "Classic", "Refined"]
    },
    {
        "name": "White & Slate Grey",
        "description": "Modern Scandinavian minimalism with subtle neutral layering.",
        "primary": "#FFFFFF",
        "secondary": "#708090",
        "accent": "#3A3A3A",
        "tags": ["Minimal", "Athletic", "Modern"]
    },
    {
        "name": "Beige & Rich Cocoa",
        "description": "Warm earth tones with a vintage lifestyle warmth.",
        "primary": "#E9E2D4",
        "secondary": "#4A2C1D",
        "accent": "#C9A877",
        "tags": ["Earth", "Casual", "Vintage"]
    },
    {
        "name": "Black & Crimson Red",
        "description": "High-octane energetic contrast celebrating classic basketball silhouettes.",
        "primary": "#171717",
        "secondary": "#C8102E",
        "accent": "#FFFFFF",
        "tags": ["Bold", "Basketball", "Dynamic"]
    },
    {
        "name": "Cream & Olive Drab",
        "description": "Utilitarian military aesthetic with relaxed organic undertones.",
        "primary": "#FAF0E6",
        "secondary": "#6B6B3A",
        "accent": "#9DAE8F",
        "tags": ["Organic", "Outdoor", "Subtle"]
    }
]

# Baseline nearest color names dictionary for offline fallback
COLOR_NAMES_MAP = {
    "#000000": "Black",
    "#FFFFFF": "Pure White",
    "#F8F7F3": "Chalk White",
    "#E9E2D4": "Bone Cream",
    "#3A3A3A": "Graphite Grey",
    "#171717": "Onyx Black",
    "#F36B38": "VAYELLE Orange",
    "#F2B33D": "Saffron Yellow",
    "#B5452B": "Brick Red",
    "#EFB7A8": "Blush Pink",
    "#BFD7E6": "Glacier Blue",
    "#2F55A4": "Cobalt Blue",
    "#1D2A44": "Deep Navy",
    "#A9D8C0": "Spearmint",
    "#6B6B3A": "Olive Green",
    "#C9A877": "Warm Tan",
    "#4A2C1D": "Cocoa Brown",
    "#9DAE8F": "Sage Green",
    "#D7F23D": "Volt Lime",
    "#C8102E": "Cherry Crimson",
    "#5B3FD9": "Ultra Violet",
    "#0E8C8C": "Deep Teal",
    "#D4AF37": "Metallic Gold",
    "#708090": "Slate Grey",
    "#E55B3C": "Flame Orange"
}


def sanitize_hex(hex_code: str) -> str:
    """Cleans and standardizes hex color input to uppercase 6-character hex without '#'."""
    clean = hex_code.strip().lstrip('#').upper()
    if len(clean) == 3:
        clean = ''.join([c * 2 for c in clean])
    if len(clean) != 6 or not all(c in '0123456789ABCDEF' for c in clean):
        return "F36B38"  # Default fallback to VAYELLE Orange
    return clean


def hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
    """Converts a hex color string to (r, g, b) tuple."""
    clean = sanitize_hex(hex_code)
    return int(clean[0:2], 16), int(clean[2:4], 16), int(clean[4:6], 16)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Converts (r, g, b) values to 6-digit hex format with '#'."""
    r_c = max(0, min(255, int(round(r))))
    g_c = max(0, min(255, int(round(g))))
    b_c = max(0, min(255, int(round(b))))
    return f"#{r_c:02X}{g_c:02X}{b_c:02X}"


def rgb_to_hsl(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Converts (r, g, b) [0..255] to (h, s, l) where h in [0..360], s in [0..100], l in [0..100]."""
    r_n, g_n, b_n = r / 255.0, g / 255.0, b / 255.0
    c_max = max(r_n, g_n, b_n)
    c_min = min(r_n, g_n, b_n)
    delta = c_max - c_min
    l = (c_max + c_min) / 2.0

    if delta == 0:
        h = 0.0
        s = 0.0
    else:
        s = delta / (2.0 - c_max - c_min) if l > 0.5 else delta / (c_max + c_min)
        if c_max == r_n:
            h = ((g_n - b_n) / delta + (6.0 if g_n < b_n else 0.0)) / 6.0
        elif c_max == g_n:
            h = ((b_n - r_n) / delta + 2.0) / 6.0
        else:
            h = ((r_n - g_n) / delta + 4.0) / 6.0
        h *= 360.0

    return round(h, 1), round(s * 100.0, 1), round(l * 100.0, 1)


def hsl_to_rgb(h: float, s: float, l: float) -> Tuple[int, int, int]:
    """Converts (h [0..360], s [0..100], l [0..100]) to (r, g, b) [0..255]."""
    h_n = (h % 360.0) / 360.0
    s_n = max(0.0, min(100.0, s)) / 100.0
    l_n = max(0.0, min(100.0, l)) / 100.0

    if s_n == 0:
        val = int(round(l_n * 255.0))
        return val, val, val

    def hue_to_rgb(p: float, q: float, t: float) -> float:
        if t < 0:
            t += 1.0
        if t > 1:
            t -= 1.0
        if t < 1.0 / 6.0:
            return p + (q - p) * 6.0 * t
        if t < 1.0 / 2.0:
            return q
        if t < 2.0 / 3.0:
            return p + (q - p) * (2.0 / 3.0 - t) * 6.0
        return p

    q = l_n * (1.0 + s_n) if l_n < 0.5 else l_n + s_n - l_n * s_n
    p = 2.0 * l_n - q

    r = hue_to_rgb(p, q, h_n + 1.0 / 3.0)
    g = hue_to_rgb(p, q, h_n)
    b = hue_to_rgb(p, q, h_n - 1.0 / 3.0)

    return int(round(r * 255.0)), int(round(g * 255.0)), int(round(b * 255.0))


def get_offline_color_name(hex_code: str) -> str:
    """Finds exact or closest descriptive color name from known map."""
    clean = f"#{sanitize_hex(hex_code)}"
    if clean in COLOR_NAMES_MAP:
        return COLOR_NAMES_MAP[clean]

    target_r, target_g, target_b = hex_to_rgb(clean)
    best_name = "Custom Color"
    min_dist = float('inf')

    for hex_key, name in COLOR_NAMES_MAP.items():
        r, g, b = hex_to_rgb(hex_key)
        dist = (r - target_r) ** 2 + (g - target_g) ** 2 + (b - target_b) ** 2
        if dist < min_dist:
            min_dist = dist
            best_name = f"Near {name}"

    return best_name


def get_color_info(hex_code: str) -> Dict[str, Any]:
    """
    Retrieves complete color details from The Color API,
    with seamless mathematical fallback if the API is offline.
    """
    clean_hex = sanitize_hex(hex_code)
    r, g, b = hex_to_rgb(clean_hex)
    h, s, l = rgb_to_hsl(r, g, b)
    hex_with_hash = f"#{clean_hex}"

    # Default fallback data
    fallback_data = {
        "hex": hex_with_hash,
        "clean_hex": clean_hex,
        "name": get_offline_color_name(clean_hex),
        "rgb": {"r": r, "g": g, "b": b, "value": f"rgb({r}, {g}, {b})"},
        "hsl": {"h": h, "s": s, "l": l, "value": f"hsl({h}, {s}%, {l}%)"},
        "hsv": {"value": f"hsv({h}, {s}%, {round(max(r, g, b) / 2.55, 1)}%)"},
        "cmyk": {"value": f"cmyk({round((1 - r/255)*100)}%, {round((1 - g/255)*100)}%, {round((1 - b/255)*100)}%, 0%)"},
        "is_light": (0.299 * r + 0.587 * g + 0.114 * b) > 128,
        "text_contrast": "#000000" if (0.299 * r + 0.587 * g + 0.114 * b) > 128 else "#FFFFFF",
        "api_image": f"{COLOR_API_BASE}/id?format=svg&named=false&hex={clean_hex}",
        "closest_named_hex": hex_with_hash,
        "exact_match_name": True,
        "source": "fallback"
    }

    try:
        url = f"{COLOR_API_BASE}/id?hex={clean_hex}"
        resp = requests.get(url, timeout=API_TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "hex": data.get("hex", {}).get("value", hex_with_hash),
                "clean_hex": clean_hex,
                "name": data.get("name", {}).get("value", fallback_data["name"]),
                "closest_named_hex": data.get("name", {}).get("closest_named_hex", hex_with_hash),
                "exact_match_name": data.get("name", {}).get("exact_match_name", False),
                "rgb": {
                    "r": data.get("rgb", {}).get("r", r),
                    "g": data.get("rgb", {}).get("g", g),
                    "b": data.get("rgb", {}).get("b", b),
                    "value": data.get("rgb", {}).get("value", f"rgb({r}, {g}, {b})")
                },
                "hsl": {
                    "h": data.get("hsl", {}).get("h", h),
                    "s": data.get("hsl", {}).get("s", s),
                    "l": data.get("hsl", {}).get("l", l),
                    "value": data.get("hsl", {}).get("value", f"hsl({h}, {s}%, {l}%)")
                },
                "hsv": {
                    "value": data.get("hsv", {}).get("value", fallback_data["hsv"]["value"])
                },
                "cmyk": {
                    "value": data.get("cmyk", {}).get("value", fallback_data["cmyk"]["value"])
                },
                "XYZ": {
                    "value": data.get("XYZ", {}).get("value", "")
                },
                "api_image": data.get("image", {}).get("named", f"{COLOR_API_BASE}/id?format=svg&named=false&hex={clean_hex}"),
                "is_light": (0.299 * r + 0.587 * g + 0.114 * b) > 128,
                "text_contrast": data.get("contrast", {}).get("value", fallback_data["text_contrast"]),
                "source": "api"
            }
    except Exception as e:
        logger.warning(f"The Color API query failed ({e}); using mathematical fallback.")

    return fallback_data


def generate_local_scheme(hex_code: str, mode: str, count: int = 5) -> List[Dict[str, Any]]:
    """
    Generates color schemes locally using standard color harmony formulas.
    Modes: complementary, analogous, triadic, monochrome, split-complementary.
    """
    clean_hex = sanitize_hex(hex_code)
    r, g, b = hex_to_rgb(clean_hex)
    h, s, l = rgb_to_hsl(r, g, b)

    hues_and_variations: List[Tuple[float, float, float]] = []

    mode_norm = mode.lower().replace('-', '').replace('_', '')

    if 'comp' in mode_norm and 'split' not in mode_norm:
        # Base + complementary + slight luminance shades
        comp_h = (h + 180.0) % 360.0
        hues_and_variations = [
            (h, s, max(15.0, l - 15.0)),
            (h, s, l),
            (comp_h, s, l),
            (comp_h, max(10.0, s - 20.0), min(85.0, l + 15.0)),
            (comp_h, s, max(15.0, l - 20.0))
        ]
    elif 'analog' in mode_norm:
        # H - 40, H - 20, H, H + 20, H + 40
        hues_and_variations = [
            ((h - 40.0) % 360.0, s, l),
            ((h - 20.0) % 360.0, s, l),
            (h, s, l),
            ((h + 20.0) % 360.0, s, l),
            ((h + 40.0) % 360.0, s, l)
        ]
    elif 'triad' in mode_norm:
        # H, H + 120, H + 240 plus balanced lightness shifts
        t1 = (h + 120.0) % 360.0
        t2 = (h + 240.0) % 360.0
        hues_and_variations = [
            (h, s, l),
            (t1, s, l),
            (t2, s, l),
            (t1, max(15.0, s - 20.0), min(85.0, l + 15.0)),
            (t2, s, max(15.0, l - 20.0))
        ]
    elif 'split' in mode_norm:
        # Base + 150 deg + 210 deg
        s1 = (h + 150.0) % 360.0
        s2 = (h + 210.0) % 360.0
        hues_and_variations = [
            (h, s, max(15.0, l - 15.0)),
            (h, s, l),
            (s1, s, l),
            (s2, s, l),
            (s1, max(10.0, s - 15.0), min(85.0, l + 15.0))
        ]
    else:  # monochrome
        # Vary lightness and subtle saturation shifts
        hues_and_variations = [
            (h, s, 20.0),
            (h, max(10.0, s - 10.0), 38.0),
            (h, s, l),
            (h, max(15.0, s - 5.0), 65.0),
            (h, max(5.0, s - 20.0), 85.0)
        ]

    # Trim or expand to count
    hues_and_variations = hues_and_variations[:count]

    results = []
    for cur_h, cur_s, cur_l in hues_and_variations:
        cur_r, cur_g, cur_b = hsl_to_rgb(cur_h, cur_s, cur_l)
        hex_str = rgb_to_hex(cur_r, cur_g, cur_b)
        results.append({
            "hex": hex_str,
            "name": get_offline_color_name(hex_str),
            "rgb": {"r": cur_r, "g": cur_g, "b": cur_b, "value": f"rgb({cur_r}, {cur_g}, {cur_b})"},
            "hsl": {"h": round(cur_h, 1), "s": round(cur_s, 1), "l": round(cur_l, 1), "value": f"hsl({round(cur_h, 1)}, {round(cur_s, 1)}%, {round(cur_l, 1)}%)"},
            "text_contrast": "#000000" if (0.299 * cur_r + 0.587 * cur_g + 0.114 * cur_b) > 128 else "#FFFFFF"
        })

    return results


def get_color_scheme(hex_code: str, mode: str = "complement", count: int = 5) -> Dict[str, Any]:
    """
    Retrieves palette scheme from The Color API,
    or falls back to local color harmony generator.
    Supported modes: complement, analogic, triad, monochrome, split-complementary
    """
    clean_hex = sanitize_hex(hex_code)
    api_mode = mode.lower()
    
    # Map friendly names to The Color API mode names
    mode_map = {
        "complementary": "complement",
        "complement": "complement",
        "analogous": "analogic",
        "analogic": "analogic",
        "triadic": "triad",
        "triad": "triad",
        "monochromatic": "monochrome",
        "monochrome": "monochrome",
        "split-complementary": "analogic-complement",
        "split": "analogic-complement",
        "quad": "quad",
        "tetradic": "quad"
    }
    api_mode = mode_map.get(api_mode, "complement")

    try:
        url = f"{COLOR_API_BASE}/scheme?hex={clean_hex}&mode={api_mode}&count={count}"
        resp = requests.get(url, timeout=API_TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            colors_list = []
            for item in data.get("colors", []):
                val_hex = item.get("hex", {}).get("value", "")
                colors_list.append({
                    "hex": val_hex,
                    "name": item.get("name", {}).get("value", get_offline_color_name(val_hex)),
                    "rgb": item.get("rgb", {}),
                    "hsl": item.get("hsl", {}),
                    "hsv": item.get("hsv", {}),
                    "cmyk": item.get("cmyk", {}),
                    "api_image": item.get("image", {}).get("named", f"{COLOR_API_BASE}/id?format=svg&named=false&hex={val_hex.replace('#','') }"),
                    "text_contrast": item.get("contrast", {}).get("value", "#000000")
                })
            if colors_list:
                return {
                    "mode": mode,
                    "base_hex": f"#{clean_hex}",
                    "colors": colors_list,
                    "scheme_image": data.get("image", {}).get("bare", f"{COLOR_API_BASE}/scheme?format=svg&hex={clean_hex}&mode={api_mode}&count={count}"),
                    "source": "api"
                }
    except Exception as e:
        logger.warning(f"The Color API scheme failed ({e}); falling back to local math generator.")

    # Local fallback
    fallback_colors = generate_local_scheme(clean_hex, mode, count)
    return {
        "mode": mode,
        "base_hex": f"#{clean_hex}",
        "colors": fallback_colors,
        "source": "fallback"
    }


def calculate_relative_luminance(r: int, g: int, b: int) -> float:
    """
    Calculates WCAG 2.1 relative luminance for an sRGB color.
    Formula: L = 0.2126 * R + 0.7152 * G + 0.0722 * B
    where each component is linearized.
    """
    def linearize(c: int) -> float:
        c_norm = c / 255.0
        if c_norm <= 0.04045:
            return c_norm / 12.92
        return ((c_norm + 0.055) / 1.055) ** 2.4

    r_lin = linearize(r)
    g_lin = linearize(g)
    b_lin = linearize(b)

    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def calculate_contrast_ratio(hex1: str, hex2: str) -> Dict[str, Any]:
    """
    Calculates the exact WCAG 2.1 contrast ratio between two hex colors,
    and returns AA and AAA pass/fail accessibility compliance.
    """
    r1, g1, b1 = hex_to_rgb(hex1)
    r2, g2, b2 = hex_to_rgb(hex2)

    lum1 = calculate_relative_luminance(r1, g1, b1)
    lum2 = calculate_relative_luminance(r2, g2, b2)

    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)

    ratio = (lighter + 0.05) / (darker + 0.05)
    ratio_rounded = round(ratio, 2)

    # WCAG 2.1 thresholds
    # Normal text: AA >= 4.5, AAA >= 7.0
    # Large text & UI components: AA >= 3.0, AAA >= 4.5
    wcag_aa_normal = ratio >= 4.5
    wcag_aa_large = ratio >= 3.0
    wcag_aaa_normal = ratio >= 7.0
    wcag_aaa_large = ratio >= 4.5

    rating = "Poor"
    if ratio >= 7.0:
        rating = "Excellent (AAA)"
    elif ratio >= 4.5:
        rating = "Good (AA)"
    elif ratio >= 3.0:
        rating = "Fair (Large Text Only)"

    return {
        "color1": f"#{sanitize_hex(hex1)}",
        "color2": f"#{sanitize_hex(hex2)}",
        "ratio": ratio_rounded,
        "ratio_display": f"{ratio_rounded}:1",
        "rating": rating,
        "wcag_aa": {
            "normal_text": wcag_aa_normal,
            "large_text": wcag_aa_large,
            "ui_components": wcag_aa_large
        },
        "wcag_aaa": {
            "normal_text": wcag_aaa_normal,
            "large_text": wcag_aaa_large
        }
    }


def get_curated_shoe_combinations() -> List[Dict[str, Any]]:
    """Returns the list of curated footwear-specific color combinations."""
    return CURATED_SHOE_SUGGESTIONS
