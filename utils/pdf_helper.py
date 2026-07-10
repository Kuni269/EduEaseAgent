"""
pdf_helper.py
─────────────
Utility functions to extract plain text from an uploaded PDF file.
Uses PyMuPDF (fitz) – a lightweight, zero-dependency PDF parser.
"""

import fitz  # PyMuPDF


def extract_text_from_pdf(uploaded_file) -> str:
    """
    Extract all text from a Streamlit UploadedFile object (PDF).

    Parameters
    ----------
    uploaded_file : streamlit.runtime.uploaded_file_manager.UploadedFile
        The file object returned by st.file_uploader().

    Returns
    -------
    str
        All extracted text joined across pages, or an empty string if
        the PDF contains no selectable text (e.g. scanned image PDFs).
    """
    # Read raw bytes from the uploaded file
    pdf_bytes = uploaded_file.read()

    # Open with PyMuPDF directly from memory
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    pages_text = []
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        text = page.get_text("text")          # plain-text extraction
        if text.strip():                       # skip blank pages
            pages_text.append(text)

    doc.close()
    return "\n\n".join(pages_text)
