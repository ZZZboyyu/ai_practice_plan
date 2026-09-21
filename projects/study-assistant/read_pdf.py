from contextlib import closing
from io import BytesIO

import pypdfium2 as pdfium
from pypdf import PdfReader

from ocr_service import recognize_image


def extract_pdf_pages(file):
    file.seek(0)
    pdf_bytes = file.read()

    reader = PdfReader(BytesIO(pdf_bytes))
    pages = []

    with pdfium.PdfDocument(pdf_bytes) as pdf:
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            # 这一页没有可直接提取的文字，尝试 OCR
            if not text.strip():
                with closing(pdf[page_number - 1]) as scan_page:
                    with closing(scan_page.render(scale=2)) as bitmap:
                        with bitmap.to_pil() as image:
                            text = recognize_image(image)

            pages.append({
                "page_number": page_number,
                "text": text,
                "char_count": len(text),
            })

    return pages
