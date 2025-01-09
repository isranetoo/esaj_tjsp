import requests
import json
import os
import main_pdf_extract 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


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


def download_pdf(cdacordao):
    """
    Baixa o PDF com base no cdacordao e executa a extração.
    """
    url = f"https://esaj.tjsp.jus.br/cjsg/getArquivo.do?cdAcordao={cdacordao}&cdForo=0"
    output_file = "processo_temp.pdf"  # Nome fixo para sobrescrever o arquivo anterior

    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f"PDF {cdacordao} baixado com sucesso.")

            main_pdf_extract.main(output_file, page_index=1)
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
                # Baixa o PDF primeiro
                links = row.find_elements(By.XPATH, f"td[2]/table/tbody/tr[1]/td/a")
                for link in links:
                    cdacordao = link.get_attribute("cdacordao")
                    if cdacordao:
                        download_pdf(cdacordao)

                # Extrai os padrões do PDF
                pdf_patterns = main_pdf_extract.extract_patterns_from_pdf(
                    "processo_temp.pdf", 1, {
                        "APELANTE": r'APELANTE:\s*(.+)',
                        "AGRAVANTE": r'AGRAVANTE:\s*(.+)',
                        "EMBARGANTE": r'EMBARGANTE:\s*(.+)',
                        "RECORRENTE": r'Recorrente:\s*(.+)',
                    }
                ) or {}

                # Garante que pdf_patterns é um dicionário, mesmo que vazio
                if pdf_patterns is None:
                    pdf_patterns = {}

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
                                "nome": {key: (remove_prefix(value, key) if value else None) 
                                   for key, value in pdf_patterns.items()},
                                "tipo": "RECLAMANTE",
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
                                "nome": None,
                                "tipo": "RECLAMADO",
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
                        "instancia": None
                    }
                ]
            }
        ]
    }

                results.append(case_data)
                print(f"Processo {i} coletado com sucesso.")
            except Exception as e:
                print(f"Erro ao coletar dados da linha {i}: {e}")
        return results

    except Exception as e:
        print(f"Erro ao coletar dados da tabela: {e}")
        return []


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
        while page <= 10:
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
