from PIL import Image
import io


def parse_image(file_path: str) -> str:
    """
    Extract text from an image using pytesseract OCR.
    Falls back to a description prompt if tesseract is not installed.
    """
    try:
        import pytesseract
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)
        return text.strip() if text.strip() else '[No text detected in image]'
    except ImportError:
        return '[pytesseract not installed - image text extraction unavailable]'
    except Exception as e:
        return f'[Image parse error: {e}]'


def parse_image_bytes(image_bytes: bytes) -> str:
    """Same as parse_image but accepts raw bytes instead of a file path."""
    try:
        import pytesseract
        img = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(img)
        return text.strip() if text.strip() else '[No text detected in image]'
    except ImportError:
        return '[pytesseract not installed - image text extraction unavailable]'
    except Exception as e:
        return f'[Image parse error: {e}]'
