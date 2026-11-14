"""
VAYELLE — Cloudinary API Service (Athoy Roy — Module 1)
Handles product image uploads and delivery optimizations for shoe silhouettes.
Uses the official Cloudinary Python SDK (cloudinary.uploader.upload, cloudinary.utils.cloudinary_url).

Features:
- Validates direct file uploads (extension, size <= 10MB, binary magic bytes).
- Robust SSRF protection for remote image URLs (DNS IPv4/IPv6 validation, redirect revalidation).
- Delivery optimization applying modern formats (f_auto), quality auto (q_auto), and responsive sizing (800x800).
- Automatic upload of preset shoe images so no local static paths are saved in MongoDB.
"""

import os
import io
import socket
import ipaddress
import urllib.parse
import requests
import cloudinary
import cloudinary.uploader
import cloudinary.utils
from config import Config

# Allowed image extensions for shoe catalog photos
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

# Allowed MIME types for uploaded/downloaded shoe photos
ALLOWED_MIME_TYPES = {'image/jpeg', 'image/jpg', 'image/png', 'image/webp'}

# Maximum allowed upload / download size (10 MB)
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024

# Remote image download timeout (seconds)
DOWNLOAD_TIMEOUT_SECONDS = 10

# Maximum redirect hops allowed when fetching remote images
MAX_REDIRECT_HOPS = 5


def is_cloudinary_configured():
    """
    Checks whether all required Cloudinary credentials are set in the environment.
    Returns True if configured, False otherwise.
    """
    cloud_name = Config.CLOUDINARY_CLOUD_NAME
    api_key = Config.CLOUDINARY_API_KEY
    api_secret = Config.CLOUDINARY_API_SECRET
    
    return bool(cloud_name and api_key and api_secret)


def configure_cloudinary():
    """
    Configures the Cloudinary SDK using credentials from Config.
    Ensures secure HTTPS delivery URLs are generated.
    """
    if is_cloudinary_configured():
        cloudinary.config(
            cloud_name=Config.CLOUDINARY_CLOUD_NAME,
            api_key=Config.CLOUDINARY_API_KEY,
            api_secret=Config.CLOUDINARY_API_SECRET,
            secure=True
        )
        return True
    return False


def is_allowed_file(filename):
    """
    Validates that the file has an allowed image extension (png, jpg, jpeg, webp).
    """
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_IMAGE_EXTENSIONS


def detect_image_format(data_bytes):
    """
    Inspects binary magic bytes to determine if the data is a real JPEG, PNG, or WEBP image.
    Returns 'jpg', 'png', 'webp', or None if not a recognized valid image format.
    """
    if not data_bytes or len(data_bytes) < 3:
        return None
        
    # JPEG starts with FF D8 FF
    if len(data_bytes) >= 3 and data_bytes[:3] == b'\xff\xd8\xff':
        return 'jpg'
        
    # PNG starts with 89 50 4E 47 0D 0A 1A 0A
    if len(data_bytes) >= 8 and data_bytes[:8] == b'\x89PNG\r\n\x1a\n':
        return 'png'
        
    # WEBP starts with RIFF....WEBP
    if len(data_bytes) >= 12 and data_bytes[:4] == b'RIFF' and data_bytes[8:12] == b'WEBP':
        return 'webp'
        
    return None


def is_safe_public_ip(ip_str):
    """
    Validates whether an IP address is a safe, publicly routable address.
    Rejects IPv4 and IPv6:
    - Loopback (127.0.0.0/8, ::1)
    - Private networks (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, fc00::/7)
    - Link-local (169.254.0.0/16, fe80::/10)
    - Multicast & reserved ranges
    - Carrier-grade NAT (100.64.0.0/10)
    - Unspecified addresses (0.0.0.0, ::)
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        
        # Check standard ipaddress flags (loopback, private, link-local, multicast, reserved, unspecified)
        if (ip.is_loopback or 
            ip.is_private or 
            ip.is_link_local or 
            ip.is_multicast or 
            ip.is_reserved or 
            ip.is_unspecified):
            return False
            
        # Additional IPv4 checks for non-routable/reserved ranges
        if isinstance(ip, ipaddress.IPv4Address):
            # Carrier-grade NAT (RFC 6598)
            if ip in ipaddress.IPv4Network('100.64.0.0/10'):
                return False
            # Current network
            if ip in ipaddress.IPv4Network('0.0.0.0/8'):
                return False
            # Benchmarking (RFC 2544)
            if ip in ipaddress.IPv4Network('198.18.0.0/15'):
                return False
            # Documentation / Test networks
            if (ip in ipaddress.IPv4Network('192.0.2.0/24') or
                ip in ipaddress.IPv4Network('198.51.100.0/24') or
                ip in ipaddress.IPv4Network('203.0.113.0/24')):
                return False
            # Future use / reserved class E
            if ip in ipaddress.IPv4Network('240.0.0.0/4'):
                return False

        return True
    except ValueError:
        return False


def validate_url_ssrf(url):
    """
    Validates a URL against Server-Side Request Forgery (SSRF).
    Checks:
    - Scheme is strictly http or https.
    - Hostname is present and does not resolve to internal, private, loopback, or cloud-metadata endpoints.
    - Resolves all IPv4 and IPv6 DNS entries and verifies that every resolved IP is public and safe.
    
    Returns:
        (True, None) if safe.
        (False, error_message) if unsafe.
    """
    if not url or not isinstance(url, str):
        return False, "Image URL cannot be empty."

    parsed = urllib.parse.urlparse(url)
    scheme = parsed.scheme.lower()
    if scheme not in ('http', 'https'):
        return False, f"Invalid URL scheme '{parsed.scheme}'. Only HTTP and HTTPS URLs are permitted."

    hostname = parsed.hostname
    if not hostname:
        return False, "Invalid URL: missing hostname."

    hostname_clean = hostname.lower()
    # Reject common internal hostnames
    if (hostname_clean in ('localhost', 'metadata.google.internal') or
        hostname_clean.endswith(('.localhost', '.local', '.internal', '.lan', '.localdomain'))):
        return False, f"Access to internal hostname '{hostname}' is blocked."

    # Resolve hostname to all IP addresses (IPv4 & IPv6)
    try:
        # socket.getaddrinfo returns list of 5-tuples: (family, type, proto, canonname, sockaddr)
        port = parsed.port or (443 if scheme == 'https' else 80)
        addr_info = socket.getaddrinfo(hostname, port)
    except socket.gaierror as e:
        return False, f"Could not resolve hostname '{hostname}': {str(e)}"
    except Exception as e:
        return False, f"DNS lookup failed for '{hostname}': {str(e)}"

    if not addr_info:
        return False, f"No IP addresses resolved for '{hostname}'."

    # Validate EVERY resolved IP address
    for entry in addr_info:
        sockaddr = entry[4]
        ip_str = sockaddr[0]
        if not is_safe_public_ip(ip_str):
            return False, f"Access blocked: URL resolves to private, loopback, or reserved IP address ({ip_str})."

    return True, None


def download_image_safely(url, max_size=MAX_IMAGE_SIZE_BYTES, timeout=DOWNLOAD_TIMEOUT_SECONDS, max_redirects=MAX_REDIRECT_HOPS):
    """
    Safely downloads an image from a remote URL with strict security validations:
    - Re-validates SSRF on every redirect destination.
    - Limits redirects to max_redirects hops.
    - Limits download size to max_size (default 10 MB).
    - Times out after timeout seconds.
    - Validates Content-Type header and binary magic bytes.
    
    Returns:
        (image_bytes, format, None) on success.
        (None, None, error_message) on failure.
    """
    current_url = url
    session = requests.Session()
    
    for hop in range(max_redirects + 1):
        # 1. SSRF check before requesting
        is_safe, err = validate_url_ssrf(current_url)
        if not is_safe:
            return None, None, f"Security check failed: {err}"
            
        try:
            # 2. Make request with allow_redirects=False to inspect every hop
            response = session.get(
                current_url,
                stream=True,
                timeout=timeout,
                allow_redirects=False,
                headers={'User-Agent': 'VayelleShoeCatalog/1.0 (Athoy-Module-1)'}
            )
        except requests.exceptions.Timeout:
            return None, None, f"Image download timed out after {timeout} seconds."
        except requests.exceptions.RequestException as e:
            return None, None, f"Failed to download image from URL: {str(e)}"

        # 3. Handle redirects manually to re-validate destination IP
        if response.status_code in (301, 302, 303, 307, 308):
            location = response.headers.get('Location')
            if not location:
                return None, None, "Redirect response received without a Location header."
            # Resolve relative redirect URLs against current URL
            current_url = urllib.parse.urljoin(current_url, location)
            continue

        # 4. Check for successful HTTP status
        if response.status_code != 200:
            return None, None, f"Remote server returned HTTP {response.status_code}."

        # 5. Check Content-Length header if provided
        content_length_header = response.headers.get('Content-Length')
        if content_length_header:
            try:
                content_length = int(content_length_header)
                if content_length > max_size:
                    return None, None, f"Image size ({content_length / (1024*1024):.1f} MB) exceeds maximum allowed limit of 10 MB."
            except ValueError:
                pass  # Ignore malformed header and rely on stream chunk limit

        # 6. Stream and accumulate bytes up to max_size limit
        data_buffer = bytearray()
        try:
            for chunk in response.iter_content(chunk_size=64 * 1024):
                if chunk:
                    data_buffer.extend(chunk)
                    if len(data_buffer) > max_size:
                        return None, None, f"Image download exceeded maximum allowed limit of 10 MB."
        except requests.exceptions.RequestException as e:
            return None, None, f"Error streaming image data: {str(e)}"

        # 7. Check MIME / Content-Type
        content_type = response.headers.get('Content-Type', '').lower().split(';')[0].strip()
        if content_type and not content_type.startswith('image/'):
            return None, None, f"Remote URL returned non-image Content-Type: '{content_type}'."

        # 8. Check binary magic bytes
        image_bytes = bytes(data_buffer)
        detected_format = detect_image_format(image_bytes)
        if not detected_format:
            return None, None, "Downloaded file does not contain valid image content (must be JPG, PNG, or WEBP)."

        return image_bytes, detected_format, None

    return None, None, f"Image URL exceeded maximum allowed redirects ({max_redirects})."


def validate_uploaded_image(file_storage, max_size=MAX_IMAGE_SIZE_BYTES):
    """
    Validates a file uploaded directly via request.files.
    Checks:
    - Filename is present and has allowed extension.
    - File size does not exceed max_size (10 MB).
    - File is not empty (0 bytes).
    - File content magic bytes match a valid image (JPEG, PNG, WEBP).
    
    Returns:
        (True, None, format) on success.
        (False, error_message, None) on failure.
    """
    if not file_storage or not file_storage.filename:
        return False, "No file selected.", None

    if not is_allowed_file(file_storage.filename):
        return False, "Invalid file format. Allowed extensions are: JPG, JPEG, PNG, and WEBP.", None

    # Measure stream size
    file_storage.seek(0, os.SEEK_END)
    size = file_storage.tell()
    file_storage.seek(0)

    if size == 0:
        return False, "Uploaded file is empty (0 bytes).", None

    if size > max_size:
        return False, f"Uploaded file ({size / (1024*1024):.1f} MB) exceeds maximum allowed limit of 10 MB.", None

    # Check magic bytes from initial chunk
    header = file_storage.read(16)
    file_storage.seek(0)

    fmt = detect_image_format(header)
    if not fmt:
        return False, "Uploaded file content is not a valid JPG, PNG, or WEBP image.", None

    return True, None, fmt


def upload_shoe_image(file_obj, folder="vayelle/shoes"):
    """
    Uploads a shoe product image to Cloudinary and generates an optimized CDN delivery URL.
    
    Parameters:
        file_obj: A file-like object, BytesIO, or physical file path.
        folder: Cloudinary asset folder (default: 'vayelle/shoes').
        
    Returns:
        (optimized_delivery_url, None) on success.
        (None, error_message) on failure.
    """
    # 1. Verify credentials
    if not is_cloudinary_configured():
        return None, "Cloudinary credentials not configured in environment variables (CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET)."

    # 2. Configure SDK
    configure_cloudinary()

    # 3. Perform upload with transformation preset
    try:
        response = cloudinary.uploader.upload(
            file_obj,
            folder=folder,
            resource_type="image",
            use_filename=True,
            unique_filename=True,
            transformation=[
                {"quality": "auto", "fetch_format": "auto"}
            ]
        )

        public_id = response.get("public_id")
        version = response.get("version")
        format_ext = response.get("format")

        # 4. Generate Cloudinary optimized delivery URL (f_auto, q_auto, max 800x800)
        try:
            optimized_url, _ = cloudinary.utils.cloudinary_url(
                public_id,
                version=version,
                format=format_ext,
                secure=True,
                quality="auto",
                fetch_format="auto",
                width=800,
                height=800,
                crop="limit"
            )
            return optimized_url, None
        except Exception:
            # Fallback to direct secure_url from upload response
            secure_url = response.get("secure_url")
            if secure_url:
                return secure_url, None
            return None, "Cloudinary upload response did not include a secure delivery URL."

    except Exception as e:
        return None, f"Cloudinary upload failed: {str(e)}"


def upload_shoe_from_url(image_url, folder="vayelle/shoes"):
    """
    Safely downloads a remote image (with SSRF protection, size limits, and format verification)
    and uploads it to Cloudinary.
    
    Returns:
        (optimized_delivery_url, None) on success.
        (None, error_message) on failure.
    """
    # 1. Safe download with strict SSRF validation
    image_bytes, fmt, download_err = download_image_safely(image_url)
    if download_err:
        return None, download_err

    # 2. Upload byte stream to Cloudinary
    image_io = io.BytesIO(image_bytes)
    return upload_shoe_image(image_io, folder=folder)


def upload_preset_to_cloudinary(preset_path, app_root, folder="vayelle/shoes"):
    """
    Uploads a local preset image file (e.g. /static/images/shoe-black-runner.jpg) to Cloudinary
    so that newly created shoe records always store a Cloudinary CDN URL instead of a local static path.
    
    Returns:
        (optimized_delivery_url, None) on success.
        (None, error_message) on failure.
    """
    # Extract filename safely
    filename = os.path.basename(preset_path.strip())
    if not filename or not is_allowed_file(filename):
        return None, f"Invalid preset image filename: {filename}"

    # Resolve local physical path
    local_path = os.path.join(app_root, 'static', 'images', filename)
    if not os.path.isfile(local_path):
        return None, f"Preset image file not found on disk: {filename}"

    # Upload local file to Cloudinary
    return upload_shoe_image(local_path, folder=folder)
