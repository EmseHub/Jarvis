import json

from HanTa import HanoverTagger as hanta
from helpers.helpers import parse_json_file, write_json_to_textfile, replace_diacritics


def generate_intents_runtime(intents_with_diacritics):
    """Stellt eine aufbereitete Version der Intents aus der JSON-Datei bereit, bei der die Patterns mit PoS-Tag und Lemma versehen sind. Alle Strings wurden in Lower-Case umgewandelt, und diakritische Zeichen sind umgebrochen.

    Zur Laufzeit einsehbar unter "tmp_intents_runtime.json".
    """

    hanover_tagger = hanta.HanoverTagger("morphmodel_ger.pgz")
    intents_runtime = []

    for intent in intents_with_diacritics:

        taglevel = 1  # Default ist 1
        casesensitive = True  # Default ist True
        patterns_tagged = hanover_tagger.tag_sent(
            intent["patterns"], taglevel, casesensitive
        )

        patterns_tagged = [
            {
                "original_processed": replace_diacritics(pattern_tagged[0]).lower(),
                "lemma_processed": replace_diacritics(pattern_tagged[1]).lower(),
                "pos": pattern_tagged[2]
            }
            for pattern_tagged in patterns_tagged
        ]

        intent_runtime = {**intent, "patterns": patterns_tagged}
        intents_runtime.append(intent_runtime)

    write_json_to_textfile("tmp_intents_runtime.json", intents_runtime)

    return intents_runtime


# Aufbereitete Intents generieren und im Arbeitsspeicher halten
intents_runtime = generate_intents_runtime(
    parse_json_file("jarvis/chatbot/intents.json")
)


def get_intent(tagged_tokens):

    if (not tagged_tokens or len(tagged_tokens) == 0):
        return None

    # Anzahl der Wörter im Text
    total_words = len(tagged_tokens)

    possible_intents = []
    for intent in intents_runtime:
        # Anzhahl der Patterns des Intents, die vom Text getroffen werden
        hit_count = 0

        for pattern in intent["patterns"]:
            # Prüfen, ob ein Original-Wort oder Lemma des Textes zum aktuellen Pattern passt
            for tagged_token in tagged_tokens:
                # Original-Wort und Lemma extrahieren und zum Abgleich ins Format der Patterns umwandeln: Umlaute ersetzen und Lower Case
                original = replace_diacritics(tagged_token["original"].lower())
                lemma = replace_diacritics(tagged_token["lemma"].lower())
                if (pattern["original_processed"] == original or (pattern["lemma_processed"] == lemma and pattern["pos"] == tagged_token["pos"])):
                    # Pattern getroffen
                    hit_count += 1
                    # Ein Pattern soll nur ein Mal vom Text getroffen werden können, daher "break"
                    # Falls etwa "Hilfe, Hilfe, Hilfe" einen HitCount von 3 liefern soll, darf die Schleife hier nicht verlassen werden
                    break

        if hit_count < intent["min_hits"]:
            # Im Intent definiertes Minimum an Treffern nicht erreicht
            continue
        if hit_count >= total_words:
            # Jedes Wort des Textes trifft -> Intent eindeutig
            return {**intent, "hit_count": hit_count}
        if hit_count > 0:
            # Möglicherweise gemeinten Intent zur Liste hinzufügen
            possible_intents.append({**intent, "hit_count": hit_count})

    # Falls kein Intent gefunden wurde, Default-Intent ausgeben
    if len(possible_intents) == 0:
        return {**next(intent for intent in intents_runtime if intent["tag"] == "trefferlos"), "hit_count": 0}

    # Intent mit den meisten Treffern ausgeben
    # print("Mögliche Intents", possible_intents)
    return max(possible_intents, key=lambda intent: intent["hit_count"])
