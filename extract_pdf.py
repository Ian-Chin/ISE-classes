import pdfplumber

pdf_path = r'C:\Users\ianga\Downloads\Week 3.pdf'

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}\n")
        print("=" * 80)
        
        for i, page in enumerate(pdf.pages, 1):
            print(f"\n--- PAGE {i} ---\n")
            text = page.extract_text()
            if text:
                print(text)
            else:
                print("[No text extracted from this page]")
            print("\n" + "=" * 80)
            
except Exception as e:
    print(f"Error reading PDF: {e}")
