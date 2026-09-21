from rapidocr_onnxruntime import RapidOCR
ocr = RapidOCR()

def recognize_image(image):
    result , elapsed = ocr(image)
    lines = []
    if result:
        for item in result:
            lines.append(item[1])
    return "\n".join(lines)