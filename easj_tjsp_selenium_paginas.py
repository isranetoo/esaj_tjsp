import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def save_session_data(driver, session_file="session_data.json"):
    """
    Salva os dados da sessão, como cookies e local storage, para reutilização futura.
    """
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
    """
    Carrega os dados da sessão a partir de um arquivo JSON e aplica ao navegador.
    """
    try:
        with open(session_file, "r", encoding="utf-8") as file:
            session_data = json.load(file)

        driver.get("https://esaj.tjsp.jus.br")  

        for cookie in session_data.get("cookies", []):
            driver.add_cookie(cookie)

        for key, value in session_data.get("localStorage", {}).items():
            driver.execute_script(f"window.localStorage.setItem('{key}', '{value}');")

        print(f"Dados da sessão carregados de '{session_file}'.")
    except FileNotFoundError:
        print(f"Arquivo '{session_file}' não encontrado. Iniciando sem sessão anterior.")
    except Exception as e:
        print(f"Erro ao carregar os dados da sessão: {e}")

def extract_case_data(driver):
    """
    Coleta os dados da tabela na página e salva em um arquivo JSON.
    """
    results = []
    rows_xpath = "//body/table[1]/tbody/tr"

    try:
        rows = driver.find_elements(By.XPATH, rows_xpath)
        for i, row in enumerate(rows, start=1):
            try:
                case_data = {
                    "numero_processo": row.find_element(By.XPATH, f"td[2]/table/tbody/tr[1]/td/a[1]").text,
                    "classe_assunto": row.find_element(By.XPATH, f"td[2]/table/tbody/tr[2]/td").text,
                    "relator": row.find_element(By.XPATH, f"td[2]/table/tbody/tr[3]/td").text,
                    "comarca": row.find_element(By.XPATH, f"td[2]/table/tbody/tr[4]/td").text,
                    "orgao_julgador": row.find_element(By.XPATH, f"td[2]/table/tbody/tr[5]/td").text,
                    "data_julgamento": row.find_element(By.XPATH, f"td[2]/table/tbody/tr[6]/td").text,
                    "data_publicacao": row.find_element(By.XPATH, f"td[2]/table/tbody/tr[7]/td").text,
                    "ementa": row.find_element(By.XPATH, f"td[2]/table/tbody/tr[8]/td").text,
                }
                results.append(case_data)
                print(f"Processo {i} coletado com sucesso.")
            except Exception as e:
                print(f"Erro ao coletar dados da linha {i}: {e}")

        with open("processos.json", "w", encoding="utf-8") as file:
            json.dump(results, file, ensure_ascii=False, indent=4)

        print("Dados dos processos salvos no arquivo 'processos.json'.")
    except Exception as e:
        print(f"Erro ao coletar dados da tabela: {e}")

if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        load_session_data(driver)

        url = "https://esaj.tjsp.jus.br/cjsg/trocaDePagina.do?tipoDeDecisao=A&pagina=1&conversationId="
        driver.get(url)
        time.sleep(5)  

        extract_case_data(driver)

        save_session_data(driver)
    finally:
        driver.quit()
