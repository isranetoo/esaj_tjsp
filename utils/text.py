
import re
import os
import json
from typing import Any

import pandas as pd

import unicodedata
import unidecode


act_lwr_letters = "àèìòùáéíóúýâêîôûãñõäëïöüÿçøåæœ"
act_upr_letters = "ÀÈÌÒÙÁÉÍÓÚÝÂÊÎÔÛÃÑÕÄËÏÖÜŸÇßØÅÆ"
act_letters = act_lwr_letters + act_upr_letters

unc_lwr_letters = "a-z"
unc_upr_letters = "A-Z"
unc_letters = "a-zA-Z"
letters = "a-zA-Z" + act_letters

punct_left = r"\“\(\[\{"
punct_right = r"\”\)\]\}"
punct_gen = r"\!\"\'\,\-\.\:\;\?"
punct = punct_gen + punct_left + punct_right

special = r"\_\#\$\＄\%\&\*\+\-\=\<\>\@\\\/\|\`\^\~"
specialpunct = punct + special


# ============== Loads variables from files ==============
def _get_abreviations() -> dict[str, str]:
    with open(os.path.dirname(__file__) + "\\static\\text\\abreviations.json", "r", encoding='utf-8') as f:
        return json.load(f)

abreviations = _get_abreviations()


def _get_last_letters() -> dict[str, list[str]]:
    with open(os.path.dirname(__file__) + "\\static\\text\\last_letter.json", "r", encoding='utf-8') as f:
        return json.load(f)

last_letter = _get_last_letters()

# ============== Functions for regex ==============
def add_between(match: re.Match, add="\n"):
    """ Adiciona algo entre entro o primeiro e segundo grupo do match

    Args:
        match: regex_match
        add: o que adicionar entre o match

    Returns:
        Texto com o valor adicionado entre os grupos

    Exemple:
        re.sub("([.])([A-Z])", lambda x : add_between(x, " "), text)
        >>> arroz. AQUI Arroz
    """
    return match.group(1) + add + match.group(2)


def add_before(match, add="\n"):
    """ Adiciona algo antes do primeiro grupo do match

    Args:
        match: regex_match
        add: o que adicionar antes o match

    Returns:
        Texto com o valor adicionado antes do grupo

    Exemple:
        re.sub("([.])[A-Z]", lambda x : add_before(x, " "), text)
        >>>  AQUI arroz.Arroz
    """
    return add + match.group(1)


def add_after(match, add="\n"):
    """ Adiciona algo depois do primeiro grupo do match

    Args:
        match: regex_match
        add: o que adicionar depois o match

    Returns:
        Texto com o valor adicionado depois do grupo

    Exemple:
        re.sub("[.]([A-Z])", lambda x : add_before(x, " AQUI "), "arroz.Arroz")
        >>> arroz.Arroz  AQUI
    """
    return match.group(1) + add


# ============== Converts between different types of text  ==============
def to_snake_case(s: str):
    """ Converte string para snake_case

    Args:
        s: string a ser convertido

    Returns:
        string as snake_case
    """
    return '_'.join(re.sub('([A-Z][a-z]+)', r' \1',
                    re.sub('([A-Z]+)', r' \1',
                    s.replace('-', ' '))).split()).lower()


def to_camel_case(s: str):
    """ Converte string para CamelCase

    Args:
        s: string a ser convertido

    Returns:
        string como CamelCase
    """
    s = re.sub(r"(_|-)+", " ", s).title().replace(" ", "")
    return ''.join([s[0].lower(), s[1:]])


# ============== Functions to fix spaces and unicode ==============
def strip_accents(text: str) -> str:
    """ Remove acentos do texto de origem

    Args:
        text: The input string.

    Returns:
        The processed String.
    """
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')


def to_ascii(text: str) -> str:
    """ Converts all text to closest ascii charater

    Args:
        text: The input string.

    Returns:
        The processed String.
    """
    return unidecode(text)


def fix_words_separation(text: str) -> str:
    """ Attempts to fix spaces between words considering the last letter of word
        if the word ends with a non standard consonant like "j" it assumes the next word is still part of it

    Args:
        text: The input string.

    Returns:
        The processed String.
    """
    new_text, next_sep = "", ""
    for word in text.split(" "):
        new_text += next_sep + word
        if word != "" and word[-1] in last_letter:
            ll = last_letter[word[-1]]
            if len(ll) != 0 and (ll[0] == "skip" or word in ll):
                next_sep = " "
            else:
                next_sep = ""
        else:
            next_sep = " "

    return new_text


def fix_punct_separation(text: str) -> str:
    """ Corrige os espaços em torno da pontuação no texto

    Args:
        text: texto a ser corrigido

    Returns:
        texto corrigido
    """
    text = re.sub(fr"({punct_left})\s+", lambda x : f"{x.group(1)}", text)
    text = re.sub(fr"\s+({punct_right})", lambda x : f"{x.group(1)}", text)
    return re.sub(fr"\s+({punct_gen})", lambda x : f"{x.group(1)}", text).replace("\\", "")


def fix_dates(text: str) -> str:
    """ Corrige os espaços e formatação em torno da datas no texto

    Args:
        text: texto a ser corrigido

    Returns:
        texto corrigido
    """
    def regroup_date(x): f" {x.group(1).replace(' ', '')}/{x.group(2).replace(' ', '')}/{x.group(3).replace(' ', '')} "
    return re.sub(r"(\d ?\d ?)\/(\d ?\d ?)\/(\d ?\d ?\d ?\d)", regroup_date, text)


# ============== Functions to search patter in list ==============
def match_list_pattern(list_str: list[str], pattern: str) -> int:
    """ Matches a list of strings for pattern

    Args:
        list_title: list of strings to look at
        pattern: pattern to search for in the list

    Returns:
        Index where pattern starts the string in list
    """
    for i, title in enumerate(list_str):
        if re.match(pattern, title, re.IGNORECASE):
            return i
    return None


def search_list_pattern(list_str: list[str], pattern: str) -> int:
    """ Searches a list of strings for pattern

    Args:
        list_title: list of strings to look at
        pattern: pattern to search for in the list

    Returns:
        Index where pattern is in the string in list
    """
    for i, title in enumerate(list_str):
        if re.search(pattern, title, re.IGNORECASE):
            return i
    return None


def match_series_pattern(series_str: pd.Series, pattern: str) -> tuple[Any, str]:
    """ Matches a series of strings for pattern

    Args:
        series_str: series of strings
        pattern: pattern to search for in the list

    Returns:
        Index where pattern is in the string in list
    """
    for date, title in series_str.items():
        if re.match(pattern, title, re.IGNORECASE):
            return date, title
    return None, None


def search_series_pattern(series_str: pd.Series, pattern: str) -> tuple[Any, str]:
    """ Searches a series of strings for pattern

    Args:
        series_str: series of strings
        pattern: pattern to search for in the list

    Returns:
        Index where pattern is in the string in list
    """
    for date, title in series_str.items():
        if re.search(pattern, title, re.IGNORECASE):
            return date, title
    return None, None


# ======================== Funções para analisar texto ========================
def non_letter_pct(text: str) -> float:
    """ Calcula o percentual do texto que não são letras

    Args:
        text: texto a ser analisado

    Returns:
        Percentual de não letras
    """
    non_letters = len(re.sub(f"[^a-zA-Z0-9 {act_letters}]", "", text))
    total = len(text)
    return total / non_letters - 1 if non_letters != 0 else 0
