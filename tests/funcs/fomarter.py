from selenium.webdriver.common.by import By
from funcs.pdf_utils import download_and_process_pdf
from funcs import (
    convert_partes_proc_1st
)

def remove_prefix(text, prefix):
    """Remove o prefixo especificado do texto, se presente."""
    if text and text.startswith(prefix):
        return text.replace(prefix, "").strip()
    return text


def extract_case_data(driver):
    """Coleta os dados da página de processos com processamento melhorado.""" 
    results = []
    rows_xpath = "//body/table[1]/tbody/tr"

    try:
        rows = driver.find_elements(By.XPATH, rows_xpath)
        if not rows:
            print("Nenhuma linha de processo encontrada na página")
            return []

        for i, row in enumerate(rows, start=1):
            try:
                processo_element = row.find_elements(By.XPATH, "td[2]/table/tbody/tr[1]/td/a[1]")
                if not processo_element:
                    print(f"Processo {i}: Elemento do número do processo não encontrado")
                    continue
                
                links = row.find_elements(By.XPATH, "td[2]/table/tbody/tr[1]/td/a")
                pdf_data = None
                for link in links:
                    try:
                        cdacordao = link.get_attribute("cdacordao")
                        if cdacordao:
                            pdf_data = download_and_process_pdf(cdacordao)
                            if pdf_data:
                                break
                    except Exception as e:
                        print(f"Erro ao processar link do PDF: {e}")
                        continue

                if not pdf_data:
                    print(f"Processo {i}: PDF não encontrado ou não processado")
                    continue

                try:
                    partes_primeira = convert_partes_proc_1st(pdf_data['text'])
                    if (partes_primeira is None or 
                        not all(k in partes_primeira for k in ['rqt', 'rqd', 'adv_rqt', 'adv_rqd'])):
                        print(f"Processo {i}: Dados das partes incompletos")
                        continue

                    nome_parte_ativa = partes_primeira["rqt"].iloc[0] if hasattr(partes_primeira["rqt"], 'iloc') else partes_primeira["rqt"]
                    nome_parte_passiva = partes_primeira["rqd"].iloc[0] if hasattr(partes_primeira["rqd"], 'iloc') else partes_primeira["rqd"]
                    
                except Exception as e:
                    print(f"Erro ao processar partes do processo {i}: {e}")
                    continue

                case_data = {
                    "numero": row.find_element(By.XPATH, f"td[2]/table/tbody/tr[1]/td/a[1]").text,
                    "area_code": None,
                    "tribunal_code": None,
                    "vara_code": None,
                    "ano": None,
                    "area": "Trabalhista",
                    "tribunal": "TJ-SP",
                    "comarca": remove_prefix(row.find_element(By.XPATH, f"td[2]/table/tbody/tr[4]/td").text, "Comarca: "),
                    "valor_da_causa": None,
                    "fontes": [{
                        "provider": "Interno",
                        "script": "Scrapper",
                        "sistema": "TJ-SP",
                        "tipo": "TRIBUNAL",
                        "instancias": [{
                            "url": "https://esaj.tjsp.jus.br/",
                            "grau": None,
                            "classe": None,
                            "orgaoJulgador": remove_prefix(row.find_element(By.XPATH, f"td[2]/table/tbody/tr[5]/td").text, "Órgão julgador: "),
                            "justica_gratuita": None,
                            "assunto_principal": None,
                            "assuntos": remove_prefix(row.find_element(By.XPATH, f"td[2]/table/tbody/tr[2]/td").text, "Classe/Assunto: "),
                            "envolvidos": [
                                {
                                    "nome": nome_parte_ativa,
                                    "tipo": "RECLAMANTE",
                                    "polo": "ATIVO",
                                    "id_sistema": {"login": None},
                                    "documento": [],
                                    "endereco": {},
                                    "representantes": [{
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
                                            "cep": None
                                        }
                                    }]
                                },
                                {
                                    "nome": nome_parte_passiva,
                                    "tipo": "RECLAMADO",
                                    "polo": "PASSIVO",
                                    "id_sistema": {"login": None},
                                    "documento": [],
                                    "endereco": {},
                                    "representantes": [{
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
                                    }]
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
                                    "data": remove_prefix(row.find_element(By.XPATH, f"td[2]/table/tbody/tr[7]/td").text, "Data de publicação: "),
                                    "titulo": "Publicado(a) o(a) intimação em 19/11/2024",
                                    "tipo": None,
                                    "conteudo": "HTML",
                                    "tem_documento": False,
                                    "id_documento": None
                                },
                                {
                                    "data": remove_prefix(row.find_element(By.XPATH, f"td[2]/table/tbody/tr[7]/td").text, "Data de publicação: "),
                                    "titulo": "Juntada a petição de Manifestação",
                                    "tipo": None,
                                    "conteudo": "HTML",
                                    "tem_documento": False,
                                    "id_documento": None
                                },
                                {
                                    "data": remove_prefix(row.find_element(By.XPATH, f"td[2]/table/tbody/tr[7]/td").text, "Data de publicação: "),
                                    "titulo": "Ata da Audiência",
                                    "tipo": "Ata da Audiência",
                                    "conteudo": "PDF",
                                    "tem_documento": True,
                                    "id_documento": None
                                }
                            ]
                        }]
                    }]
                }

                results.append(case_data)
                print(f"Processo {i} coletado com sucesso.")

            except Exception as e:
                print(f"Erro ao coletar dados da linha {i}: {str(e)}")
                continue

        return results

    except Exception as e:
        print(f"Erro ao coletar dados da tabela: {e}")
        return []
