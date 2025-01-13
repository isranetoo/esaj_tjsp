import re
from unidecode import unidecode
from utils.text import specialpunct, strip_accents


def is_company_name(name, preset_companies: list = None):
    if preset_companies is None:
        preset_companies = []

    keywords = ["ltda", "ltda.", "s/a", "s.a.", "sa", "inc", "group", "agencia", "companhia", "corporation",
                "viagens", "turismo", "transportes", "transporte", "comércio", "serviços", "seguros",
                "linhas", "lineas", "aereas", "aéreas", "aereos", "aéreos", "aerea", "aérea", "aereo", "aéreo",
                "airlines", "airways", "aerovias", "air", "aviação", "aviación"]

    for keyword in (keywords + preset_companies):
        if f"{keyword}" in name.split(" "):
            return True
    return False


def clean_company_name(company_name):
    trashs = {r"ltda\.": "", "ltda": "", "s/a": "", r"s\.a\.": "", r"\bsa\b": "", "epp": ""}
    for trash, new in trashs.items():
        company_name = re.sub(trash, new, company_name)

    company_name = re.sub(specialpunct, "", company_name)
    company_name = strip_accents(company_name)

    return re.sub(" +", " ", company_name).strip()


def apply_name_convertion(raw_name, trad):
    names, new_name = raw_name.split("', '"), []
    for name in names:
        name = name.strip("' ")
        if name != name or len(name) <= 1:
            new_name.append(name)
        elif name in trad:
            new_name.append(trad[name])
        else:
            new_name.append("person")

    f_rq = str(list(set(new_name))).strip("[] ")
    return f_rq if f_rq != "'person'" or len(new_name) == 1 else "'people'"
