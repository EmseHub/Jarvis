import re

from helpers.helpers import get_random_item_in_list, replace_diacritics
from tasks.entity_detection import detect_sth_in_text
from tasks import agents


def do_sth(state_running_task, message_processed, intent_tag):

    if not state_running_task or not message_processed or not intent_tag:
        return {"state_running_task": state_running_task, "response": None}

    if intent_tag == "ablehnung":
        return {"state_running_task": None, "response": "Ich breche die Aufgabe ab."}

    # String mit Rückfragen bei unvollständigen Angaben
    query = ""

    # Nachverfolgen, ob schon vor dieser Nachricht alle Daten vorlagen und es sich um eine Besätigung handeln kann
    is_confirmation_possible = True

    # Prüfen, ob noch Rückfragen vorliegen, oder alle relevanten Daten vorhanden sind
    if query:
        return {"state_running_task": state_running_task, "response": query}

    # Prüfen, ob mit der aktuellen Nachricht die Bestätigung erteilt wird
    if (not is_confirmation_possible) or (intent_tag != "zustimmung"):
        query = "Nun denn, ich führe den Task aus, okay?"
        return {"state_running_task": state_running_task, "response": query}

    return {"state_running_task": None, "response": "Vielen Dank, der Task wurde ausgeführt."}


def google_information(state_running_task, message_raw, intent_tag):

    search_term = message_raw
    words_to_ignore = ["google", "bitte", "nach"]
    for word_to_ignore in words_to_ignore:
        search_term = re.sub(
            rf"\b{word_to_ignore}\b", "", search_term, count=1, flags=re.IGNORECASE
        )

    # TODO: Falls search_term nur ein Wort enthält, Rückfrage ausgeben, wonach gesucht werden soll

    result = agents.selenium_lib.get_google_answer(search_term)

    return result
