import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


def save_session_data(driver, session_file="session_data.json"):
    """
    Salva os dados da sessão, como cookies e local storage, para reutilização futura.
    """
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


def get_uuidCaptcha_from_payload():
    """
    Realiza uma requisição POST para obter o valor do uuidCaptcha necessário para continuar o processo.
    """
    url = "https://esaj.tjsp.jus.br/cjsg/captchaControleAcesso.do"

    response = requests.post(url)

    if response.status_code == 200:
        if 'uuidCaptcha' in response.text:
            print("uuidCaptcha encontrado:", response.text.split('uuidCaptcha":')[1].split('"')[1])
        else:
            print("uuidCaptcha não encontrado na resposta.")
    else:
        print(f"Erro ao enviar a requisição: {response.status_code}")
        return None


def search_and_collect(driver):
    """
    Realiza a busca e coleta informações organizadas das linhas 1 até 21 da tabela, salvando em JSON.
    """
    url = "https://esaj.tjsp.jus.br/cjsg/resultadoCompleta.do"
    try:
        driver.get(url)
        time.sleep(2)

        search_input = driver.find_element(By.XPATH, '//*[@id="iddados.buscaInteiroTeor"]')
        search_input.send_keys("itau")
        search_input.send_keys(Keys.RETURN)
        print("Busca realizada com sucesso.")
    except Exception as e:
        print(f"Erro durante a busca ou coleta de informações: {e}")


if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        load_session_data(driver)

        get_uuidCaptcha_from_payload()
        search_and_collect(driver)

        save_session_data(driver)
    finally:
        driver.quit()
