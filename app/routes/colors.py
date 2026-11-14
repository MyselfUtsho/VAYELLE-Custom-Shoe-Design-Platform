"""
VAYELLE — Color Blueprint (Module 1: Color Exploration and Suggestions)
Author: Miftahul Islam Prangon (ID: 24101537)

Routes:
- /choose-design : Step 2 design choice gateway (Option A: Explore Designs vs Option B: Create Your Color)
- /colors        : Color Studio interface (Color Picker, Palette Generator, Shoe Suggestions, Contrast Checker)
- /customize-shoe: Transition screen with dummy shoe on left and active color palette on right
- /api/color/*   : JSON endpoints for Color API info, schemes, and WCAG contrast calculations
"""

from flask import Blueprint, render_template, request, jsonify, session
from app.auth_utils import get_current_user
from app.color_service import (
    get_color_info,
    get_color_scheme,
    calculate_contrast_ratio,
    get_curated_shoe_combinations,
    sanitize_hex
)

colors_bp = Blueprint('colors', __name__)


@colors_bp.route('/choose-design')
def choose_design():
    """
    Step 1 & 2: Choose Your Design Gateway.
    Presents two distinct options:
    - Option A: Explore Designs (Athoy Roy's Category Catalog)
    - Option B: Create Your Color (Miftahul Islam Prangon's Color Studio)
    """
    user = get_current_user()
    return render_template('choose_design.html', user=user)


@colors_bp.route('/colors')
def color_studio():
    """
    Step 3: Color Studio Interface.
    Full-featured color exploration, Color API palette generator,
    footwear-tailored color suggestions, and WCAG contrast analysis.
    """
    user = get_current_user()
    initial_hex = request.args.get('hex', 'F36B38').strip()
    shoe_name = request.args.get('shoe_name', 'Urban Runner').strip()
    shoe_id = request.args.get('shoe_id', 'urban-runner').strip()

    curated_combinations = get_curated_shoe_combinations()
    initial_color_info = get_color_info(initial_hex)

    return render_template(
        'colors.html',
        user=user,
        initial_color=initial_color_info,
        curated_combinations=curated_combinations,
        shoe_name=shoe_name,
        shoe_id=shoe_id
    )


@colors_bp.route('/customize-shoe')
def customize_shoe():
    """
    Step 4: Connect to Shoe Customization Workflow.
    Displays a dummy shoe on the left and the user's selected/created
    color palette on the right, primed for Module 2 canvas customization.
    """
    user = get_current_user()
    
    # Retrieve palette passed via query param or session
    palette_raw = request.args.get('palette', '')
    shoe_name = request.args.get('shoe_name', 'VAYELLE Silhouette').strip()
    
    palette_colors = []
    if palette_raw:
        for hex_code in palette_raw.split(','):
            h_clean = sanitize_hex(hex_code)
            palette_colors.append(get_color_info(h_clean))
    
    if not palette_colors and 'active_palette' in session:
        palette_colors = session.get('active_palette', [])

    # If still empty, provide default VAYELLE shoe palette
    if not palette_colors:
        for h_code in ['F36B38', '171717', 'F8F7F3', 'E9E2D4', '2F55A4']:
            palette_colors.append(get_color_info(h_code))

    return render_template(
        'customize_shoe.html',
        user=user,
        shoe_name=shoe_name,
        palette_colors=palette_colors
    )


# --- JSON API Endpoints ---

@colors_bp.route('/api/color/info')
def api_color_info():
    """Returns color details, RGB, HSL, and text contrast for a hex code."""
    hex_code = request.args.get('hex', 'F36B38')
    info = get_color_info(hex_code)
    return jsonify({"success": True, "data": info})


@colors_bp.route('/api/color/scheme')
def api_color_scheme():
    """Generates color schemes via Color API with local mathematical fallback."""
    hex_code = request.args.get('hex', 'F36B38')
    mode = request.args.get('mode', 'complementary')
    count = int(request.args.get('count', 5))
    scheme = get_color_scheme(hex_code, mode=mode, count=count)
    return jsonify({"success": True, "data": scheme})


@colors_bp.route('/api/color/contrast')
def api_color_contrast():
    """Calculates WCAG 2.1 contrast ratio and AA/AAA compliance between two colors."""
    c1 = request.args.get('c1', '171717')
    c2 = request.args.get('c2', 'F8F7F3')
    result = calculate_contrast_ratio(c1, c2)
    return jsonify({"success": True, "data": result})


@colors_bp.route('/api/color/save-session', methods=['POST'])
def api_save_session_palette():
    """Saves the user's active palette in Flask session."""
    data = request.get_json(silent=True) or {}
    palette = data.get('palette', [])
    if isinstance(palette, list) and len(palette) > 0:
        cleaned_palette = [get_color_info(h) for h in palette[:10]]
        session['active_palette'] = cleaned_palette
        return jsonify({"success": True, "count": len(cleaned_palette)})
    return jsonify({"success": False, "message": "Invalid palette data"}), 400
