import requests
import PyPDF2
from funcs import (
    filter_text,
    search_header_footer
)

def download_and_process_pdf(cdacordao):
    """
    Baixa e processa o PDF, retornando dados estruturados.
    """
    url = f"https://esaj.tjsp.jus.br/cjsg/getArquivo.do?cdAcordao={cdacordao}&cdForo=0"
    output_file = "processo_temp.pdf"

    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None

        with open(output_file, 'wb') as f:
            f.write(response.content)

        with open(output_file, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = reader.pages[0].extract_text()
            
            filtered_text = filter_text(text)
            headers, footers = search_header_footer([filtered_text])
            
            return {
                'text': filtered_text,
                'headers': headers,
                'footers': footers
            }

    except Exception as e:
        print(f"Erro ao processar PDF {cdacordao}: {e}")
        return None
