import requests
import json

URL_BASE = "https://esaj.tjsp.jus.br/cjsg/captchaControleAcesso.do"
URL_PAYLOAD = "https://esaj.tjsp.jus.br/cjsg/resultadoCompleta.do"

def fetch_uuid_captcha():
    """  """
    try:
        response = requests.get(URL_BASE)
        response.raise_for_status()
        print(f"URL_BASE status code {response.status_code}")

        if "sajcaptcha_" in response.text:
            start_index = response.text.find("sajcaptcha_")
            end_index = response.text.find('"', start_index)
            uuid_captcha = response.text[start_index:end_index]
        else:
            raise ValueError("uuidCaptcha not found in the response")
        
        with open("uuid_captcha.json", 'w', encoding='utf-8') as json_file:
            json.dump({"uuidCaptcha": uuid_captcha}, json_file, ensure_ascii=False, indent=4)

        print(f"uuidCaptcha extracted and saved: {uuid_captcha}")
        return uuid_captcha
    except requests.exceptions.RequestException as e:
        print(f"An error ocurred while fetchig URL_BASE: {e}")
    except ValueError as ve:
        print(ve)
    return None
    

def send_payload(uuid_captcha):
    """  """
    if not uuid_captcha:
        print("uuidCaptcha is missing, Cannot proceed with payload.")
        return
    
    payload = {
        "conversationId": "",
        "dados.buscaInteiroTeor": "itau",
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
        "recaptcha_response_token": "03AFcWeA61b-PznGxZm0PPnrArU-pHVBbUcv9qHMbsGdC0rqxhBTgl0t12arNHLFwSayOzDRNgm0hYBi2wmNja9kTRX59r6X_FB8GwaM7_106dFsIu5kKIaGpmsg65nvzfkj4JfK3YsGijNmdx6AcJyZZ4TMsDjrMJv5L9HkkKQ4NAnHHpiMHp8Q47ALxx9qftFV6vqyIe0irqkDvnpLne61X4YYrK3mlwIbFFUQj3_4s0oZ8bbY8unYhFEWlNCCO0S6v_mljQgjfdsN-rvrxtZIlkYptI3tpZpDHgO2n21oC1OCcM9rjxVXJ-m88W2nxuuokcxc275gveK1l3bTiIOqwExiYXyktAYklsQ0BSM0vfc8pby3UKPphRIW-7SrXOAvJJwNTuGTOIw4oUbuK8OfY_r8Qfd7B_R20HFtn6eNzL9Sd38wkuDqn8lCkqwLJDmDazwLz6ev_cAW3HuSjtwL4fAAhfcKN2fi07dh7XkwSocrdC8F3KmgNKmnEg8gNNBulSJqIKm3GclWBNRXjxzrhO8iq1uavPpvvICuCCJ1vwwQS9RujIcs97QWULkp2qInTHH0MvBNTign1c-lVoO3C_xdBPnZK_VYrkbK1Hbo3BhzzRWSVGZKpelAwruBlRvRUJSqYbh1AVbQUCIxJ_qhbfNU0LvwsAyBxq8MbLHAslYJF_mYBJouXCY5zFL8BUc0z3AM3rxtks2BWq6tbNYWKwY739bOLxlmwB8q_0-7M0GgQnBQZ6zJJBA0QA7w6URRfnvge9vCcYHsX3GDtNP3_VQqIWypTYMNJU_LqgflaU2yay67lg-JR-uI18HudLfh8SgtOm_Xt6rV9eHFhsnqKWizjDrxuyDMl72DAivzIAb5f4SvpwDiZLYrQ70_LyV3MnUUDdjiM52sZ9grPetBUq-3_QOeeFpQkF11pX7fhyAlJBSvgwPgI",
        "uuidCaptcha": uuid_captcha
    }
    try: 
        response = requests.post(URL_PAYLOAD, data=payload)
        response.raise_for_status()

        content_type = response.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            response_data = response.json()
            with open ("response.json", 'w', encoding='utf-8') as json_file:
                json.dump(response_data, json_file, ensure_ascii=False, indent=4)
            print("Response saved to 'response.json'")
        else:
            with open("response_raw_html.html", 'w', encoding='utf-8') as html_file:
                html_file.write(response.text)
            print("Raw response saved to 'response_raw.html'")
    except requests.exceptions.RequestException as e:
        print(f"An error ocurred while sending the payload: {e}")
    except ValueError as ve:
        print(f"Error while processing the resonse: {ve}")

if __name__ == '__main__':
    uuid_captcha = fetch_uuid_captcha()
    if uuid_captcha:
        send_payload(uuid_captcha)