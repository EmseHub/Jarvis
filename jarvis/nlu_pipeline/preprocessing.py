import re
import string

from nltk.tokenize import word_tokenize
from spylls.hunspell import Dictionary
from HanTa import HanoverTagger as hanta

from helpers.helpers import parse_json_file


# Bekannte Begriffe, die aus Performanzgründen von der Rechtschreibkorrektur ausgenommen werden sollen
words_not_to_correct = ["Muggel"]
intents = parse_json_file("jarvis/nlu_pipeline/intents.json")
patterns = [pattern for intent in intents for pattern in intent.get("patterns")]
words_not_to_correct += patterns

# Maximal zulässige Wortlänge, ab deren Überschreitung Begriffe aus Performanzgründen von der Rechtschreibkorrektur ausgenommen werden
max_wordlength_to_correct = 15

# Spylls mit Modell initialisieren
spylls_dictionary = Dictionary.from_files("jarvis/nlu_pipeline/additional_dictionaries/de_DE")

# HanoverTagger mit Modell initialisieren
hanover_tagger = hanta.HanoverTagger("morphmodel_ger.pgz")


def autocorrect_word(word):
    # Prüfen, ob Wort bekannt/im Wörterbuch vorhanden, wenn nicht, ersten Vorschlag zurückgeben
    if spylls_dictionary.lookup(word) == False:
        for suggestion in spylls_dictionary.suggest(word):
            return suggestion if suggestion else word
    return word


def get_tagged_tokens(text_raw):

    language = "german"

    # Mehrfache Leerzeichen, Tabs und Zeilenumbrüche mit RegEx auf ein Leerzeichen reduzieren
    clean_text = re.sub(r"\s+", " ", text_raw)

    # Tokenization auf Wort-Ebene
    tokens_original = word_tokenize(clean_text, language)

    # Satzzeichen entfernen
    tokens_original = [token for token in tokens_original if token not in string.punctuation]

    # Tokens, die eine Mindestanzahl an Zeichen unterschreiten, entfernen [aktuell genügt ein Zeichen]
    tokens_original = [token for token in tokens_original if len(token) > 0]

    # Rechtschreibkorrektur
    tokens_corrected = [
        (
            token
            if (
                (re.search(r"[^A-ZÄÖÜa-zäöüß]", token))
                or (len(token) > max_wordlength_to_correct)
                or (token in words_not_to_correct)
            )
            else autocorrect_word(token)
        )
        for token in tokens_original
    ]

    # Part-of-Speech-Tagging und Lemmatisierung

    # ---Hanover Tagger---
    # Deutsch, Niederländisch und Englisch
    # https://github.com/wartaal/HanTa
    # https://github.com/wartaal/HanTa/blob/master/Demo.ipynb --> Doku
    # https://textmining.wp.hs-hannover.de/Preprocessing.html#Lemmatisierung-und-Wortarterkennung
    # POS-Tags auflisten:
    #   hanover_tagger.list_postags()
    #   hanover_tagger.list_mtags()
    # HanTa-Tags entsprechen dem Stuttgart-Tübingen-Tagset (STTS)
    # https://www.ims.uni-stuttgart.de/forschung/ressourcen/lexika/germantagsets/#id-cfcbf0a7-0
    # https://homepage.ruhr-uni-bochum.de/stephen.berman/Korpuslinguistik/Tagsets-STTS.html
    # https://www.ims.uni-stuttgart.de/documents/ressourcen/korpora/tiger-corpus/annotation/tiger_scheme-morph.pdf (S. 26/27)

    taglevel = 1  # Default ist 1
    casesensitive = True  # Default ist True
    tokens_hannover_tagged = hanover_tagger.tag_sent(tokens_corrected, taglevel, casesensitive)

    # ---Weitere Optionen---
    # "Pattern" Library des CLiPS Research Center
    # https://datascience.blog.wzb.eu/2016/07/13/accurate-part-of-speech-tagging-of-german-texts-with-nltk/

    # Tags je Token zusammenführen und als Liste ausgeben
    result_tagged_tokens = [
        {
            "original": tokens_original[i],
            "korrigiert": tokens_corrected[i],
            "lemma": tokens_hannover_tagged[i][1],
            "pos": tokens_hannover_tagged[i][2],
        }
        for i in range(len(tokens_original))
    ]

    return result_tagged_tokens
