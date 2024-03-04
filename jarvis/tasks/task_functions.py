import re

from helpers.helpers import (
    get_random_item_in_list,
    remove_punctuation,
    remove_words_first_occurances,
    extract_values_in_syntax,
    extract_values_in_multiple_syntaxes,
    replace_diacritics,
)
from tasks.entity_detection import detect_sth_in_text

# from tasks import agents
from tasks.agents import selenium_lib, requests_lib, requests_html_lib, openai


get_error_msg = (
    lambda task_name: f"Es tut mir leid, bei der Bearbeitung der Aufgabe ist es zu einem unerwarteten Fehler gekommen."
)


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

    # Prüfen, ob die Bestätigung der Ausführung logisch bereits erteilt werden kann und diese mit der aktuellen Nachricht auch erteilt wurde
    if (not is_confirmation_possible) or (intent_tag != "zustimmung"):
        query = "Nun denn, ich führe den Task aus, okay?"
        return {"state_running_task": state_running_task, "response": query}

    return {"state_running_task": None, "response": "Vielen Dank, der Task wurde ausgeführt."}


def check_where_to_stream_media(state_running_task, message_raw, intent_tag):

    if not state_running_task or not message_raw or not intent_tag:
        return {"state_running_task": state_running_task, "response": None}

    if intent_tag == "ablehnung":
        return {
            "state_running_task": None,
            "response": "Ich breche die Suche nach Streaming-Anbietern ab.",
        }

    # Was bisher an Werten ermittelt wurde
    media_title = state_running_task["params"].get("media_title")

    # String mit Rückfragen bei unvollständigen Angaben
    query = ""

    # Nachverfolgen, ob schon vor dieser Nachricht alle Daten vorlagen und es sich um eine Besätigung handeln kann
    is_confirmation_possible = True

    # Falls dem Task noch kein Medientitel zugeordnet wurde, versuche, diesen aus dem Text zu entnehmen
    if not media_title:
        start_end_pairs = [
            ("wer streamt ", "?"),
            ("wer hat ", "?"),
            ("wo kann ich ", " streamen"),
            ("wo kann ich ", " gucken"),
            ("wo kann man ", " streamen"),
            ("wo kann man ", " gucken"),
        ]
        extracted_values = extract_values_in_multiple_syntaxes(
            message_raw, start_end_pairs, is_case_sensitive=False
        )
        if extracted_values:
            media_title = extracted_values[0].strip()

        if not media_title:
            media_title = remove_punctuation(message_raw)
            words_to_remove = ["wer streamt", "wo streame ich"]
            media_title = remove_words_first_occurances(media_title, words_to_remove).strip()
            if not media_title:
                query = get_random_item_in_list(
                    [
                        "Gib den Titel des Films oder der Serie bitte erneut an.",
                        "Wie lautet der Titel des Films oder der Serie genau?",
                        "Nach welchem Titel soll ich suchen?",
                    ]
                )
                return {"state_running_task": state_running_task, "response": query}

        # Medientitel wurde gefunden und wird im Task-Zustand gespeichert
        state_running_task["params"]["media_title"] = media_title
        is_confirmation_possible = False

    # Prüfen, ob die Bestätigung der Ausführung logisch bereits erteilt werden kann und diese mit der aktuellen Nachricht auch erteilt wurde
    if (not is_confirmation_possible) or (intent_tag != "zustimmung"):
        query = get_random_item_in_list(
            [
                f'Du möchtest wissen, bei welchem Anbieter Du "{media_title}" aktuell streamen kannst?',
                f'Du möchtest "{media_title}" streamen, aber weißt nicht wo?',
            ]
        )
        return {"state_running_task": state_running_task, "response": query}

    result = requests_html_lib.requests_html_lib.wer_streamt_es(media_title)
    return {"state_running_task": None, "response": result}


def google_information(state_running_task, message_raw, intent_tag):

    # TODO ...

    search_term = remove_punctuation(message_raw)
    words_to_remove = ["google", "bitte", "nach"]
    search_term = remove_words_first_occurances(search_term, words_to_remove).strip()

    # TODO: Falls search_term nur ein Wort enthält, Rückfrage ausgeben, wonach gesucht werden soll

    result = selenium_lib.google.get_google_answer(search_term)

    return result
