import os
import re
import sys

from helpers.helpers import get_random_item, replace_diacritics
from tasks import task_functions

# Task-Bezeichnung aus Intent eine Funktion zuordnen
task_function_mapping = {
    "ask_ai": {"function": task_functions.ask_ai, "additional_args_names": ["message_raw_simple"]},
    "ask_google": {"function": task_functions.ask_google, "additional_args_names": ["message_raw_simple"]},
    "check_where_to_stream_media": {
        "function": task_functions.check_where_to_stream_media,
        "additional_args_names": ["message_raw_simple"],
    },
    "exit_assistant": {"function": task_functions.exit_assistant},
    "computer_sleep": {"function": task_functions.hibernate_computer},
    "computer_shutdown": {"function": task_functions.shutdown_computer},
    "computer_restart": {"function": task_functions.restart_computer},
}


get_message_raw_simple = lambda message_raw: re.sub(r"\s+", " ", message_raw).strip()
get_message_processed = lambda message_raw_simple: replace_diacritics(message_raw_simple.lower())


def process_task(state_running_task, tagged_tokens, message_raw, intent):
    """Funktion, die die Fortsetzung eines bestehenden oder Eröffnung eines neu erkannten Tasks steuert.
    Falls keine Ausgabe ausgeführt werden soll, wird ein simpler, im Intent vordefinierter Antwort-String zurückgegeben.
    """

    state_running_task = state_running_task if state_running_task else None
    response = None
    is_exit_assistant = False
    get_return_value = lambda: (state_running_task, response, is_exit_assistant)

    # Prüfen, ob eine Nachricht und Tokens vorhanden sind
    if not tagged_tokens or not message_raw:
        return get_return_value()

    try:
        # Prüfen, ob es noch entweder noch einen offenen Task gibt, oder die Eröffnung eines neuen Tasks aus dem Intent hervorgeht
        if state_running_task or intent.get("task"):

            if not state_running_task:
                state_running_task = {"name": intent.get("task"), "params": {}}

            running_task_name = state_running_task.get("name")
            intent_tag = intent["tag"]

            # Weitere Argumente, die je nach Task benötigt werden könnten
            additional_args = {}
            additional_args["message_raw_simple"] = get_message_raw_simple(message_raw)
            additional_args["message_processed"] = get_message_processed(additional_args["message_raw_simple"])

            # Funktion, die dem Task zugeordnet ist
            task_function = task_function_mapping.get(running_task_name).get("function")
            # Weitere Argumente, die an die Funktion übergeben werden sollen (zusätzlich zu state_running_task, intent_tag)
            additional_args_names = task_function_mapping.get(running_task_name).get("additional_args_names")

            if task_function is not None:
                additional_args = (
                    []
                    if (additional_args_names is None)
                    else [additional_args[args_name] for args_name in additional_args_names]
                )
                all_args = [state_running_task, intent_tag] + additional_args
                (state_running_task, response, is_exit_assistant) = task_function(*all_args)
            else:
                state_running_task = None
                response = f'Für die Aufgabe "{running_task_name}" ist leider noch kein Ablauf definiert...'

            # Task abgeschlossen oder abgebrochen -> Anschlussfrage ergänzen
            if not state_running_task and not is_exit_assistant:
                response += " " + get_random_item(
                    [
                        "Kann ich sonst noch etwas für Dich tun?",
                        "Darf es sonst noch etwas sein?",
                        "Hast Du weitere Anliegen?",
                    ]
                )

        # Es ist kein Task offen und soll auch kein neuer gestartet werden (Rückgabe eines im Intent vordefinierten Response-Strings)
        else:
            response = get_random_item(intent["responses"])

        return get_return_value()

    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

        response = f'Es tut mir leid, bei der Bearbeitung der Aufgabe "{state_running_task.get("name")}" ist es zu einem unerwarteten Fehler gekommen. Wiederholen?'
        return get_return_value()
