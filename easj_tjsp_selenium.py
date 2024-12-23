from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def search_and_collect(driver):
    """
    Realiza a busca e coleta informações do primeiro resultado.
    """
    url = "https://esaj.tjsp.jus.br/cjsg/resultadoCompleta.do"

    try:
        driver.get(url)
        time.sleep(2)

        search_input = driver.find_element(By.XPATH, '//*[@id="iddados.buscaInteiroTeor"]')
        search_input.send_keys("itau")
        search_input.send_keys(Keys.RETURN)
        print("Busca realizada com sucesso.")

        time.sleep(5)

        result_xpath = '//*[@id="divDadosResultado-A"]/table/tbody/tr[1]'
        result_element = driver.find_element(By.XPATH, result_xpath)

        result_text = result_element.text
        print("Resultado coletado: ")
        print(result_text)
        return result_text
    except Exception as e:
        print(f"Erro ao buscar ou coletar informações: {e}")

if __name__ == '__main__':
    driver = webdriver.Chrome()

    try:
        search_and_collect(driver)
    finally:
        driver.quit()
    