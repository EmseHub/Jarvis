from helpers.helpers import parse_object_from_jsonfile
from nlu_pipeline.preprocessing import get_tagged_tokens
from nlu_pipeline.intent_matching import get_intent
from tasks.task_management import process_task

# Globale Variable mit Settings
settings = parse_object_from_jsonfile("jarvis/settings.json")

# Globale Variable über den aktuell bearbeiteten Task
state_running_task = {}


def get_response(message):

    global state_running_task

    tagged_tokens = get_tagged_tokens(message)

    intent = get_intent(tagged_tokens)

    (state_running_task, response, is_exit_assistant) = process_task(state_running_task, tagged_tokens, message, intent)

    diagnostic = {"tagged_tokens": tagged_tokens, "intent": intent, "state_running_task": state_running_task}

    return (response, diagnostic, is_exit_assistant)
