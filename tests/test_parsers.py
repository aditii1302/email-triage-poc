import os
import pytest
from backend.app.parsing.pdf_parser import parse_pdf
from backend.app.parsing.docx_parser import parse_docx
from backend.app.parsing.image_parser import parse_image, parse_image_bytes


def test_parse_pdf_valid(tmp_path):
    from reportlab.pdfgen import canvas
    pdf_path = str(tmp_path / 'test.pdf')
    c = canvas.Canvas(pdf_path)
    c.drawString(100, 750, 'Error Code: AUTH-401')
    c.save()
    result = parse_pdf(pdf_path)
    assert 'AUTH-401' in result


def test_parse_pdf_missing_file():
    result = parse_pdf('/nonexistent/file.pdf')
    assert 'error' in result.lower() or result == ''


def test_parse_docx_valid(tmp_path):
    from docx import Document
    docx_path = str(tmp_path / 'test.docx')
    doc = Document()
    doc.add_paragraph('VPN Client is not responding')
    doc.save(docx_path)
    result = parse_docx(docx_path)
    assert 'VPN Client' in result


def test_parse_docx_missing_file():
    result = parse_docx('/nonexistent/file.docx')
    assert 'error' in result.lower() or result == ''


def test_parse_image_bytes_valid():
    from PIL import Image, ImageDraw
    import io
    img = Image.new('RGB', (200, 100), color='white')
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), 'ERROR 500', fill='black')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    result = parse_image_bytes(buf.getvalue())
    assert isinstance(result, str)
    assert len(result) > 0


def test_parse_image_missing_file():
    result = parse_image('/nonexistent/file.png')
    assert isinstance(result, str)
