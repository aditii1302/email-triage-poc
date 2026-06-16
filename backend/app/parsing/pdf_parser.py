import fitz  # PyMuPDF


def parse_pdf(file_path: str) -> str:
    """Extract text from a PDF file. Returns empty string on failure."""
    try:
        doc = fitz.open(file_path)
        text = []
        for page in doc:
            text.append(page.get_text())
        doc.close()
        return '\n'.join(text).strip()
    except Exception as e:
        return f'[PDF parse error: {e}]'
