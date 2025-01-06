import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json

def save_session_data(driver, session_file="session_data.json"):
    """Salva os dados da sessão (cookies e local storage)"""
    try:
        cookies = driver.get_cookies()
        local_storage = driver.execute_script("return window.localStorage;")
        session_data = {
            "cookies": cookies,
            "localStorage": local_storage,
        }
        with open(session_file, "w", encoding="utf-8") as file:
            json.dump(session_data, file, ensure_ascii=False, indent=4)
        print(f"Dados da sessão salvos em '{session_file}'.")
    except Exception as e:
        print(f"Erro ao salvar os dados da sessão: {e}")

def load_session_data(driver, session_file="session_data.json"):
    """Carrega os dados da sessão (cookies e local storage)"""
    try:
        with open(session_file, "r", encoding="utf-8") as file:
            session_data = json.load(file)

        driver.get("https://esaj.tjsp.jus.br/cjsg/resultadoCompleta.do")

        for cookie in session_data.get("cookies", []):
            driver.add_cookie(cookie)

        for key, value in session_data.get("localStorage", {}).items():
            driver.execute_script(f"window.localStorage.setItem('{key}', '{value}');")

        print(f"Dados da sessão carregados de '{session_file}'.")
        return True
    except FileNotFoundError:
        print(f"Arquivo '{session_file}' não encontrado. Iniciando sem sessão anterior.")
        return False
    except Exception as e:
        print(f"Erro ao carregar os dados da sessão: {e}")
        return False

def download_pdf(cdacordao):
    """Baixa o PDF com base no cdacordao"""
    url = f"https://esaj.tjsp.jus.br/cjsg/getArquivo.do?cdAcordao={cdacordao}&cdForo=0"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(f"processo_{cdacordao}.pdf", 'wb') as f:
                f.write(response.content)
            print(f"PDF {cdacordao} baixado com sucesso.")
        else:
            print(f"Erro ao baixar o PDF para {cdacordao}. Status: {response.status_code}")
    except Exception as e:
        print(f"Erro ao tentar baixar o PDF {cdacordao}: {e}")

def extract_case_data(driver):
    """Coleta os dados da página de processos"""
    results = []
    rows_xpath = "//body/table[1]/tbody/tr"

    try:
        rows = driver.find_elements(By.XPATH, rows_xpath)
        for i, row in enumerate(rows, start=1):
            try:
                case_data = {                             
                    "numero":  row.find_element(By.XPATH, f"td[2]/table/tbody/tr[1]/td/a[1]").text,
                    "valorDaCausa": None,
                    "area_code": None,
                    "tribunal_code": None,
                    "vara_code": None,
                    "area": None,
                    "tribunal": "TJ-SP",
                    "comarca":  remove_prefix(row.find_element(By.XPATH, f"td[2]/table/tbody/tr[4]/td").text,
                            "Comarca: "      
                        ),
                    "instancias": [{
                        "fonte_script": "Scrapper",
                        "fonte_sistema": "TJ-SP",
                        "fonte_tipo": "TRIBUNAL",
                        "fonte_url": "https://esaj.tjsp.jus.br/",

                        "grau": None,
                        "classe": None,
                        "orgaoJulgador": remove_prefix(row.find_element(By.XPATH, f"td[2]/table/tbody/tr[5]/td").text,
                          "Órgão julgador: "             
                        ),

                        "segredoJustica": None,
                        "justicaGratuita": None,

                        "assunto_principal": None,
                        "assuntos": remove_prefix(row.find_element(By.XPATH, f"td[2]/table/tbody/tr[2]/td").text, 
                            "Classe/Assunto: "
                        ),

                        "first_mov": None,
                        "last_mov": remove_prefix(row.find_element(By.XPATH, f"td[2]/table/tbody/tr[7]/td").text,
                          "Data de publicação: "              
                        ),
                         "envolvidos": [
                    {
                        "nome": None,
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
                        "nome":  remove_prefix(row.find_element(By.XPATH, f"td[2]/table/tbody/tr[3]/td").text,
                            "Relator(a): "
                        ),
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

                
                links = row.find_elements(By.XPATH, f"td[2]/table/tbody/tr[1]/td/a")
                for link in links:
                    cdacordao = link.get_attribute("cdacordao")
                    if cdacordao:
                        download_pdf(cdacordao)

                results.append(case_data)
                print(f"Processo {i} coletado com sucesso.")
            except Exception as e:
                print(f"Erro ao coletar dados da linha {i}: {e}")
        return results
    except Exception as e:
        print(f"Erro ao coletar dados da tabela: {e}")
        return []

def remove_prefix(text, prefix):
    """Remove o prefixo especificado do texto, se presente"""
    if text and text.startswith(prefix):
        return text.replace(prefix, "").strip()
    return text

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
        while page <= 2:
            print(f"Acessando página {page}")
            driver.get(base_url.format(page))

            case_data = extract_case_data(driver)
            all_case_data.extend(case_data)

            page += 1

        with open("processos.json", "w", encoding="utf-8") as file:
            json.dump(all_case_data, file, ensure_ascii=False, indent=4)

        print("Dados de todos os processos salvos no arquivo 'processos.json'.")
        save_session_data(driver)

    finally:
        driver.quit()
