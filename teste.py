import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

def manage_session_and_search(driver, session_file="session_data.json"):
    """
    Gerencia a sessão do navegador (carregando ou salvando) e realiza a busca.
    """
    try:
        with open(session_file, "r", encoding="utf-8") as file:
            session_data = json.load(file)

        driver.get("https://esaj.tjsp.jus.br")  

        for cookie in session_data.get("cookies", []):
            if "domain" in cookie and not cookie["domain"].startswith("."):
                cookie["domain"] = f".{cookie['domain']}"  
            driver.add_cookie(cookie)

        for key, value in session_data.get("localStorage", {}).items():
            driver.execute_script(f"window.localStorage.setItem('{key}', '{value}');")

        print(f"Dados da sessão carregados de '{session_file}'.")
    except FileNotFoundError:
        print(f"Arquivo '{session_file}' não encontrado. Iniciando sem sessão anterior.")
    except Exception as e:
        print(f"Erro ao carregar os dados da sessão: {e}")

    try:
        url = "https://esaj.tjsp.jus.br/cjsg/resultadoCompleta.do"
        driver.get(url)
        time.sleep(2)

        search_input = driver.find_element(By.XPATH, '//*[@id="iddados.buscaInteiroTeor"]')
        search_input.send_keys("itau")
        search_input.send_keys(Keys.RETURN)
        print("Busca realizada com sucesso.")
    except Exception as e:
        print(f"Erro durante a busca: {e}")

    
    try:
        cookies = driver.get_cookies()
        current_url = driver.current_url
        domain = current_url.split("//")[1].split("/")[0] 
        valid_cookies = [cookie for cookie in cookies if domain in cookie.get("domain", "")]

        local_storage = driver.execute_script("return window.localStorage;")
        session_data = {
            "cookies": valid_cookies,
            "localStorage": local_storage,
        }

        with open(session_file, "w", encoding="utf-8") as file:
            json.dump(session_data, file, ensure_ascii=False, indent=4)

        print(f"Dados da sessão salvos em {session_file}.")
    except Exception as e:
        print(f"Erro ao salvar os dados da sessão: {e}")

if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        manage_session_and_search(driver)
    finally:
        driver.quit()
