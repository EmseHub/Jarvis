import re

from helpers.helpers import (
    get_random_item,
    remove_punctuation,
    remove_expressions_first_occurances,
    remove_expressions_at_start,
    extract_values_in_syntax,
    extract_values_in_multiple_syntaxes,
    replace_diacritics,
)

from tasks.entity_detection import detect_sth_in_text

# from tasks import agents
from tasks.agents import selenium_lib, requests_lib, requests_html_lib, openai_lib, operating_system


def check_if_args_are_valid(*args):
    for arg in args:
        if not arg:
            return False
    return True


def obtain_confirmation(state_running_task, intent_tag, confirmation_messages):
    response = None
    is_confirmed = True

    # Attribut soll sicherstellen, dass Vorgang in einer gesonderten Mitteilung bestätigt wird (Wert ist None, wenn Attribut nicht gesetzt)
    is_confirmation_possible = state_running_task["params"].get("is_confirmation_possible")

    # Prüfen, ob die Bestätigung der Ausführung bereits erteilt werden darf (alle Parameter bekannt) und ob diese mit der aktuellen Nachricht vorliegt
    if not (is_confirmation_possible and intent_tag == "confirmation"):
        # Rückfrage wird ausgegeben, spätestens ab jetzt kann Bestätigung in den nächsten Nachrichten erteilt werden
        state_running_task["params"]["is_confirmation_possible"] = True
        response = get_random_item(confirmation_messages)
        is_confirmed = False

    return (state_running_task, response, is_confirmed)


def prepare_task(
    state_running_task, intent_tag, cancellation_messages, required_param_keys=None, param_detection_function=None
):
    response = None
    is_prepared = True
    params_is_invalid = lambda params, required_keys: any((params.get(key) is None) for key in required_keys)

    # Falls aus aktueller Nachricht eine Ablehnung hervorgeht, beende den Task (zurücksetzen auf None)
    if intent_tag == "denial":
        state_running_task = None
        response = get_random_item(cancellation_messages)
        is_prepared = False

    # Falls dem Task noch ein Parameter-Wert für die Ausführung fehlt, versuche, diesen zu ermitteln
    elif (
        required_param_keys
        and param_detection_function
        and params_is_invalid(state_running_task["params"], required_param_keys)
    ):
        (state_running_task["params"], response) = param_detection_function(state_running_task["params"])
        # Falls immer noch ein Parameter-Wert fehlt, abbrechen und Rückfrage zurückgeben
        if params_is_invalid(state_running_task["params"], required_param_keys):
            is_prepared = False

    # Bereits vor der aktuellen Nachricht wurden alle Parameter-Werte ermittelt und im Task-Zustand gespeichert
    else:
        # Die aktuelle Nachricht kann die Bestätigung der Task-Ausführung sein
        state_running_task["params"]["is_confirmation_possible"] = True

    return (state_running_task, response, is_prepared)


def ask_ai(state_running_task, intent_tag, message_raw):
    response = None
    is_exit_assistant = False

    if check_if_args_are_valid(state_running_task, intent_tag, message_raw):

        def param_detection_function(params):
            query = None
            expressions_to_remove = ("frag die ki", "frag chat gpt", "frag copilot", "ki", "chat gpt", "copilot")
            question = remove_expressions_at_start(remove_punctuation(message_raw), expressions_to_remove).strip()
            if question:
                params["question"] = question
            else:
                query = get_random_item(("Gib Deine Anfrage an die KI bitte erneut an."))
            return (params, query)

        (state_running_task, response, is_prepared) = prepare_task(
            state_running_task=state_running_task,
            intent_tag=intent_tag,
            cancellation_messages=("Ich breche die Anfrage an die KI ab.", "KI-Anfrage wird abgebrochen."),
            required_param_keys=["question"],
            param_detection_function=param_detection_function,
        )

        if is_prepared:
            # Vor der Ausführung die Bestätigung prüfen
            question = state_running_task["params"].get("question")
            (state_running_task, response, is_confirmed) = obtain_confirmation(
                state_running_task=state_running_task,
                intent_tag=intent_tag,
                confirmation_messages=(
                    f'Du möchtest folgende Frage an die KI stellen?: "{question}"',
                    f'Du möchtest die KI Folgendes fragen?: "{question}"',
                ),
            )
            if is_confirmed:
                state_running_task = None
                response = selenium_lib.ms_copilot.get_mscopilot_answer(question, is_short_answer=True)

    return (state_running_task, response, is_exit_assistant)


def ask_google(state_running_task, intent_tag, message_raw):
    response = None
    is_exit_assistant = False

    if check_if_args_are_valid(state_running_task, intent_tag, message_raw):

        def param_detection_function(params):
            query = None
            search_term = None

            start_end_pairs = [
                ("suche nach", " auf google"),
                ("suche nach", " bei google"),
                ("suche ", " auf google"),
                ("suche ", " bei google"),
                ("such nach", " auf google"),
                ("such nach", " bei google"),
                ("such ", " auf google"),
                ("such ", " bei google"),
            ]
            extracted_values = extract_values_in_multiple_syntaxes(message_raw, start_end_pairs)
            if extracted_values:
                search_term = extracted_values[0].strip()

            if not search_term:
                search_term = remove_punctuation(message_raw)
                expressions_to_remove = [
                    "suche auf google nach",
                    "suche bei google nach",
                    "suche bei google",
                    "suche auf google",
                    "such auf google nach",
                    "such bei google nach",
                    "such bei google",
                    "such auf google",
                    "google suche nach",
                    "google bitte nach",
                    "google bitte nach",
                    "google mal nach",
                    "google nach",
                    "google",
                ]
                search_term = remove_expressions_first_occurances(search_term, expressions_to_remove).strip()

            if not search_term:
                query = get_random_item(
                    (
                        "Wonach genau soll ich googlen?",
                        "Wonach soll ich auf Google suchen?",
                        "Wie genau lautet der Suchbegriff?",
                        "Wie lautet die Suchanfrage?",
                    )
                )
            else:
                params["search_term"] = search_term

            return (params, query)

        (state_running_task, response, is_prepared) = prepare_task(
            state_running_task=state_running_task,
            intent_tag=intent_tag,
            cancellation_messages=("Ich breche die Google-Suche ab.", "Suche bei Google wird abgebrochen."),
            required_param_keys=["search_term"],
            param_detection_function=param_detection_function,
        )

        if is_prepared:
            search_term = state_running_task["params"].get("search_term")
            (state_running_task, response, is_confirmed) = obtain_confirmation(
                state_running_task=state_running_task,
                intent_tag=intent_tag,
                confirmation_messages=(
                    f'Du möchtest nach "{search_term}" googlen?',
                    f'Du willst wissen, was Google zur Anfrage "{search_term}" sagt?',
                    f'Du willst auf Google suchen nach"{search_term}"?',
                ),
            )

            if is_confirmed:
                state_running_task = None
                response = selenium_lib.google.get_google_answer(search_term)

    return (state_running_task, response, is_exit_assistant)


def check_where_to_stream_media(state_running_task, intent_tag, message_raw):
    response = None
    is_exit_assistant = False

    if check_if_args_are_valid(state_running_task, intent_tag, message_raw):

        def param_detection_function(params):
            query = None
            media_title = None

            start_end_pairs = [
                ("wer streamt ", "?"),
                ("wer hat ", "?"),
                ("wo kann ich ", " streamen"),
                ("wo kann ich ", " gucken"),
                ("wo kann man ", " streamen"),
                ("wo kann man ", " gucken"),
            ]
            extracted_values = extract_values_in_multiple_syntaxes(message_raw, start_end_pairs)
            if extracted_values:
                media_title = extracted_values[0].strip()

            if not media_title:
                media_title = remove_punctuation(message_raw)
                expressions_to_remove = ["wer streamt", "wo streame ich"]
                media_title = remove_expressions_first_occurances(media_title, expressions_to_remove).strip()

            if not media_title:
                query = get_random_item(
                    (
                        "Gib den Titel des Films oder der Serie bitte erneut an.",
                        "Wie lautet der Titel des Films oder der Serie genau?",
                        "Nach welchem Titel soll ich suchen?",
                    )
                )
            else:
                params["media_title"] = media_title

            return (params, query)

        (state_running_task, response, is_prepared) = prepare_task(
            state_running_task=state_running_task,
            intent_tag=intent_tag,
            cancellation_messages=(
                "Ich breche die Suche nach Streaming-Anbietern ab.",
                "Suche nach Streaming-Anbietern wird abgebrochen.",
            ),
            required_param_keys=["media_title"],
            param_detection_function=param_detection_function,
        )

        if is_prepared:
            # Vor der Ausführung die Bestätigung prüfen
            media_title = state_running_task["params"].get("media_title")
            (state_running_task, response, is_confirmed) = obtain_confirmation(
                state_running_task=state_running_task,
                intent_tag=intent_tag,
                confirmation_messages=(
                    f'Du möchtest wissen, bei welchem Anbieter Du "{media_title}" aktuell streamen kannst?',
                    f'Du möchtest "{media_title}" streamen, aber weißt nicht wo?',
                    f'Du möchtest "{media_title}" streamen?',
                    f'Meinst Du "{media_title}"?',
                ),
            )

            if is_confirmed:
                state_running_task = None
                response = requests_html_lib.requests_html_lib.wer_streamt_es(media_title)

    return (state_running_task, response, is_exit_assistant)


def ask_ai_BAK(state_running_task, intent_tag, message_raw):

    state_running_task = state_running_task if state_running_task else None
    response = None
    is_exit_assistant = False
    get_return_value = lambda: (state_running_task, response, is_exit_assistant)

    if not state_running_task or not intent_tag or not message_raw:
        return get_return_value()

    if intent_tag == "denial":
        state_running_task = None
        response = get_random_item(
            ("Ich breche die Anfrage an die künstliche Intelligenz ab.", "KI-Anfrage wird abgebrochen.")
        )
        return get_return_value()

    # Was bisher an Werten ermittelt wurde
    media_title = state_running_task["params"].get("question")

    # Nachverfolgen, ob schon vor dieser Nachricht alle Daten vorlagen und es sich um eine Besätigung handeln kann
    is_confirmation_possible = True

    # Falls dem Task noch keine Fragentext zugeordnet wurde, versuche, diesen aus dem Text zu entnehmen
    if not media_title:
        media_title = message_raw
        if not media_title:
            response = get_random_item(("Gib Deine Anfrage an die KI bitte erneut an."))
            return get_return_value()

        # Fragentext wurde (jetzt erst) gefunden und wird im Task-Zustand gespeichert
        state_running_task["params"]["question"] = media_title
        is_confirmation_possible = False

    # Prüfen, ob die Bestätigung der Ausführung logisch bereits erteilt werden kann und diese mit der aktuellen Nachricht auch erteilt wurde
    if not (is_confirmation_possible and intent_tag == "confirmation"):
        response = get_random_item(
            (
                f'Du möchtest folgende Frage an die KI stellen?: "{media_title}"',
                f'Du möchtest die KI Folgendes fragen?: "{media_title}"',
            )
        )
        return get_return_value()

    response = selenium_lib.ms_copilot.get_mscopilot_answer(media_title, is_short_answer=True)
    state_running_task = None
    return get_return_value()


def check_where_to_stream_media_BAK(state_running_task, intent_tag, message_raw):

    state_running_task = state_running_task if state_running_task else None
    response = None
    is_exit_assistant = False
    get_return_value = lambda: (state_running_task, response, is_exit_assistant)

    if not state_running_task or not intent_tag or not message_raw:
        return get_return_value()

    if intent_tag == "denial":
        state_running_task = None
        response = get_random_item(
            ("Ich breche die Suche nach Streaming-Anbietern ab.", "Suche nach Streaming-Anbietern wird abgebrochen.")
        )
        return get_return_value()

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
        extracted_values = extract_values_in_multiple_syntaxes(message_raw, start_end_pairs, is_case_sensitive=False)
        if extracted_values:
            media_title = extracted_values[0].strip()

        if not media_title:
            media_title = remove_punctuation(message_raw)
            words_to_remove = ["wer streamt", "wo streame ich"]
            media_title = remove_expressions_first_occurances(media_title, words_to_remove).strip()
            if not media_title:
                response = get_random_item(
                    (
                        "Gib den Titel des Films oder der Serie bitte erneut an.",
                        "Wie lautet der Titel des Films oder der Serie genau?",
                        "Nach welchem Titel soll ich suchen?",
                    )
                )
                return get_return_value()

        # Medientitel wurde (jetzt erst) gefunden und wird im Task-Zustand gespeichert
        state_running_task["params"]["media_title"] = media_title
        is_confirmation_possible = False

    # Prüfen, ob die Bestätigung der Ausführung logisch bereits erteilt werden kann und diese mit der aktuellen Nachricht auch erteilt wurde
    if not (is_confirmation_possible and intent_tag == "confirmation"):
        response = get_random_item(
            (
                f'Du möchtest wissen, bei welchem Anbieter Du "{media_title}" aktuell streamen kannst?',
                f'Du möchtest "{media_title}" streamen, aber weißt nicht wo?',
                f'Du möchtest "{media_title}" streamen?',
                f'Meinst Du "{media_title}"?',
            )
        )
        return get_return_value()

    response = requests_html_lib.requests_html_lib.wer_streamt_es(media_title)
    state_running_task = None
    return get_return_value()


def exit_assistant(state_running_task, intent_tag):
    state_running_task = None
    response = "Assistent wird beendet."
    is_exit_assistant = True
    return (state_running_task, response, is_exit_assistant)


# ------------------------------------------------- OS -------------------------------------------------


def hibernate_computer(state_running_task, intent_tag):
    response = None
    is_exit_assistant = False

    if check_if_args_are_valid(state_running_task, intent_tag):

        (state_running_task, response, is_prepared) = prepare_task(
            state_running_task=state_running_task,
            intent_tag=intent_tag,
            cancellation_messages=(
                "Ich versetze das Gerät nicht in den Ruhezustand.",
                "Okay, dann also kein Ruhezustand...",
            ),
        )

        if is_prepared:
            (state_running_task, response, is_confirmed) = obtain_confirmation(
                state_running_task=state_running_task,
                intent_tag=intent_tag,
                confirmation_messages=(
                    "Soll das Gerät wirklich in den Ruhezustand versetzt werden?",
                    "Bist Du sicher, dass das System in den Ruhezustand versetzt werden soll?",
                    "Soll das Gerät wirklich in den Ruhezustand versetzt werden?",
                    "System wirklich in den Ruhezustand versetzen?",
                ),
            )

            if is_confirmed:
                state_running_task = None
                (response, is_successful) = operating_system.operating_system.hibernate_computer()

    return (state_running_task, response, is_exit_assistant)


def shutdown_computer(state_running_task, intent_tag):
    response = None
    is_exit_assistant = False

    if check_if_args_are_valid(state_running_task, intent_tag):

        (state_running_task, response, is_prepared) = prepare_task(
            state_running_task=state_running_task,
            intent_tag=intent_tag,
            cancellation_messages=("Ich fahre das Gerät nicht herunter.", "Okay, das System läuft weiter..."),
        )

        if is_prepared:
            (state_running_task, response, is_confirmed) = obtain_confirmation(
                state_running_task=state_running_task,
                intent_tag=intent_tag,
                confirmation_messages=(
                    "Soll das Gerät wirklich vollständig heruntergefahren werden?",
                    "Bist Du sicher, dass das System vollständig heruntergefahren werden soll?",
                    "Soll das Gerät wirklich ausgeschaltet werden?",
                    "System wirklich herunterfahren?",
                    "Gerät wirklich ausschalten?",
                ),
            )

            if is_confirmed:
                state_running_task = None
                (response, is_successful) = operating_system.operating_system.shutdown_computer()
                is_exit_assistant = is_successful

    return (state_running_task, response, is_exit_assistant)


def restart_computer(state_running_task, intent_tag):
    response = None
    is_exit_assistant = False

    if check_if_args_are_valid(state_running_task, intent_tag):

        (state_running_task, response, is_prepared) = prepare_task(
            state_running_task=state_running_task,
            intent_tag=intent_tag,
            cancellation_messages=("Ich starte das Gerät nicht neu.", "Okay, das System läuft ohne Neustart weiter..."),
        )

        if is_prepared:
            (state_running_task, response, is_confirmed) = obtain_confirmation(
                state_running_task=state_running_task,
                intent_tag=intent_tag,
                confirmation_messages=(
                    "Soll das Gerät wirklich neu gestartet werden?",
                    "Bist Du sicher, dass das System neu gestartet werden soll?",
                    "System wirklich neu starten?",
                    "Willst Du wirklich einen Neustart des Geräts?",
                ),
            )

            if is_confirmed:
                state_running_task = None
                (response, is_successful) = operating_system.operating_system.restart_computer()
                is_exit_assistant = is_successful

    return (state_running_task, response, is_exit_assistant)
