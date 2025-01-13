
import os
import re

import pandas as pd
from bs4 import BeautifulSoup

html_path = ".\\inputs\\Montadoras_1\\"
htmls = os.listdir(html_path)

out_path = ".\\outputs\\Montadoras_1\\"

if not os.path.exists(out_path):
    os.mkdir(out_path)

keywords_1st = {
    "sentence": ["sentença proferida", "sentença completa",
                 "julgad[oa] procedente", "julgad[oa] improcedente",
                 "julgad[oa] virtualmente",
                 "trânsito em julgado"],
    "1st_acordo_done": ["(?:homologo|homologação).+(?:acordo|transação)"],
    "1st_obrigacao_done": ["pedido de expedição de mandado", "mandado de levantamento juntado"],
    "1st_seguro_prestamista": ["seguro prestamista"],
    "1st_extinto": ["arquivado definitivamente", "julgo extinto", "artigo 924.{0,2}inciso ii"]
}

keywords_2nd = {
    "2nd_acordo_done": ["(?:homologo|homologação).+(?:acordo|transação)"],
    "2nd_obrigacao_done": ["pedido de expedição de mandado", "mandado de levantamento juntado"],
    "2nd_seguro_prestamista": ["seguro prestamista"],
    "2nd_extinto": ["arquivado definitivamente", "julgo extinto", "artigo 924.{0,2}inciso ii"]
}

todo = {
    "1st": [[html for html in htmls if "1st" in html], keywords_1st],
    "2nd": [[html for html in htmls if "2nd" in html], keywords_2nd]
}

for inst, (htmls_inst, keywords_inst) in todo.items():
    data = {}
    for html_name in htmls_inst:
        # Loads documents
        with open(html_path + html_name, "r", encoding='utf-8') as file:
            html_doc = "".join(file.readlines())

        soup = BeautifulSoup(html_doc, 'html.parser')

        # Look for all mov classes
        if inst == "1st":
            mov_dates = pd.Series(soup.find_all("td", {"class": "dataMovimentacao"}), dtype="object")
            mov_contn = pd.Series(soup.find_all("td", {"class": "descricaoMovimentacao"}), dtype="object")
        elif inst == "2nd":
            mov_dates = pd.Series(soup.find_all("td", {"class": "dataMovimentacaoProcesso"}), dtype="object")
            mov_contn = pd.Series(soup.find_all("td", {"class": "descricaoMovimentacaoProcesso"}), dtype="object")
        else:
            raise ValueError(f"Unkown instance {inst}")

        if len(mov_dates) == 0:
            print(f"No movs found in html for {html_name}")
            continue
        if len(mov_dates) != len(mov_contn):
            print(f"Different number of dates and movs for {html_name}")
            continue
        html_data = {}

        # Create mov dataframe
        movs = {"date": [], "name": [], "desc": []}
        for date, descr in zip(mov_dates, mov_contn):
            descr = re.sub("\n+", " | ", descr.get_text().replace("\t", "")).strip(" |")
            descr = re.sub(" +", " ", descr)

            movs['date'].append(re.sub("\n+", " | ", date.get_text().replace("\t", ". ")).strip(" |."))
            movs['name'].append(descr.split(" | ")[0])
            movs['desc'].append(". ".join(descr.split(" | ")[1:]))

        movs = pd.DataFrame(movs)
        movs["date"] = pd.to_datetime(movs["date"], format="%d/%m/%Y")
        movs = movs[movs["date"] > '2000-01-01']

        # Look for first mov
        start = movs.iloc[-1].to_dict()
        html_data["start_date"] = start["date"]
        html_data["start_name"] = start["name"]
        html_data["start_desc"] = start["desc"]

        # Look for last mov
        finish = movs.iloc[0].to_dict()
        html_data["last_date"] = finish["date"]
        html_data["last_name"] = finish["name"]
        html_data["last_desc"] = finish["desc"]

        # Look for specific keywords
        for cat, keywords in keywords_inst.items():
            for key in keywords:
                cat_movs = movs[movs["name"].str.lower().str.contains(key)]
                if not cat_movs.empty:
                    cat_mov = cat_movs.iloc[-1].to_dict()
                    html_data[f"{cat}_date"] = cat_mov["date"]
                    html_data[f"{cat}_name"] = cat_mov["name"]
                    html_data[f"{cat}_desc"] = cat_mov["desc"]
                    break
            else:
                html_data[f"{cat}_date"] = "Not Found"
                html_data[f"{cat}_name"] = "Not Found"
                html_data[f"{cat}_desc"] = "Not Found"

        data[html_name.split("_")[0]] = html_data

    data = pd.DataFrame.from_dict(data, orient="index")
    data.rename_axis('processo').reset_index().to_csv(f"{out_path}movidata_{inst}.csv", encoding='utf-8')
