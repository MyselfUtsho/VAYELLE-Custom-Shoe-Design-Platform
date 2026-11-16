"""
VAYELLE — Unit & Integration Tests for Cloudinary API Service (Athoy Roy — Module 1)
Tests:
1. File extension validation (valid and invalid)
2. Image magic bytes detection (JPEG, PNG, WEBP, and invalid non-image content)
3. SSRF IPv4 and IPv6 private/internal/reserved address rejection
4. SSRF Public routable IP validation
5. URL validation for SSRF (localhost, private IPs, schemes)
6. Download image safely with redirect re-validation and SSRF blocking
7. Download image size limit (10 MB) and MIME/magic bytes verification
8. Direct uploaded image validation (size limit, empty file, extension, magic bytes)
9. Unconfigured credential handling
10. Successful Cloudinary upload with delivery optimization (f_auto, q_auto, 800x800)
11. Cloudinary API failure graceful error handling
12. Preset image uploading to Cloudinary
13. Manager route integration: direct file upload priority over URL
14. Manager route integration: upload failure prevents shoe document creation
15. Manager route integration: preset converts to Cloudinary URL in MongoDB
"""

import os
import io
import socket
import unittest
from unittest.mock import patch, MagicMock
import mongomock

from app import create_app
import app.db as db_module
from config import Config
from app.cloudinary_service import (
    is_cloudinary_configured,
    is_allowed_file,
    detect_image_format,
    is_safe_public_ip,
    validate_url_ssrf,
    download_image_safely,
    validate_uploaded_image,
    upload_shoe_image,
    upload_shoe_from_url,
    upload_preset_to_cloudinary,
    MAX_IMAGE_SIZE_BYTES
)

# Sample valid binary headers
VALID_JPEG_BYTES = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00' + b'\x00' * 100
VALID_PNG_BYTES = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR' + b'\x00' * 100
VALID_WEBP_BYTES = b'RIFF\x24\x00\x00\x00WEBPVP8 ' + b'\x00' * 100


class TestCloudinaryService(unittest.TestCase):

    def test_01_is_allowed_file_valid_extensions(self):
        """Verify image validation allows png, jpg, jpeg, webp."""
        self.assertTrue(is_allowed_file("sneaker.png"))
        self.assertTrue(is_allowed_file("runner.jpg"))
        self.assertTrue(is_allowed_file("casual.jpeg"))
        self.assertTrue(is_allowed_file("formal.webp"))
        self.assertTrue(is_allowed_file("UPPERCASE.JPG"))

    def test_02_is_allowed_file_invalid_extensions(self):
        """Verify non-image files are rejected."""
        self.assertFalse(is_allowed_file("script.js"))
        self.assertFalse(is_allowed_file("malware.exe"))
        self.assertFalse(is_allowed_file("doc.pdf"))
        self.assertFalse(is_allowed_file("no_extension"))
        self.assertFalse(is_allowed_file(""))

    def test_03_detect_image_format_valid(self):
        """Verify magic bytes detection accurately identifies JPEG, PNG, and WEBP formats."""
        self.assertEqual(detect_image_format(VALID_JPEG_BYTES), 'jpg')
        self.assertEqual(detect_image_format(VALID_PNG_BYTES), 'png')
        self.assertEqual(detect_image_format(VALID_WEBP_BYTES), 'webp')

    def test_04_detect_image_format_invalid(self):
        """Verify non-image binary content and text are rejected."""
        self.assertIsNone(detect_image_format(b'<!DOCTYPE html><html><body>Test</body></html>'))
        self.assertIsNone(detect_image_format(b'MZ\x90\x00\x03\x00\x00\x00'))
        self.assertIsNone(detect_image_format(b'{"key": "value"}'))
        self.assertIsNone(detect_image_format(b''))
        self.assertIsNone(detect_image_format(b'short'))

    def test_05_is_safe_public_ip_rejects_private_and_internal(self):
        """Verify SSRF protection blocks all private, internal, loopback, and reserved IPs."""
        blocked_ips = [
            '127.0.0.1',           # IPv4 loopback
            '127.0.1.1',           # IPv4 loopback range
            '10.0.0.1',            # RFC 1918 Class A
            '10.255.255.255',      # RFC 1918 Class A
            '172.16.0.1',          # RFC 1918 Class B
            '172.31.255.255',      # RFC 1918 Class B
            '192.168.1.1',         # RFC 1918 Class C
            '192.168.0.100',       # RFC 1918 Class C
            '169.254.169.254',     # Link-local / Cloud metadata service
            '100.64.0.1',          # Carrier-grade NAT (RFC 6598)
            '0.0.0.0',             # Unspecified address
            '::1',                 # IPv6 loopback
            'fe80::1',             # IPv6 link-local
            'fc00::1',             # IPv6 unique local
            'fd12:3456:789a::1',   # IPv6 unique local
            'invalid_ip_string'    # Invalid IP format
        ]
        for ip in blocked_ips:
            with self.subTest(ip=ip):
                self.assertFalse(is_safe_public_ip(ip), f"IP {ip} should be rejected as non-public")

    def test_06_is_safe_public_ip_allows_public(self):
        """Verify SSRF protection allows legitimate public routable IPs."""
        public_ips = [
            '8.8.8.8',
            '1.1.1.1',
            '142.250.190.46',
            '2606:4700:4700::1111'  # Public IPv6
        ]
        for ip in public_ips:
            with self.subTest(ip=ip):
                self.assertTrue(is_safe_public_ip(ip), f"Public IP {ip} should be allowed")

    @patch('socket.getaddrinfo')
    def test_07_validate_url_ssrf_rejects_internal_urls(self, mock_getaddrinfo):
        """Verify URL validation rejects internal hostnames, schemes, and private resolutions."""
        # Non-HTTP/HTTPS schemes
        safe, err = validate_url_ssrf("ftp://example.com/shoe.jpg")
        self.assertFalse(safe)
        self.assertIn("Only HTTP and HTTPS", err)

        safe, err = validate_url_ssrf("file:///etc/passwd")
        self.assertFalse(safe)

        # Localhost hostname
        safe, err = validate_url_ssrf("http://localhost:5000/image.jpg")
        self.assertFalse(safe)
        self.assertIn("blocked", err)

        # Internal domain name (.local / .internal)
        safe, err = validate_url_ssrf("http://metadata.google.internal/computeMetadata/v1")
        self.assertFalse(safe)

        # Hostname resolving to loopback 127.0.0.1
        mock_getaddrinfo.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', 80))]
        safe, err = validate_url_ssrf("http://attacker-owned-domain.com/shoe.jpg")
        self.assertFalse(safe)
        self.assertIn("private, loopback, or reserved IP", err)

        # Hostname resolving to IPv6 loopback ::1
        mock_getaddrinfo.return_value = [(socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('::1', 80, 0, 0))]
        safe, err = validate_url_ssrf("http://attacker-ipv6.com/shoe.jpg")
        self.assertFalse(safe)
        self.assertIn("private, loopback, or reserved IP", err)

    @patch('socket.getaddrinfo')
    def test_08_validate_url_ssrf_allows_safe_public_url(self, mock_getaddrinfo):
        """Verify URL validation allows public domains resolving to public IPs."""
        mock_getaddrinfo.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 443))]
        safe, err = validate_url_ssrf("https://example.com/shoes/runner.jpg")
        self.assertTrue(safe)
        self.assertIsNone(err)

    @patch('app.cloudinary_service.validate_url_ssrf')
    @patch('requests.Session.get')
    def test_09_download_image_safely_redirect_revalidation_blocks_ssrf(self, mock_get, mock_val_ssrf):
        """Verify that redirect destinations are re-validated and blocked if targeting private addresses."""
        # Initial URL passes SSRF check
        # First hop returns 302 redirect to an internal IP endpoint
        mock_val_ssrf.side_effect = [
            (True, None),                                                       # First hop safe
            (False, "Access blocked: URL resolves to private IP address (169.254.169.254).") # Redirect hop blocked!
        ]

        mock_resp_1 = MagicMock()
        mock_resp_1.status_code = 302
        mock_resp_1.headers = {'Location': 'http://169.254.169.254/latest/meta-data'}
        mock_get.return_value = mock_resp_1

        data, fmt, err = download_image_safely("https://legit-looking-redirector.com/shoe.jpg")
        self.assertIsNone(data)
        self.assertIn("Security check failed", err)
        self.assertIn("169.254.169.254", err)

    @patch('app.cloudinary_service.validate_url_ssrf', return_value=(True, None))
    @patch('requests.Session.get')
    def test_10_download_image_safely_enforces_10mb_limit(self, mock_get, mock_val_ssrf):
        """Verify download rejects files exceeding the 10 MB limit."""
        # Case A: Content-Length header > 10 MB
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {'Content-Length': str(15 * 1024 * 1024)}  # 15 MB
        mock_get.return_value = mock_resp

        data, fmt, err = download_image_safely("https://example.com/huge_image.jpg")
        self.assertIsNone(data)
        self.assertIn("exceeds maximum allowed limit of 10 MB", err)

        # Case B: Streamed chunks exceed 10 MB
        mock_resp_stream = MagicMock()
        mock_resp_stream.status_code = 200
        mock_resp_stream.headers = {}
        # Simulate chunks that sum up to > 10 MB
        mock_resp_stream.iter_content.return_value = [b'A' * (2 * 1024 * 1024)] * 6
        mock_get.return_value = mock_resp_stream

        data, fmt, err = download_image_safely("https://example.com/huge_stream.jpg")
        self.assertIsNone(data)
        self.assertIn("exceeded maximum allowed limit of 10 MB", err)

    @patch('app.cloudinary_service.validate_url_ssrf', return_value=(True, None))
    @patch('requests.Session.get')
    def test_11_download_image_safely_rejects_non_image_content(self, mock_get, mock_val_ssrf):
        """Verify downloaded file is rejected if Content-Type or magic bytes do not match images."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {'Content-Type': 'text/html'}
        mock_resp.iter_content.return_value = [b'<html><body>Not an image</body></html>']
        mock_get.return_value = mock_resp

        data, fmt, err = download_image_safely("https://example.com/fake.png")
        self.assertIsNone(data)
        self.assertIn("non-image Content-Type", err)

    @patch('app.cloudinary_service.validate_url_ssrf', return_value=(True, None))
    @patch('requests.Session.get')
    def test_12_download_image_safely_success_with_valid_image(self, mock_get, mock_val_ssrf):
        """Verify successful download with valid JPEG content."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {'Content-Type': 'image/jpeg'}
        mock_resp.iter_content.return_value = [VALID_JPEG_BYTES]
        mock_get.return_value = mock_resp

        data, fmt, err = download_image_safely("https://example.com/real_shoe.jpg")
        self.assertIsNotNone(data)
        self.assertEqual(fmt, 'jpg')
        self.assertIsNone(err)

    def test_13_validate_uploaded_image_valid_file(self):
        """Verify direct file upload passes validation for valid JPEG file."""
        file_obj = MagicMock()
        file_obj.filename = "sneaker.jpg"
        file_bio = io.BytesIO(VALID_JPEG_BYTES)
        file_obj.seek = file_bio.seek
        file_obj.tell = file_bio.tell
        file_obj.read = file_bio.read

        is_valid, err, fmt = validate_uploaded_image(file_obj)
        self.assertTrue(is_valid)
        self.assertIsNone(err)
        self.assertEqual(fmt, 'jpg')

    def test_14_validate_uploaded_image_enforces_10mb_limit(self):
        """Verify direct file upload is rejected if file size exceeds 10 MB."""
        file_obj = MagicMock()
        file_obj.filename = "huge_photo.png"
        
        # Mock file size > 10 MB
        file_obj.seek = MagicMock()
        file_obj.tell = MagicMock(return_value=12 * 1024 * 1024)
        file_obj.read = MagicMock(return_value=VALID_PNG_BYTES[:16])

        is_valid, err, fmt = validate_uploaded_image(file_obj)
        self.assertFalse(is_valid)
        self.assertIn("exceeds maximum allowed limit of 10 MB", err)

    def test_15_validate_uploaded_image_rejects_empty_file(self):
        """Verify direct file upload is rejected if file is 0 bytes."""
        file_obj = MagicMock()
        file_obj.filename = "empty.png"
        file_obj.seek = MagicMock()
        file_obj.tell = MagicMock(return_value=0)

        is_valid, err, fmt = validate_uploaded_image(file_obj)
        self.assertFalse(is_valid)
        self.assertIn("empty", err)

    def test_16_validate_uploaded_image_rejects_invalid_magic_bytes(self):
        """Verify direct file upload is rejected if file content is not a real image."""
        file_obj = MagicMock()
        file_obj.filename = "trojan.jpg"  # allowed extension, but corrupt content
        fake_bio = io.BytesIO(b'THIS_IS_NOT_AN_IMAGE_FILE')
        file_obj.seek = fake_bio.seek
        file_obj.tell = fake_bio.tell
        file_obj.read = fake_bio.read

        is_valid, err, fmt = validate_uploaded_image(file_obj)
        self.assertFalse(is_valid)
        self.assertIn("not a valid JPG, PNG, or WEBP", err)

    def test_17_upload_fails_safely_when_unconfigured(self):
        """Verify upload returns a clear error message when credentials are not configured."""
        with patch.object(Config, 'CLOUDINARY_CLOUD_NAME', ''), \
             patch.object(Config, 'CLOUDINARY_API_KEY', ''), \
             patch.object(Config, 'CLOUDINARY_API_SECRET', ''):
            
            url, err = upload_shoe_image("test_image.jpg")
            self.assertIsNone(url)
            self.assertIn("Cloudinary credentials not configured", err)

    @patch('cloudinary.uploader.upload')
    @patch('app.cloudinary_service.is_cloudinary_configured', return_value=True)
    def test_18_successful_cloudinary_upload_generates_optimized_url(self, mock_is_configured, mock_upload):
        """Verify successful upload applies f_auto, q_auto, and responsive dimensions (800x800)."""
        mock_upload.return_value = {
            "public_id": "vayelle/shoes/runner_apex",
            "version": 1700000000,
            "format": "jpg",
            "secure_url": "https://res.cloudinary.com/vayelle/image/upload/v1700000000/vayelle/shoes/runner_apex.jpg"
        }

        with patch.object(Config, 'CLOUDINARY_CLOUD_NAME', 'vayelle-demo'), \
             patch.object(Config, 'CLOUDINARY_API_KEY', '12345'), \
             patch.object(Config, 'CLOUDINARY_API_SECRET', 'secret'):

            url, err = upload_shoe_image("dummy_image_data.jpg", folder="vayelle/shoes")
            
            self.assertIsNone(err)
            self.assertIsNotNone(url)
            # Verify Cloudinary delivery optimization parameters in the generated URL
            self.assertIn("f_auto", url)
            self.assertIn("q_auto", url)
            self.assertIn("c_limit", url)
            self.assertIn("w_800", url)
            self.assertIn("h_800", url)
            mock_upload.assert_called_once()

    @patch('cloudinary.uploader.upload')
    @patch('app.cloudinary_service.is_cloudinary_configured', return_value=True)
    def test_19_cloudinary_api_failure_handled_gracefully(self, mock_is_configured, mock_upload):
        """Verify API exceptions from Cloudinary are caught and returned as clean error strings."""
        mock_upload.side_effect = Exception("Cloudinary rate limit exceeded")

        url, err = upload_shoe_image("dummy_image.jpg")
        
        self.assertIsNone(url)
        self.assertIn("Cloudinary upload failed: Cloudinary rate limit exceeded", err)

    @patch('os.path.isfile', return_value=True)
    @patch('app.cloudinary_service.upload_shoe_image')
    def test_20_upload_preset_to_cloudinary(self, mock_upload_img, mock_isfile):
        """Verify local preset files are resolved and uploaded to Cloudinary."""
        mock_upload_img.return_value = ("https://res.cloudinary.com/test/image/upload/f_auto,q_auto/v1/shoe-black-runner.jpg", None)

        url, err = upload_preset_to_cloudinary("/static/images/shoe-black-runner.jpg", app_root="/app")
        self.assertIsNone(err)
        self.assertEqual(url, "https://res.cloudinary.com/test/image/upload/f_auto,q_auto/v1/shoe-black-runner.jpg")
        mock_upload_img.assert_called_once()


class TestCloudinaryManagerRouteIntegration(unittest.TestCase):
    """
    Integration tests for the Manager Add Shoe route:
    Verifies Option A (File Upload), Option B (URL / Presets), precedence, and error handling.
    """

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['STRICT_CLOUDINARY_TEST'] = True
        self.app.config['SECRET_KEY'] = 'test-secret'
        self.client = self.app.test_client()

        # Mock MongoDB
        self.mock_client = mongomock.MongoClient()
        self.mock_db = self.mock_client['vayelle_test_db']

        # Patch check_db_connection and get_shoes_collection in manager route module
        self.patcher_check = patch('app.routes.manager.check_db_connection', return_value=(True, "Mock DB Connected"))
        self.patcher_shoes = patch('app.routes.manager.get_shoes_collection', return_value=self.mock_db.shoes)
        self.patcher_check.start()
        self.patcher_shoes.start()

        # Set manager session (role must be 'manager' as checked by manager_required)
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'mgr123'
            sess['user_email'] = 'manager@vayelle.com'
            sess['user_name'] = 'Platform Manager'
            sess['role'] = 'manager'

    def tearDown(self):
        self.patcher_check.stop()
        self.patcher_shoes.stop()

    @patch('app.routes.manager.is_cloudinary_configured', return_value=True)
    @patch('app.routes.manager.upload_shoe_image')
    @patch('app.routes.manager.upload_shoe_from_url')
    def test_21_direct_file_upload_takes_priority_over_url(self, mock_from_url, mock_upload_img, mock_is_conf):
        """Verify that when BOTH Option A (file) and Option B (URL) are supplied, file takes priority."""
        mock_upload_img.return_value = ("https://res.cloudinary.com/test/image/upload/f_auto,q_auto/v1/uploaded_shoe.jpg", None)

        data = {
            'shoe_name': 'Priority Test Sneaker',
            'category': 'Sneakers',
            'gender': 'Men',
            'base_price': '4500',
            'availability': 'In Stock',
            'shoe_image': (io.BytesIO(VALID_PNG_BYTES), 'uploaded_shoe.png'),
            'image_url': 'https://example.com/should_be_ignored.jpg'
        }

        res = self.client.post('/manager/shoes/add', data=data, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # upload_shoe_image MUST be called, upload_shoe_from_url must NOT be called
        mock_upload_img.assert_called_once()
        mock_from_url.assert_not_called()

        # Shoe saved in MongoDB with Cloudinary URL
        saved = self.mock_db.shoes.find_one({'shoe_name': 'Priority Test Sneaker'})
        self.assertIsNotNone(saved)
        self.assertEqual(saved['image_url'], "https://res.cloudinary.com/test/image/upload/f_auto,q_auto/v1/uploaded_shoe.jpg")

    @patch('app.routes.manager.is_cloudinary_configured', return_value=True)
    @patch('app.routes.manager.upload_shoe_image')
    def test_22_cloudinary_upload_failure_prevents_shoe_creation(self, mock_upload_img, mock_is_conf):
        """Verify that if Cloudinary upload fails, no shoe document is created in MongoDB."""
        mock_upload_img.return_value = (None, "Cloudinary upload failed: Network timeout")

        data = {
            'shoe_name': 'Doomed Shoe',
            'category': 'Casual',
            'gender': 'Women',
            'base_price': '3000',
            'availability': 'In Stock',
            'shoe_image': (io.BytesIO(VALID_JPEG_BYTES), 'doomed.jpg')
        }

        res = self.client.post('/manager/shoes/add', data=data, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Image processing failed", res.data)

        # Database must NOT contain the failed shoe
        count = self.mock_db.shoes.count_documents({'shoe_name': 'Doomed Shoe'})
        self.assertEqual(count, 0)

    @patch('app.routes.manager.is_cloudinary_configured', return_value=True)
    @patch('app.routes.manager.upload_preset_to_cloudinary')
    def test_23_preset_upload_saves_cloudinary_url_not_local_path(self, mock_preset, mock_is_conf):
        """Verify that selecting a preset uploads it to Cloudinary and saves the Cloudinary URL."""
        mock_preset.return_value = ("https://res.cloudinary.com/vayelle/image/upload/c_limit,f_auto,h_800,q_auto,w_800/v1/runner.jpg", None)

        data = {
            'shoe_name': 'Preset Converted Runner',
            'category': 'Running',
            'gender': 'Unisex',
            'base_price': '5200',
            'availability': 'In Stock',
            'image_url': '/static/images/shoe-black-runner.jpg'
        }

        res = self.client.post('/manager/shoes/add', data=data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        mock_preset.assert_called_once()
        saved = self.mock_db.shoes.find_one({'shoe_name': 'Preset Converted Runner'})
        self.assertIsNotNone(saved)
        # Final image_url in DB MUST be the Cloudinary URL, never the /static/ path
        self.assertTrue(saved['image_url'].startswith('https://res.cloudinary.com/'))
        self.assertNotIn('/static/images/', saved['image_url'])


if __name__ == '__main__':
    unittest.main()
