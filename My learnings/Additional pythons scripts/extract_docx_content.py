from docx import Document
import os

def extract_docx_text(docx_path):
	doc = Document(docx_path)
	text = []
	for para in doc.paragraphs:
		text.append(para.text)
	return '\n'.join(text)

def main():
	base = r"c:\Odoo Study\My learnings\Rohan_Documentation"
	files = ["WorkCenter.docx", "Subcontracting.docx"]
	for fname in files:
		fpath = os.path.join(base, fname)
		print(f"\n--- {fname} ---\n")
		print(extract_docx_text(fpath))

if __name__ == "__main__":
	main()