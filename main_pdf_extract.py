import PyPDF2
import re


def extract_patterns_from_pdf(file_path, page_index, patterns):
    """
    Extrai padrões específicos de texto de uma página de um arquivo PDF.
    """
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
            if match:
                results[pattern_name] = match.group(1).strip()                
        return results


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


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        page_index = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        main(file_path, page_index)
    else:
        print("Usage: python main_pdf_extract.py <pdf_file> [page_index]")
