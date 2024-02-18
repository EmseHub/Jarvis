import re
from operator import itemgetter

from helpers.helpers import get_random_item_in_list, replace_diacritics
from chatbot.entity_detection import detect_sth_in_text
from functions.web import selenium_lib


# region --------------------------- Task-Funtkionen ---------------------------
def do_sth(state_running_task, message_processed, intent_tag):

    if (not state_running_task or not message_processed or not intent_tag):
        return {"state_running_task": state_running_task, "response": None}

    if intent_tag == "ablehnung":
        return {"state_running_task": None, "response": "Ich breche die Aufgabe ab."}

    # String mit Rückfragen bei unvollständigen Angaben
    query = ""

    # Nachverfolgen, ob schon vor dieser Nachricht alle Daten vorlagen und es sich um eine Besätigung handeln kann
    is_confirmation_possible = True

    # Prüfen, ob noch Rückfragen vorliegen, oder alle relevanten Daten vorhanden sind
    if (query):
        return {"state_running_task": state_running_task, "response": query}

    # Prüfen, ob mit der aktuellen Nachricht die Bestätigung erteilt wird
    if ((not is_confirmation_possible) or (intent_tag != "zustimmung")):
        query = "Nun denn, ich führe den Task aus, okay?"
        return {"state_running_task": state_running_task, "response": query}

    return {"state_running_task": None, "response": "Vielen Dank, der Task wurde ausgeführt."}

# endregion --------------------------- Task-Funtkionen ---------------------------


# region --------------------------- Steuerung der Task-Funktionen ---------------------------
def process_task(state_running_task, tagged_tokens, message_raw, intent):
    '''Funktion, die die Fortsetzung eines bestehenden oder Eröffnung eines neu erkannten Tasks steuert. 
    Falls keine Ausgabe ausgeführt werden soll, wird ein simpler, im Intent vordefinierter Antwort-String zurückgegeben.'''

    response = None

    # Prüfen, ob eine Nachricht und Tokens vorhanden sind
    if (not tagged_tokens or not message_raw):
        return {"state_running_task": state_running_task, "response": response}

    # Prüfen, ob es noch entweder noch einen offenen Task gibt, oder die Eröffnung eines neuen Tasks aus dem Intent hervorgeht
    if (state_running_task or intent.get("task")):

        if not state_running_task:
            state_running_task = {"name": intent.get("task"), "params": {}}

        running_task_name = state_running_task.get("name")

        response = f'Für die Aufgabe "{
            running_task_name}" ist leider noch kein Ablauf definiert...'

        message_raw_simple = re.sub(r"\s+", " ", message_raw).strip()
        message_processed = replace_diacritics(message_raw_simple.lower())
        intent_tag = intent["tag"]

        if (running_task_name == "do_sth"):
            state_running_task, response = itemgetter("state_running_task", "response")(
                do_sth(
                    state_running_task, message_processed, intent_tag)
            )
        elif (running_task_name == "test_0"):
            state_running_task = None
            response = selenium_lib.get_mscopilot_answer_full(
                message_raw_simple
            )
        else:
            state_running_task, response = (None, response)

        # Funktion/Prozess für den entsprechenden Task auswählen
        # state_running_task, response = (lambda: (
        #     {
        #         "adresse_aendern": adresse_aendern,
        #         "nachname_aendern": nachname_aendern,
        #         "pruefung_anmelden": pruefung_anmelden,
        #         "pruefung_abmelden": pruefung_abmelden,
        #         "pruefung_status": pruefung_status
        #     }.get(running_task_name, lambda *args: [None, response])
        # )(state_running_task, tagged_tokens, message_raw_simple, intent_tag))()

        # Task abgeschlossen oder abgebrochen -> Anschlussfrage ergänzen
        if not state_running_task:
            response += " " + get_random_item_in_list([
                "Kann ich sonst noch etwas für Dich tun?",
                "Darf es sonst noch etwas sein?",
                "Hast Du weitere Anliegen?"
            ])

    # Es ist kein Task offen und soll auch kein neuer gestartet werden (Rückgabe eines im Intent vordefinierten Response-Strings)
    else:
        response = get_random_item_in_list(intent["responses"])

    return {"state_running_task": state_running_task, "response": response}

# endregion --------------------------- Steuerung der Task-Funktionen ---------------------------
