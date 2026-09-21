from pathlib import Path
import pypdfium2 as pdfium
from ocr_service import recognize_image

base_dir = Path(__file__).resolve().parent
pdf_path = base_dir / "output" / "pdf" / "day4-scanned-notes.pdf"
with pdfium.PdfDocument(pdf_path) as pdf:
    page = pdf[0]
    bitmap = page.render(scale=2)
    image = bitmap.to_pil()
    image.save(base_dir/"scan-page-1.png")
    image.close()
    bitmap.close()
    page.close()
print("第一页已保存为 scan-page-1.png")


image_path = base_dir / "scan-page-1.png"
text = recognize_image(str(image_path))

print(text)
print("字符数：", len(text))