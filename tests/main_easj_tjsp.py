import json
from funcs.fomarter import extract_case_data
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from funcs import (
    preprocess_text, is_company_name,
    clean_company_name, group_similar,
)

def process_party_names(names, is_company=False):
    """
    Processa nomes de partes com limpeza e agrupamento.
    """
    if not names:
        return names

    clean_names = []
    for name in names:
        if is_company and is_company_name(name):
            clean_names.append(clean_company_name(name))
        else:
            clean_names.append(preprocess_text(name, rem_accents=True))

    grouped_names = group_similar(
        clean_names,
        lambda x: preprocess_text(x, text_only=True),
        clean_cache_thresh=100
    )
    
    return list(grouped_names.values())


if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    try:
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
        except Exception as e:
            print(f"Erro ao salvar dados: {str(e)}")

    finally:
        driver.quit()

