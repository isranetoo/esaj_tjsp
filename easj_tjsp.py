import requests

URL_BASE = "https://esaj.tjsp.jus.br/cjsg/captchaControleAcesso.do"


def fetch_urls():
    response_captcha = None 
    try:
        response = requests.get(URL_BASE)

        if URL_BASE == "https://esaj.tjsp.jus.br/cjsg/captchaControleAcesso.do":
            response_captcha = response  
        print(f"URL: {URL_BASE}\nStatus Code: {response.status_code}\n")
        print("Response Content:")
        print(response.text[:500])
        print("-" * 80)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching {URL_BASE}: {e}\n")
    return response_captcha

def send_payload(response_captcha):
    if response_captcha is None:
        print("Captcha response is missing. Cannot proceed with payload.")
        return

    url = "https://esaj.tjsp.jus.br/cjsg/resultadoCompleta.do"
    payload = {
        "conversationId": "",
        "dados.buscaInteiroTeor": "arroz",
        "dados.pesquisarComSinonimos": "S",
        "dados.buscaEmenta": "",
        "dados.nuProcOrigem": "",
        "dados.nuRegistro": "",
        "agenteSelectedEntitiesList": "",
        "contadoragente": "0",
        "contadorMaioragente": "0",
        "codigoCr": "",
        "codigoTr": "",
        "nmAgente": "",
        "juizProlatorSelectedEntitiesList": "",
        "contadorjuizProlator": "0",
        "contadorMaiorjuizProlator": "0",
        "codigoJuizCr": "",
        "codigoJuizTr": "",
        "nmJuiz": "",
        "classesTreeSelection.values": "",
        "classesTreeSelection.text": "",
        "assuntosTreeSelection.values": "",
        "assuntosTreeSelection.text": "",
        "comarcaSelectedEntitiesList": "",
        "contadorcomarca": "0",
        "contadorMaiorcomarca": "0",
        "cdComarca": "",
        "nmComarca": "",
        "secoesTreeSelection.values": "",
        "secoesTreeSelection.text": "",
        "dados.dtJulgamentoInicio": "",
        "dados.dtJulgamentoFim": "",
        "dados.dtPublicacaoInicio": "",
        "dados.dtPublicacaoFim": "",
        "dados.origensSelecionadas": "T",
        "tipoDecisaoSelecionados": "A",
        "dados.ordenarPor": "dtPublicacao",
        "recaptcha_response_token": "03AFcWeA757swfsekzjAtv5D-iFzimn6LZcf86gNUZNcg6Zz_4T-fq0MM3SOmIME6e-ao5OkAdz5iG94wpze1qwWH9Muor_7NUyXFJdkIOwLGN9Z-ChvpseNevi5ae0SDQ6a5M5Q36fEi_ukCelMkH6lm4nNSbe3TRJXBE8q4WbTOEY8Hra_vi0Bt2Ac8pLiAF0mhs3Hl5z5ECGOTG3Hi2HpsYPuHp56xVgpCjFS9TxsizRAPvjuqBf9y6wc4IpU4Zb6UX1cDJ8iDVvnfnUazxNw33qZR7EmjsgvElND5cONXS7yRSbYo5Tj4mZ37xckW3s2mv1swV4BYdr1EQeSKznyGLHhbKTl2DdCClg5mR9vq4gjeqzwACL9htuldGvSHbEoLhMwPe1lJnTmbQADY5h8mlLSQdCHDlncoFgAHc5LSXskWENVvSZTxydpY-UU91Vujx6sjVcCCMpyTuJrphbXfkbyxCrCjPyEDkA3rVSZG6lsQBJJccqKemUa5iccC9cy8d3AEmyJenEFeTckkuMgWBlDN1EkvC4MPbZ6tckZ8kvSMe2Ltvp8JIx1BaQzDiQJeOyTAsxsQroomijfaSOEEptDPiof2viqGmCnNSXWBTTWePXV5yAQ1lJNwwn9tmJyKYknJTjbc9a1dkPFmJk32OIYpd23jAOfzIUhy0c-MxHQMyGaY5J8YvKOsxS4s_mo18ZfDiFzRAt3ACylyJzu5BYeKVlsm3bAqtliXQR-VP1tqIKPCip5fO54SbdzwOWTHn0dSLmn_9ZY1ySjcRRYhI6Rz2SZYji2dHJlqxv2LwlObFyr_pozhcqBpsHZDvakbfgGFq52mOlXc8y5YE5HSyiOqlhhFmySkB-twJDvtCYJx-p2Fg8KOfzXNUJ-PZ5fWIfvyuefgQbZco0sejHzuL4xUU9I8aZA",
        "uuidCaptcha": response_captcha.text
    }

    try:
        response = requests.post(url, data=payload)
        print("Payload Sent. Response Status Code:", response.status_code)
        print("Response Content:")
        print(response.text[:500])
    except requests.exceptions.RequestException as e:
        print("An error occurred while sending the payload:", e)

if __name__ == "__main__":
    response_captcha = fetch_urls()
    if response_captcha:
        send_payload(response_captcha)
