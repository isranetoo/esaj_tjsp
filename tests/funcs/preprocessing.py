import re
import pandas as pd
import nltk
from nltk.corpus import stopwords

from funcs.text import (
    act_letters, act_lwr_letters, act_upr_letters,
    add_before, add_between,
    fix_dates, strip_accents, fix_words_separation, fix_punct_separation
)


def ensure_nltk_resources():
    """Ensure required NLTK resources are downloaded."""
    try:
        stopwords.words('portuguese')
    except LookupError:
        nltk.download('stopwords')


# Call this at module level to ensure resources are available
ensure_nltk_resources()


def filter_text(text, abrevs: dict = {}, trashs: dict = {}):
    # Replaces trash
    for trash_from, trash_to in trashs.items():
        text = re.sub(trash_from, trash_to, text)

    # Tries to fix dates that are separated with '.'
    text = re.sub(r"(\d\d)\.(\d\d)\.(\d\d\d\d)", lambda x : f"{x.group(1)}/{x.group(2)}/{x.group(3)}", text)
    text = fix_dates(text)

    # Remove thousands separator
    text = re.sub(r"[\.]([0-9]+)", lambda x : add_before(x, ""), text)

    # Corrects Excepions to /n rule
    text = re.sub(r"(\d)\. ", lambda x : add_before(x, ""), text)
    text = re.sub(r"S\.A", "s/a", text)
    text = re.sub(r"S\.A", "s/a", text)

    # Add Space Between period and capitals
    text = re.sub(f"([a-z0-9]{act_lwr_letters})([A-Z{act_upr_letters}])", lambda x : add_between(x, "\n"), text)
    text = re.sub(r"([\.])([A-Z" + act_upr_letters + "])", lambda x : add_between(x, " "), text)

    # lowers text
    text = text.lower()

    # Fixes other spaces
    text = fix_words_separation(text)
    text = fix_punct_separation(text)

    # Replaces abreviations
    for abrev_from, abrev_to in abrevs.items():
        text = re.sub(abrev_from, abrev_to, text)

    # Adds new, correct /n in text
    text = re.sub(r"\.+", r"\.", text)
    text = re.sub(r"\. ", r"\.\n", text)

    # Removes hiperlinks from text
    text = re.sub(r"http[^\s]+", "", text)

    # Removes double spaces
    text = re.sub("\\xa0", " ", text)
    text = re.sub(" +", " ", text)
    text = re.sub("(\\n)+", "\n", text)
    text = re.sub("\\n +", "\n", text)

    return text.strip()


def preprocess_text(text, text_language: str = "portuguese", tokenize: bool = False,
                    text_only: bool = False, rem_stopwords: bool = True, other_stopwords: list[str] = None,
                    rem_small_words: int = -1, rep_dates: bool = True, rep_digits: bool = True, rem_simbols: bool = True,
                    rem_punct: bool = True, rem_links: bool = True, rem_email: bool = True, rem_accents: bool = False):
    """  Funcion to filter a single text according to preprocess object filter_flags

    args:
        text: text to filter

    returns:
        filtered text
    """
    if other_stopwords is None:
        other_stopwords = []

    # Retira caracteres obrigatórios
    text = re.sub(r"\n", " ", text, flags=re.DOTALL|re.MULTILINE)

    # Retira acentos
    if rem_accents:
        text = strip_accents(text)

    # Retira caracteres opcionais
    if(text_only):
        text = re.sub(r"[^a-zA-Z0-9 " + act_letters + r"]", "", text, flags=re.DOTALL|re.MULTILINE)
    else:
        if rep_dates:
            text = re.sub(r"\d\d\/\d\d\/\d\d\d\d", " date ", text, flags=re.DOTALL|re.MULTILINE)

        if rep_digits:
            text = re.sub(r"\d[\d\.\/]+", " num ", text, flags=re.DOTALL|re.MULTILINE)
            text = re.sub(r"\d+", " num ", text, flags=re.DOTALL|re.MULTILINE)
            text = re.sub(r"(num)+", " num ", text, flags=re.DOTALL|re.MULTILINE)

        if rem_links:
            text = re.sub(r"http\S+", " url ", text, flags=re.DOTALL|re.MULTILINE)

        if rem_email:
            text = re.sub(r"\S*@\S*\s?", " url ", text, flags=re.DOTALL|re.MULTILINE)

        if rem_simbols:
            text = re.sub(r"[§°ªº$%^&*/@#]+", " ", text, flags=re.DOTALL|re.MULTILINE)

        if rem_punct:
            text = re.sub(r"[\|\\!?\[\]\{\}\(\);:.,'\–\-\+\_\"\…\“\”]", " ", text, flags=re.DOTALL|re.MULTILINE)

    # tokeniza o texto
    text = re.sub(" +", " ", text)
    text = text.lower().split(" ")

    # Removes small words
    if rem_small_words > 0:
        text = list(filter(lambda x: len(x) > rem_small_words, text))

    # Remove stopwords
    to_remove = [""] + other_stopwords
    if rem_stopwords:
        to_remove += stopwords.words(text_language)

    for word in to_remove:
        while word in text:
            text.remove(word)

    # Se não for para tokenizar junta o texto
    if not tokenize:
        text = " ".join(text)

    return text


def search_header_footer(pages, words: int = 50, tol: float = 0.75) -> tuple[list, list]:
    """ Tries to find headers and footers by looking for patterns in the
        beggining and end of each page

    Args:
        pages: list of text of each page
        words: how many words to look at in the beggining and end of the page
        tol: how many pages each word must appear in to be considered a header/footer

    Return:
        list of headers and list footers
    """
    tol = max(tol * len(pages), 1)

    headers, footers = [], []
    for page in pages:
        if page == "":
            continue
        page_words = page.strip().split(" ")
        headers.append(page_words[:words])
        footers.append(page_words[-words:])

    def extract_sentences(word_matrix):
        df = pd.DataFrame(word_matrix)
        df = df.loc[:, df.apply(lambda x: x.value_counts().max() > tol)]
        if df.empty:
            return []

        mode = df.mode(axis=0).iloc[0]
        sentences, last_sentence, last_index = [], "", mode.index[0]
        for index, word in mode.items():
            if index > (last_index + 1):
                sentences.append(last_sentence)
                last_sentence = ""
            last_sentence += " " + word
            last_index = index
        sentences.append(last_sentence.strip())

        return sentences

    return extract_sentences(headers), extract_sentences(footers)
