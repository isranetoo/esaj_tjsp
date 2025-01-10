import requests
import json
import os
import re
import PyPDF2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

def download_pdf(cdacordao):
    """
    Baixa o PDF com base no cdacordao e executa a extração.
    """
    url = f"https://esaj.tjsp.jus.br/cjsg/getArquivo.do?cdAcordao={cdacordao}&cdForo=0"
    output_file = "processo_temp.pdf"  

    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f"PDF {cdacordao} baixado com sucesso.")

            # Extrair informações da primeira página
            first_page_text = extract_text_from_pdf(output_file, 0)
            if first_page_text:
                print(f"Text from first page of {output_file}:")
                print(first_page_text)

            # Extrair header e ementa da segunda página
            header, ementa = extract_header_and_ementa_from_pdf(output_file, 1)
            if header:
                print(f"Header from second page of {output_file}:")
                print(header)
            if ementa:
                print(f"Ementa from second page of {output_file}:")
                print(ementa)
        else:
            print(f"Erro ao baixar o PDF para {cdacordao}. Status: {response.status_code}")
    except Exception as e:
        print(f"Erro ao tentar baixar o PDF {cdacordao}: {e}")

def remove_prefix(text, prefix):
    """Remove o prefixo especificado do texto, se presente."""
    if text and text.startswith(prefix):
        return text.replace(prefix, "").strip()
    return text

def extract_case_data(driver):
    """Coleta os dados da página de processos e baixa os PDFs correspondentes."""
    results = []
    rows_xpath = "//body/table[1]/tbody/tr"

    try:
        rows = driver.find_elements(By.XPATH, rows_xpath)

        for i, row in enumerate(rows, start=1):
            try:
                links = row.find_elements(By.XPATH, f"td[2]/table/tbody/tr[1]/td/a")
                for link in links:
                    cdacordao = link.get_attribute("cdacordao")
                    if cdacordao:
                        download_pdf(cdacordao)

                pdf_header, pdf_ementa = extract_header_and_ementa_from_pdf("processo_temp.pdf", 1)

                collected_ementa = remove_prefix(row.find_element(By.XPATH, f"td[2]/table/tbody/tr[8]/td/div[1]").text, "Ementa:")
                
                if pdf_ementa and collected_ementa:
                    pdf_words = set(pdf_ementa.lower().split())
                    collected_words = set(collected_ementa.lower().split())
                    matching_words = pdf_words.intersection(collected_words)
                    similarity_score = len(matching_words) / max(len(pdf_words), len(collected_words))
                    ementa_match = similarity_score > 0.5
                else:
                    ementa_match = False

                print(f"\nProcesso {i}:")
                print(f"Header do PDF:")
                print(pdf_header if pdf_header else "Não encontrado")
                print(f"\nEmenta do PDF:")
                print(pdf_ementa if pdf_ementa else "Não encontrada")
                print(f"\nEmenta coletada:")
                print(collected_ementa)
                print(f"\nTextos correspondem: {ementa_match}")
                print("-" * 80)

                pdf_patterns_ativo = extract_patterns_from_pdf(
                    "processo_temp.pdf", 1, {
                        "APELANTE": r'APELANTE:\s*(.+)',
                        "AGRAVANTE": r'AGRAVANTE:\s*(.+)',
                        "EMBARGANTE": r'EMBARGANTE:\s*(.+)',
                        "RECORRENTE": r'Recorrente:\s*(.+)',
                    }
                ) or {}

                pdf_patterns_passivo = extract_patterns_from_pdf(
                    "processo_temp.pdf", 1, {
                        "APELADO": r'APELADO:\s*(.+)',
                        "AGRAVADO": r'AGRAVADO:\s*(.+)',
                        "EMBARGADO": r'EMBARGADO:\s*(.+)',
                        "RECORRIDO": r'Recorrido:\s*(.+)',
                    }
                ) or {}

                nome_parte_ativa = None
                tipo_parte_ativa = None
                for key, value in pdf_patterns_ativo.items():
                    if value:
                        nome_parte_ativa = value.strip()
                        tipo_parte_ativa = key
                        break

                nome_parte_passiva = None
                tipo_parte_passiva = None
                for key, value in pdf_patterns_passivo.items():
                    if value:
                        nome_parte_passiva = value.strip()
                        tipo_parte_passiva = key
                        break

                case_data = {                             
                    "numero":  row.find_element(By.XPATH, f"td[2]/table/tbody/tr[1]/td/a[1]").text,
                    "valorDaCausa": None,
                    "area_code": None,
                    "tribunal_code": None,
                    "vara_code": None,
                    "area": None,
                    "tribunal": "TJ-SP",
                    "comarca": remove_prefix(row.find_element(By.XPATH, f"td[2]/table/tbody/tr[4]/td").text, "Comarca: "),
                    "instancias": [{
                        "fonte_script": "Scrapper",
                        "fonte_sistema": "TJ-SP",
                        "fonte_tipo": "TRIBUNAL",
                        "fonte_url": "https://esaj.tjsp.jus.br/",

                        "grau": None,
                        "classe": None,
                        "orgaoJulgador": remove_prefix(row.find_element(By.XPATH, f"td[2]/table/tbody/tr[5]/td").text, "Órgão julgador: "),
                        "segredoJustica": None,
                        "justicaGratuita": None,
                        "assunto_principal": None,
                        "assuntos": remove_prefix(row.find_element(By.XPATH, f"td[2]/table/tbody/tr[2]/td").text, "Classe/Assunto: "),
                        "first_mov": None,
                        "last_mov": remove_prefix(row.find_element(By.XPATH, f"td[2]/table/tbody/tr[7]/td").text, "Data de publicação: "),
                        "envolvidos": [
                            {
                                "nome": nome_parte_ativa,
                                "tipo": tipo_parte_ativa if tipo_parte_ativa else "RECLAMANTE",
                                "polo": "ATIVO",
                                "id_sistema": {"login": None},
                                "documento": [],
                                "endereco": {},
                                "representantes": [
                                    {
                                        "nome": None,
                                        "tipo": "ADVOGADO",
                                        "polo": "ATIVO",
                                        "id_sistema": {"login": None},
                                        "documento": [{"CPF": None}],
                                        "endereco": {
                                            "logradouro": None,
                                            "numero": None,
                                            "complemento": None,
                                            "bairro": None,
                                            "municipio": None,
                                            "estado": None,
                                            "cep": None,
                                        }
                                    }
                                ]
                            },
                            {
                                "nome": nome_parte_passiva,
                                "tipo": tipo_parte_passiva if tipo_parte_passiva else "RECLAMADO",
                                "polo": "PASSIVO",
                                "id_sistema": {"login": None},
                                "documento": [],
                                "endereco": {},
                                "representantes": [
                                    {
                                        "nome": None,
                                        "tipo": "ADVOGADO",
                                        "polo": "PASSIVO",
                                        "id_sistema": {"login": None},
                                        "documento": [{"CPF": None}],
                                        "endereco": {
                                            "logradouro": None,
                                            "numero": None,
                                            "complemento": None,
                                            "bairro": None,
                                            "municipio": None,
                                            "estado": None,
                                            "cep": None
                                        }
                                    }
                                ]
                            },
                            {
                                "nome": remove_prefix(row.find_element(By.XPATH, f"td[2]/table/tbody/tr[3]/td").text, "Relator(a): "),
                                "tipo": "RELATOR(A)",
                                "polo": "OUTROS",
                                "id_sistema": {"login": None},
                                "documento": [],
                                "endereco": {},
                                "representantes": []
                            }
                        ],
                        "movimentacoes": [
                    {
                        "titulo": "Data de publicação",
                        "tipoConteudo": "HTML",
                        "data":  remove_prefix(row.find_element(By.XPATH, f"td[2]/table/tbody/tr[7]/td").text,
                          "Data de publicação: "              
                        ),
                        "ativo": None,
                        "documento":None,
                        "mostrarHeaderData": None,
                        "usuarioCriador": None
                    },
                    {
                        "titulo": None,
                        "tipoConteudo": None,
                        "data": None,
                        "ativo": None,
                        "documento": None,
                        "usuarioCriador": None
                    },
                    {
                        "id": None,
                        "idUnicoDocumento": None,
                        "titulo": "Ata da Audieancia",
                        "tipo": "Ata da Audieancia",
                        "tipoConteudo": "PDF",
                        "data":  remove_prefix(row.find_element(By.XPATH, f"td[2]/table/tbody/tr[7]/td").text,
                          "Data de publicação: "              
                        ),
                        "ativo": None,
                        "documentoSigiloso": None,
                        "usuarioPerito": None,
                        "publico": None,
                        "usuarioJuntada": None,
                        "usuarioCriador": None,
                        "instancia": None,
                        "ementa": collected_ementa,
                    }
                ]
            }
        ],
        "ementa_match": ementa_match,
        "pdf_header": pdf_header
    }

                case_data.update({
                    "ementa_match": ementa_match,
                    "pdf_header": pdf_header,
                    "similarity_score": similarity_score if ementa_match else 0
                })

                results.append(case_data)
                print(f"Processo {i} coletado com sucesso.")
                print(f"Ementa match: {ementa_match}")
                print(f"PDF Header: {pdf_header}")
                print(f"Collected Ementa: {collected_ementa}")
            except Exception as e:
                print(f"Erro ao coletar dados da linha {i}: {e}")
        return results

    except Exception as e:
        print(f"Erro ao coletar dados da tabela: {e}")
        return []

def save_session_data(driver):
    try:
        cookies = driver.get_cookies()
        with open("session_cookies.json", "w") as file:
            json.dump(cookies, file)
    except Exception as e:
        print(f"Erro ao salvar cookies da sessão: {str(e)}")

def load_session_data(driver):
    try:
        if os.path.exists("session_cookies.json"):
            with open("session_cookies.json", "r") as file:
                cookies = json.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
            return True
    except Exception as e:
        print(f"Erro ao carregar cookies da sessão: {str(e)}")
    return False

if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        session_loaded = load_session_data(driver)

        if not session_loaded:
            print("A sessão não foi carregada. Coletando dados de processos.")
            driver.get("https://esaj.tjsp.jus.br/cjsg/resultadoCompleta.do")

        all_case_data = []
        base_url = "https://esaj.tjsp.jus.br/cjsg/trocaDePagina.do?tipoDeDecisao=A&pagina={}&conversationId="
        page = 1
        while page <= 1:
            try:
                print(f"Acessando página {page}")
                driver.get(base_url.format(page))
                
                case_data = extract_case_data(driver)
                all_case_data.extend(case_data)
                
                page += 1
            except Exception as e:
                print(f"Erro ao processar página {page}: {str(e)}")
                continue

        try:
            with open("processos.json", "w", encoding="utf-8") as file:
                json.dump(all_case_data, file, ensure_ascii=False, indent=4)
            print("Dados de todos os processos salvos no arquivo 'processos.json'.")
            save_session_data(driver)
        except Exception as e:
            print(f"Erro ao salvar dados: {str(e)}")

    finally:
        driver.quit()
