
import re

import pandas as pd


def convert_valor(x):
    if isinstance(x, str):
        return float(x.replace(".", "").replace(",", ".").replace("R$ ", ""))
    return x


def is_juizado_especial(name):
    keywords = ["juizado especial", "especial"]

    name = name.lower()
    for keyword in keywords:
        if keyword in name:
            return True
    return False


def convert_partes_proc_1st(x):
    default = {"rqt": ["error"], "adv_rqt": ["error"], "rqd": ["error"], "adv_rqd": ["error"]}

    if not isinstance(x, str):
        return pd.Series({k: str(v)[1:-1] for k, v in default.items()})
    else:
        x = x.lower()

    rqt_words = ['reqte', 'autor', 'embargte', 'impugte', 'reprtateat', 'embargda', "reclamante", "liqdteat",
                 'impugdo',  'herdeiro', 'herdeira', 'invtante', "reconvinte", 'exeqte', 'imptte', "alimentado"]
    rqd_words = ['reqda', 'reqdo', "reconvindo", "reclamado", 'imptdo', "reqdo", "exectdo", "liqdtepas"]
    adv_words = ['advogada', 'advogado', 'repreleg']

    trad = {w: "rqt" for w in rqt_words}
    trad.update({w: "rqd" for w in rqd_words})
    trad.update({w: "adv" for w in adv_words})

    pattern = re.compile("(" + "|".join(rqt_words + rqd_words + adv_words) + ")")
    sides = ["rqt", "rqd"]

    result = {"rqt": [], "adv_rqt": [], "rqd": [], "adv_rqd": []}
    last_side, last_cat, last_end = None, None, 0
    try:
        for match in pattern.finditer(x):
            if last_cat is not None:
                last_side = last_cat if last_cat in sides else last_side
                cat = last_side if last_cat in sides else f"{last_cat}_{last_side}"
                result[cat].append(x[last_end: match.start()].strip("-:| "))
            last_cat, last_end = trad[match.group()], match.end()
        if last_cat is not None:
            last_side = last_cat if last_cat in sides else last_side
            cat = last_side if last_cat in sides else f"{last_cat}_{last_side}"
            result[cat].append(x[last_end: -1].strip("|-: "))
    except Exception as e:
        print(f"ERR {e} PARSING: {x}")
        return pd.Series({k: str(v)[1:-1] for k, v in default.items()})
    return pd.Series({k: str(v)[1:-1] for k, v in result.items()})


def convert_partes_proc_2nd(x):
    default = {"outr": ["error"], "adv_outr": ["apdo"],
               "apte": ["error"], "adv_apte": ["apdo"],
               "apdo": ["error"], "adv_apdo": ["error"]}

    if not isinstance(x, str):
        return pd.Series({k: str(v)[1:-1] for k, v in default.items()})
    else:
        x = x.lower()

    skip_words = ["interessada", "interessado"]
    apte_words = ["apelante", "apte/apda", "apte/apdo", "apldo/recte", "agravante", "recorrente",
                  "impetrante", "requerente", "reclamante", "suscitante", "autor", "embargte"]
    apdo_words = ["apelado", "apelada", "agravado", "agravada", "embargdo", "recorrido",
                  "apda/apte", "apdo/apte", "requerido", "reclamado", "suscitado", "réu"]
    adv_words = ['advogada', 'advogado', 'repreleg']

    trad = {w: "outr" for w in skip_words}
    trad.update({w: "apte" for w in apte_words})
    trad.update({w: "apdo" for w in apdo_words})
    trad.update({w: "adv" for w in adv_words})

    pattern = re.compile("(" + "|".join(skip_words + apte_words + apdo_words + adv_words) + ")")
    sides = ["outr", "apte", "apdo"]

    result = {"outr": [], "adv_outr": [], "apte": [], "adv_apte": [], "apdo": [], "adv_apdo": []}
    last_side, last_cat, last_end = None, None, 0
    try:
        for match in pattern.finditer(x):
            if last_cat is not None:
                last_side = last_cat if last_cat in sides else last_side
                cat = last_side if last_cat in sides else f"{last_cat}_{last_side}"
                result[cat].append(x[last_end: match.start()].strip("-:| "))
            last_cat, last_end = trad[match.group()], match.end()
        if last_cat is not None:
            last_side = last_cat if last_cat in sides else last_side
            cat = last_side if last_cat in sides else f"{last_cat}_{last_side}"
            result[cat].append(x[last_end: -1].strip("|-: "))
    except Exception as e:
        print(f"ERR {e} PARSING: {x}")
        return pd.Series({k: str(v)[1:-1] for k, v in default.items()})
    return pd.Series({k: str(v)[1:-1] for k, v in result.items()})
