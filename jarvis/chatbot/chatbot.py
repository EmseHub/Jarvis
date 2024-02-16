from operator import itemgetter

from chatbot.preprocessing import get_tagged_tokens
from chatbot.intent_matching import get_intent
from chatbot.tasks import process_task

# Globale Variable über den aktuell bearbeiteten Task
state_running_task = {}


def get_response(message):

    global state_running_task

    tagged_tokens = get_tagged_tokens(message)

    intent = get_intent(tagged_tokens)

    state_running_task, response = itemgetter("state_running_task", "response")(
        process_task(state_running_task, tagged_tokens, message, intent)
    )

    diagnostic = {
        "tagged_tokens": tagged_tokens,
        "intent": intent,
        "state_running_task": state_running_task
    }

    return (response, diagnostic)
