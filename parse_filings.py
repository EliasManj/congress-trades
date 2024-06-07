import pdfplumber

pdf_path = "data/pdf/2024/20024580.pdf"


with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    text = page.extract_text()

print(text)