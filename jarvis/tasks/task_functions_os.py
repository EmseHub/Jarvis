from operator import itemgetter

from helpers.helpers import get_random_item_in_list
from tasks.agents import operating_system


def shutdown_computer(state_running_task, intent_tag):

    if not state_running_task or not intent_tag:
        return {
            "state_running_task": state_running_task,
            "response": None,
            "is_exit_assistant": False,
        }

    if intent_tag == "denial":
        return {
            "state_running_task": None,
            "response": "Ich fahre das Gerät nicht herunter.",
            "is_exit_assistant": False,
        }

    # Attribut soll sicherstellen, dass Vorgang in einer gesonderten Mitteilung bestätigt wird (Wert ist None, wenn Attribut nicht gesetzt)
    is_confirmation_possible = state_running_task["params"].get("is_confirmation_possible")

    # Prüfen, ob die Bestätigung der Ausführung bereits erteilt werden darf und ob diese mit der aktuellen Nachricht vorliegt
    if not (is_confirmation_possible and intent_tag == "confirmation"):
        state_running_task["params"]["is_confirmation_possible"] = True
        query = get_random_item_in_list(
            [
                "Soll das Gerät wirklich vollständig heruntergefahren werden?",
                "Bist Du sicher, dass das System vollständig heruntergefahren werden soll?",
                "Soll das Gerät wirklich ausgeschaltet werden?",
                "System wirklich herunterfahren?",
                "Gerät wirklich ausschalten?",
            ]
        )
        return {
            "state_running_task": state_running_task,
            "response": query,
            "is_exit_assistant": False,
        }

    # Vorgang wurde bestätigt
    response, is_exit_assistant = itemgetter("feedback_text", "is_successful")(
        operating_system.operating_system.shutdown_computer()
    )

    return {
        "state_running_task": None,
        "response": response,
        "is_exit_assistant": is_exit_assistant,
    }
