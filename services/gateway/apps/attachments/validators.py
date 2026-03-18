"""File validation and security hardening for attachments.

Validates magic bytes, sanitizes EXIF from images, and checks PDFs for
JavaScript injection. All validation runs BEFORE files are stored.
"""

import io
import logging
import re

from PIL import Image

logger = logging.getLogger(__name__)

# Magic byte signatures for allowed file types
MAGIC_SIGNATURES = {
    "image/png": [b"\x89PNG"],  # 89 50 4E 47
    "image/jpeg": [b"\xff\xd8\xff"],  # FF D8 FF
    "image/webp": [b"RIFF"],  # RIFF....WEBP (check WEBP at offset 8)
    "application/pdf": [b"%PDF"],  # 25 50 44 46
}

# Dangerous PDF action keywords
_PDF_DANGEROUS_ACTIONS = {"/JS", "/JavaScript", "/Launch", "/SubmitForm", "/GoToR"}


class FileValidationError(Exception):
    """Raised when file validation fails."""


def validate_magic_bytes(file_data: bytes, declared_content_type: str) -> None:
    """Verify that file magic bytes match the declared MIME type.

    Reads the first 16 bytes and checks against known signatures.
    Raises FileValidationError if magic bytes don't match.
    """
    if len(file_data) < 4:
        raise FileValidationError("File is too small to validate")

    header = file_data[:16]

    signatures = MAGIC_SIGNATURES.get(declared_content_type)
    if signatures is None:
        raise FileValidationError(f"Unsupported content type: {declared_content_type}")

    if declared_content_type == "image/webp":
        # WebP: starts with RIFF, then 4 bytes of size, then WEBP
        if not (header[:4] == b"RIFF" and header[8:12] == b"WEBP"):
            raise FileValidationError(
                "File magic bytes do not match declared type image/webp"
            )
        return

    for sig in signatures:
        if header[: len(sig)] == sig:
            return

    raise FileValidationError(
        f"File magic bytes do not match declared type {declared_content_type}"
    )


def sanitize_image(file_data: bytes) -> bytes:
    """Strip EXIF metadata from images using Pillow.

    Opens the image, clears metadata, and re-saves to BytesIO.
    Returns sanitized bytes.
    """
    try:
        img = Image.open(io.BytesIO(file_data))
        img_format = img.format
        if img_format is None:
            raise FileValidationError("Cannot determine image format")

        # Clear all metadata
        img.info.clear()

        # For JPEG, also strip EXIF via saving without exif
        output = io.BytesIO()
        save_kwargs: dict = {}
        if img_format == "JPEG":
            save_kwargs["exif"] = b""
        img.save(output, format=img_format, **save_kwargs)
        output.seek(0)
        return output.read()
    except FileValidationError:
        raise
    except Exception as e:
        raise FileValidationError(f"Failed to sanitize image: {e}") from e


def sanitize_pdf(file_data: bytes) -> bytes:
    """Check PDF for JavaScript injection and dangerous actions.

    Uses PyMuPDF (fitz) to scan for /JS, /JavaScript, /Launch,
    /SubmitForm, /GoToR actions. Rejects the file if any are found.
    Returns the original bytes if clean.
    """
    try:
        import fitz
    except ImportError:
        logger.warning("PyMuPDF not installed, skipping PDF sanitization")
        return file_data

    try:
        doc = fitz.open(stream=file_data, filetype="pdf")
    except Exception as e:
        raise FileValidationError(f"Failed to open PDF: {e}") from e

    try:
        # Check each page for JavaScript links
        for page_num in range(len(doc)):
            page = doc[page_num]
            links = page.get_links()
            for link in links:
                uri = link.get("uri", "")
                if uri and uri.lower().startswith("javascript:"):
                    raise FileValidationError(
                        f"PDF contains JavaScript URI on page {page_num + 1}"
                    )

        # Check xref objects for dangerous actions
        for xref in range(1, doc.xref_length()):
            try:
                obj_str = doc.xref_object(xref)
            except Exception:
                continue
            for action in _PDF_DANGEROUS_ACTIONS:
                if action in obj_str:
                    raise FileValidationError(
                        f"PDF contains dangerous action {action} in xref {xref}"
                    )
    finally:
        doc.close()

    return file_data


def sanitize_filename(name: str) -> str:
    """Sanitize a filename for safe storage.

    Strips directory path, replaces chars outside [a-zA-Z0-9._-] with
    underscore, collapses consecutive underscores, truncates to 255.
    """
    # Strip directory path
    name = name.rsplit("/", 1)[-1]
    name = name.rsplit("\\", 1)[-1]
    # Replace non-alphanumeric except .-_ with underscore
    name = re.sub(r"[^a-zA-Z0-9._-]", "_", name)
    # Collapse consecutive underscores
    name = re.sub(r"_+", "_", name)
    # Truncate to 255
    return name[:255]
