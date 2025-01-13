
import re
import os

import PyPDF2

from scrappers.utils.text import abreviations
from scrappers.tjsp_esaj.funcs import search_header_footer, filter_text, preprocess_text


input_path = "./Transporte Aereo - Petições/"
raw_path = "./Transporte Aereo - Petições Cru/"
filtered_path = "./Transporte Aereo - Petições Filtrado/"
preprocess_path = "./Transporte Aereo - Petições Pre Processado/"
required_comps = [f for f in os.listdir(input_path) if "." not in f]


trashs = {
    "Este documento é cópia .+? sob o número [0-9]+?\.": "",
    "Para conferir o original, .+? e código [0-9A-Z]+?\.": "",
    "fls\. \d+": " ", " \-se": "\-se", "€":" "
}

errors = {}
for comp in required_comps:
    if not os.path.isdir(f"{raw_path}/{comp}"):
        os.mkdir(f"{raw_path}/{comp}")
    if not os.path.isdir(f"{filtered_path}/{comp}"):
        os.mkdir(f"{filtered_path}/{comp}")
    if not os.path.isdir(f"{preprocess_path}/{comp}"):
        os.mkdir(f"{preprocess_path}/{comp}")

    for doc in os.listdir(f"{input_path}/{comp}"):
        if os.path.isfile(f"{raw_path}/{comp}/{doc.replace('pdf', 'txt')}"):
            pass

        # -------------- Reads PDF -------------------
        with open(f"{input_path}/{comp}/{doc}", "rb") as pdf_file:
            pdf_reader = PyPDF2.PdfFileReader(pdf_file, strict=False)
            num_pages = pdf_reader.numPages

            count, text = 0, ""
            while count < num_pages:
                text += pdf_reader.getPage(count).extractText() + "separaçãopagina"
                count += 1

        # -------------- Pre Filters Text -------------------
        # Make sure text is utc
        text = re.sub("\xa0", " ", text.encode('utf-8','ignore').decode("utf-8"))

        # Removes wrong /n from text
        text = re.sub("\\n", " ", text)
        text = re.sub(" +", " ", text)

        # Removes trash from data
        ftext = filter_text(text, abrevs=abreviations, trashs=trashs)

        # Removes header / footer
        headers, footers = search_header_footer(ftext.split("separaçãopagina"), tol=0.75)
        for rep in headers + footers:
            ftext = re.sub(re.escape(rep), " ", ftext)
        ftext = re.sub("separaçãopagina", " ", ftext)
        ftext = re.sub(" +", " ", ftext)

        # Removes stopwords, characters, punctuation and other stuff from data
        ptext = preprocess_text(ftext, rem_small_words=1)
        ptext = re.sub(" +", " ", ptext)

        with open(f"{raw_path}/{comp}/{doc.replace('pdf', 'txt')}", "w", encoding="utf-8") as file:
            file.write(text)
        with open(f"{filtered_path}/{comp}/{doc.replace('pdf', 'txt')}", "w", encoding="utf-8") as file:
            file.write(ftext)
        with open(f"{preprocess_path}/{comp}/{doc.replace('pdf', 'txt')}", "w", encoding="utf-8") as file:
            file.write(ptext)

        print(f"Done {doc}")
