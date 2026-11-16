"""
VAYELLE — Module 1 Automated Test Suite: Color Exploration and Suggestions
Author: Miftahul Islam Prangon (ID: 24101537)

Tests:
1. Hex sanitization and color conversions (HEX <-> RGB <-> HSL)
2. Color scheme generation (Complementary, Analogous, Triadic, Monochromatic, Split-Complementary)
3. Color API service offline/timeout fallback mechanism
4. WCAG 2.1 relative luminance and contrast ratio calculations
5. Curated shoe color combinations
6. Route /choose-design loads with Option A and Option B
7. Route /colors loads Color Studio interface
8. Route /customize-shoe renders dummy shoe and active color palette
9. JSON API endpoint /api/color/info
10. JSON API endpoint /api/color/scheme
11. JSON API endpoint /api/color/contrast
12. Session persistence endpoint /api/color/save-session
"""

import unittest
from app import create_app
import mongomock
import app.db as app_db
from app.color_service import (
    sanitize_hex,
    hex_to_rgb,
    rgb_to_hex,
    rgb_to_hsl,
    hsl_to_rgb,
    get_color_info,
    get_color_scheme,
    calculate_contrast_ratio,
    calculate_relative_luminance,
    get_curated_shoe_combinations,
    generate_local_scheme
)


class TestColorExplorationAndSuggestions(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.client = self.app.test_client()

        # Mock DB
        self.mock_client = mongomock.MongoClient()
        self.mock_db = self.mock_client['vayelle_db']
        app_db._client = self.mock_client
        app_db._db = self.mock_db

    # --- Unit Tests: Color Service & Calculations ---

    def test_01_sanitize_hex(self):
        """Verify hex sanitization for valid, short, and malformed hex strings."""
        self.assertEqual(sanitize_hex("#f36b38"), "F36B38")
        self.assertEqual(sanitize_hex("000"), "000000")
        self.assertEqual(sanitize_hex("#FFF"), "FFFFFF")
        self.assertEqual(sanitize_hex("xyz123"), "F36B38")  # default fallback

    def test_02_conversions(self):
        """Verify bidirectional RGB and HSL conversions."""
        r, g, b = hex_to_rgb("#F36B38")
        self.assertEqual((r, g, b), (243, 107, 56))
        self.assertEqual(rgb_to_hex(r, g, b), "#F36B38")

        h, s, l = rgb_to_hsl(r, g, b)
        self.assertAlmostEqual(h, 16.4, delta=1.5)
        self.assertAlmostEqual(s, 89.0, delta=2.0)
        self.assertAlmostEqual(l, 58.6, delta=2.0)

        r_back, g_back, b_back = hsl_to_rgb(h, s, l)
        self.assertAlmostEqual(r, r_back, delta=2)
        self.assertAlmostEqual(g, g_back, delta=2)
        self.assertAlmostEqual(b, b_back, delta=2)

    def test_03_scheme_generation_modes(self):
        """Verify all 5 scheme modes produce valid 5-color palettes."""
        modes = ['complementary', 'analogous', 'triadic', 'monochromatic', 'split-complementary']
        for mode in modes:
            scheme = get_color_scheme('F36B38', mode=mode, count=5)
            self.assertIn('colors', scheme)
            self.assertEqual(len(scheme['colors']), 5, f"Mode {mode} should return 5 colors")
            for c in scheme['colors']:
                self.assertTrue(c['hex'].startswith('#'))
                self.assertIn('rgb', c)
                self.assertIn('name', c)

    def test_04_wcag_contrast_black_and_white(self):
        """Verify WCAG contrast ratio for pure black and white evaluates to 21:1."""
        res = calculate_contrast_ratio("#000000", "#FFFFFF")
        self.assertEqual(res['ratio'], 21.0)
        self.assertTrue(res['wcag_aa']['normal_text'])
        self.assertTrue(res['wcag_aaa']['normal_text'])
        self.assertIn("AAA", res['rating'])

    def test_05_wcag_contrast_low_contrast(self):
        """Verify low contrast colors fail AA and AAA normal text standards."""
        res = calculate_contrast_ratio("#FFFFFF", "#F8F7F3")
        self.assertLess(res['ratio'], 3.0)
        self.assertFalse(res['wcag_aa']['normal_text'])
        self.assertFalse(res['wcag_aaa']['normal_text'])

    def test_06_curated_shoe_combinations(self):
        """Verify curated shoe color combinations are available with descriptions and tags."""
        combos = get_curated_shoe_combinations()
        self.assertGreaterEqual(len(combos), 7)
        first = combos[0]
        self.assertIn('name', first)
        self.assertIn('primary', first)
        self.assertIn('secondary', first)
        self.assertIn('tags', first)

    # --- Route Integration Tests ---

    def test_07_choose_design_route(self):
        """Verify /choose-design loads with HTTP 200 and contains both Option A and Option B."""
        response = self.client.get('/choose-design')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("Choose Your Design", html)
        self.assertIn("Option A", html)
        self.assertIn("Explore Designs", html)
        self.assertIn("Option B", html)
        self.assertIn("Create Your Color", html)

    def test_08_colors_studio_route(self):
        """Verify /colors route loads with HTTP 200 and all studio components."""
        response = self.client.get('/colors?hex=F36B38&shoe_name=Urban+Runner')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("Color Exploration", html)
        self.assertIn("Color Palette Generator", html)
        self.assertIn("Curated Shoe Color Suggestions", html)
        self.assertIn("Contrast Checker", html)
        self.assertIn("Continue to Customize Your Shoe", html)

    def test_09_customize_shoe_route(self):
        """Verify /customize-shoe renders dummy shoe screen and selected color palette."""
        response = self.client.get('/customize-shoe?palette=%23F36B38,%23171717,%23FFFFFF&shoe_name=Urban+Runner')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("Customization Preview", html)
        self.assertIn("Your Selected Colors", html)
        self.assertIn("Base Silhouette: Urban Runner", html)
        self.assertIn("Interactive 2D Canvas (Module 2)", html)

    # --- API JSON Endpoints ---

    def test_10_api_color_info(self):
        """Verify /api/color/info returns valid JSON color metadata."""
        response = self.client.get('/api/color/info?hex=F36B38')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['clean_hex'], 'F36B38')
        self.assertIn('rgb', data['data'])
        self.assertIn('name', data['data'])

    def test_11_api_color_scheme(self):
        """Verify /api/color/scheme returns valid palette list."""
        response = self.client.get('/api/color/scheme?hex=F36B38&mode=triadic&count=5')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']['colors']), 5)

    def test_12_api_color_contrast(self):
        """Verify /api/color/contrast returns WCAG contrast calculation."""
        response = self.client.get('/api/color/contrast?c1=171717&c2=F8F7F3')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('ratio', data['data'])
        self.assertIn('wcag_aa', data['data'])

    def test_13_api_save_session_palette(self):
        """Verify /api/color/save-session saves palette into session."""
        response = self.client.post(
            '/api/color/save-session',
            json={"palette": ["#F36B38", "#171717", "#FFFFFF"]}
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 3)

    def test_14_mock_db_palette_persistence_and_retrieval(self):
        """Verify palette persistence in MongoDB collection using mongomock."""
        import mongomock
        from unittest.mock import patch

        mock_db = mongomock.MongoClient()['vayelle_db']
        mock_palettes = mock_db['palettes']

        with patch('app.routes.colors.check_db_connection', return_value=(True, 'Connected')):
            with patch('app.routes.colors.get_palettes_collection', return_value=mock_palettes):
                # Save palette
                save_resp = self.client.post(
                    '/api/color/save-session',
                    json={
                        "palette": ["#F36B38", "#171717", "#F8F7F3"],
                        "name": "Urban Runner Palette",
                        "harmony_type": "triad",
                        "shoe_name": "Urban Runner"
                    }
                )
                self.assertEqual(save_resp.status_code, 200)
                save_data = save_resp.get_json()
                self.assertTrue(save_data['success'])
                self.assertTrue(save_data['persisted'])
                self.assertIsNotNone(save_data['palette_id'])

                # Verify saved in mock collection
                doc = mock_palettes.find_one({"name": "Urban Runner Palette"})
                self.assertIsNotNone(doc)
                self.assertIn("#F36B38", doc['colors'])
                self.assertEqual(doc['shoe_name'], "Urban Runner")

                # Retrieve via API
                get_resp = self.client.get('/api/color/palettes')
                self.assertEqual(get_resp.status_code, 200)
                get_data = get_resp.get_json()
                self.assertTrue(get_data['success'])
                self.assertGreaterEqual(get_data['count'], 1)
                self.assertEqual(get_data['palettes'][0]['name'], "Urban Runner Palette")

    def test_15_palette_saving_invalid_input(self):
        """Verify invalid palette payloads are rejected safely."""
        resp = self.client.post('/api/color/save-session', json={"palette": []})
        self.assertEqual(resp.status_code, 400)
        resp2 = self.client.post('/api/color/save-session', json={})
        self.assertEqual(resp2.status_code, 400)

    def test_16_palette_db_graceful_fallback_when_disconnected(self):
        """Verify palette save still returns success for session when DB is down."""
        from unittest.mock import patch
        with patch('app.routes.colors.check_db_connection', return_value=(False, 'Connection refused')):
            resp = self.client.post(
                '/api/color/save-session',
                json={"palette": ["#F36B38", "#000000"]}
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertTrue(data['success'])
            self.assertFalse(data['persisted'])



if __name__ == '__main__':
    unittest.main()
