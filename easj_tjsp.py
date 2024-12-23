import requests

URL_BASE = "https://esaj.tjsp.jus.br/cjsg/captchaControleAcesso.do"
URL_PAYLOAD = "https://esaj.tjsp.jus.br/cjsg/resultadoCompleta.do"

def fetch_captcha():
    """
    Faz a requisição à URL_BASE e extrai o uuidCaptcha.
    """
    try:
        response = requests.get(URL_BASE)
        response.raise_for_status()

        uuid_captcha = None
        if "sajcaptcha_" in response.text:
            start_index = response.text.find("sajcaptcha_")
            end_index = response.text.find('"', start_index)
            uuid_captcha = response.text[start_index:end_index]

        print(f"uuidCaptcha encontrado: {uuid_captcha}")
        return uuid_captcha
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar o uuidCaptcha: {e}")
        return None

def send_captcha(uuid_captcha):
    """
    Envia o uuidCaptcha para a URL_BASE e verifica a resposta.
    """
    if not uuid_captcha:
        print("uuidCaptcha está vazio. Não é possível continuar.")
        return None

    payload = {"uuidCaptcha": uuid_captcha}

    try:
        response = requests.post(URL_BASE, data=payload)
        response.raise_for_status()

        print("Payload enviado com sucesso para a URL_BASE.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar o payload para a URL_BASE: {e}")
        return None

def fetch_html(uuid_captcha):
    """
    Faz a requisição para a URL_PAYLOAD com o uuidCaptcha e salva a resposta como HTML.
    """
    if not uuid_captcha:
        print("uuidCaptcha está vazio. Não é possível continuar.")
        return

    payload = {"uuidCaptcha": uuid_captcha}

    try:
        response = requests.post(URL_PAYLOAD, data=payload)
        response.raise_for_status()

        with open("resultado.html", "w", encoding="utf-8") as html_file:
            html_file.write(response.text)

        print("HTML salvo com sucesso em 'resultado.html'.")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar o payload para a URL_PAYLOAD: {e}")

if __name__ == "__main__":
    uuid_captcha = fetch_captcha()
    if send_captcha(uuid_captcha):
        fetch_html(uuid_captcha)
