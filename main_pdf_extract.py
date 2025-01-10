import PyPDF2
import re


def extract_patterns_from_pdf(file_path, page_index, patterns):
    """
    Extrai padrões específicos de texto de uma página de um arquivo PDF.
    """
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            if page_index >= len(reader.pages):
                print(f"Page {page_index} not found in {file_path}. Skipping...")
                return {key: None for key in patterns}
            
            page = reader.pages[page_index]
            text = page.extract_text()

            results = {}
            for pattern_name, pattern in patterns.items():
                match = re.search(pattern, text, re.IGNORECASE)
                results[pattern_name] = match.group(1).strip() if match else None
            return results
    except Exception as e:
        print(f"Error extracting patterns from PDF: {e}")
        return {key: None for key in patterns}


def extract_text_from_pdf(file_path, page_index):
    """
    Extrai todo o texto de uma página específica de um arquivo PDF.
    """
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            if page_index >= len(reader.pages):
                print(f"Page {page_index} not found in {file_path}. Skipping...")
                return None
            
            page = reader.pages[page_index]
            text = page.extract_text()
            return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None


def extract_header_and_ementa_from_pdf(file_path, page_index):
    """
    Extrai o header e a ementa da página especificada de um arquivo PDF.
    """
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            if page_index >= len(reader.pages):
                print(f"Page {page_index} not found in {file_path}. Skipping...")
                return None, None
            
            page = reader.pages[page_index]
            text = page.extract_text()

            ementa_pos = text.find("Ementa:")
            if ementa_pos != -1:
                header = text[:ementa_pos].strip()
                ementa_text = text[ementa_pos:].replace("Ementa:", "").strip()
                return header, ementa_text
            return None, None
            
    except Exception as e:
        print(f"Error extracting header and ementa from PDF: {e}")
        return None, None


def main(file_path, page_index=1):
    """
    Função principal para extrair padrões de um PDF.
    """
    ativo = {
            "APELANTE": r'APELANTE:\s*(.+)',
            "AGRAVANTE": r'AGRAVANTE:\s*(.+)',
            "EMBARGANTE": r'EMBARGANTE:\s*(.+)',
            "RECORRENTE": r'Recorrente:\s*(.+)',
        }
    passivo = {
            "APELANTES": r'APELANTES:\s*(.+)',
            "APELADO": r'APELADO:\s*(.+)',
            "APELANTE/APELADO:": r'Apelante/Apelado:\s*(.+)',
            "AGRAVADO": r'AGRAVADO:\s*(.+)',
            "AGRAVADA": r'AGRAVADA:\s*(.+)',
            "EMBARGADO": r'EMBARGADO:\s*(.+)',
            "RECORRIDO(A)": r'Recorrido\(a\): \s*(.+)',
        }
    
    outros = {
            "R$": r'R\$\s*([\d\.,]+)',
    }

    patterns = {**ativo, **passivo, **outros}
    
    results = extract_patterns_from_pdf(file_path, page_index, patterns)

    print(f"Results for {file_path}:")
    for value in results.items():
        print(f"{value if value else 'None'}")

    text = extract_text_from_pdf(file_path, page_index)
    if text:
        print(f"Text from page {page_index} of {file_path}:")
        print(text)

    header, ementa = extract_header_and_ementa_from_pdf(file_path, page_index)
    if header:
        print(f"Header from page {page_index} of {file_path}:")
        print(header)
    if ementa:
        print(f"Ementa from page {page_index} of {file_path}:")
        print(ementa)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        page_index = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        main(file_path, page_index)
    else:
        print("Usage: python main_pdf_extract.py <pdf_file> [page_index]")
