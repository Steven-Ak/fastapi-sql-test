import io
import pypdf


def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    """
    Extract plain text from a PDF given its raw bytes.
    Returns an empty string if extraction fails.
    """
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = pypdf.PdfReader(pdf_file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        print(f"PDF text extraction failed: {e}")
        return ""
