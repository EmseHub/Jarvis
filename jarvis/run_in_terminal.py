import json

from chatbot.chatbot import get_response


def run_chatbot_in_terminal():

    tagged_tokens = intent = state_running_task = {}

    opening_messsage = 'Okay, lass uns per Terminal chatten!\n' + \
        '[Eingabe "task": Stand des aktuell bearbeiteten Tasks ausgeben]\n' + \
        '[Eingabe "tokens": Ermittelte Tokens der letzten Nachricht ausgeben]\n' + \
        '[Eingabe "exit": Chat beenden]'
    print(opening_messsage)

    while True:
        message = input().strip()

        if (not message):
            continue

        elif message.lower() == "task":
            print(json.dumps(state_running_task, indent=4))

        elif message.lower() == "tokens":
            print(json.dumps(tagged_tokens, indent=4))
            continue

        elif message.lower() == "exit":
            print('> Danke! Bis bald!')
            break

        response, diagnostic = get_response(message)

        tagged_tokens = diagnostic.get("tagged_tokens")
        intent = diagnostic.get("intent")
        state_running_task = diagnostic.get("state_running_task")

        print("---Gefundener Intent---\n", intent.get("tag"))

        print("> " + response)


if (__name__) == "__main__":
    run_chatbot_in_terminal()
