import re
import io
import csv
from typing import List

def simple_text_splitter(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
        if start < 0:
            start = 0
    return chunks

def extract_text_from_file(file_content: bytes, filename: str) -> str:
    ext = filename.split(".")[-1].lower()
    
    if ext == "pdf":
        try:
            import pypdf
            pdf_file = io.BytesIO(file_content)
            reader = pypdf.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
        except Exception as e:
            return f"Error parsing PDF: {str(e)}"
            
    elif ext in ["docx", "doc"]:
        try:
            import docx
            doc_file = io.BytesIO(file_content)
            doc = docx.Document(doc_file)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except Exception as e:
            return f"Error parsing Word Document: {str(e)}"
            
    elif ext == "csv":
        try:
            try:
                csv_text = file_content.decode("utf-8", errors="ignore")
            except Exception:
                csv_text = file_content.decode("latin-1", errors="ignore")
            
            f = io.StringIO(csv_text)
            reader = csv.reader(f)
            rows = []
            for row in reader:
                rows.append(", ".join(row))
            return "\n".join(rows)
        except Exception as e:
            return f"Error parsing CSV: {str(e)}"
            
    else:
        # Default text decoding
        try:
            return file_content.decode("utf-8")
        except Exception:
            return file_content.decode("latin-1", errors="ignore")
