import re

from helpers.helpers import get_random_item, replace_diacritics


def detect_sth_in_text(tagged_tokens, text_raw):

    result = {"sth": None, "query": ""}

    if not tagged_tokens or not text_raw or not text_raw.strip():
        return result

    # Nachricht bereinigen
    text_processed = text_raw

    # Jeden White Space auf ein Leerzeichen reduzieren
    text_processed = re.sub(r"\s+", " ", text_processed).strip()

    # Wert, der als Nachname in Frage kommt
    sth = None

    # Falls...
    if not sth:
        regex_match = re.search(
            r"\b(ist|lautet|heißt|heisst|heisse|heiße|in|zu|nach)(\s+([A-ZÄÖÜ][a-zäöüß]+(-?))+)+\b", text_processed
        )
        if regex_match:
            regex_match_string = regex_match.group()
            regex_match_splitted = regex_match_string.strip("- ").split()
            sth = (" ").join(regex_match_splitted[1:])

    # Prüfen, ob der gefundene Nachname gültig ist
    if sth and len(sth.strip("- ")) > 1:
        # Satzzeichen entfernen
        sth = re.sub(r"[^A-Za-zÄÖÜäöüß\s-]", "", sth).strip("- ")
        result["sth"] = sth
    else:
        result["query"] = get_random_item(
            [
                "Wie genau lautet Dein neuer Nachname bitte?",
                'Gib Deinen neuen Nachnamen gerne in folgender Form an: "Mein neuer Nachname lautet: Beispielname"',
            ]
        )

    return result
