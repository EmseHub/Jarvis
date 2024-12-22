import asyncio

import os
from datetime import datetime

from tasks.agents import selenium_lib, requests_lib, requests_html_lib, openai_lib


from speech_synthesis.api import elevenlabs_lib
from speech_recognitions.speech_recognition_lib import recognize_speech


def main():

    result = "NIX"

    url = "https://www.google.com/search?q=wie+alt+ist+angela+merkel"
    # result = requests_lib.requests_lib.get_reponse_text(url)

    # result = requests_html_lib.requests_html_lib.wer_streamt_es("Army of Darkness")

    question = "Wie alt ist Angela Merkel?"
    # result = selenium_lib.google.get_google_answer(question)

    # result = selenium_lib.ms_copilot.get_mscopilot_answer(question, is_short_answer=True)

    # result = openai_lib.chat_gpt.get_response("Wer ist eigentlich Angela?")

    # result = selenium_lib.whatsapp.get_whatsapp_TODO()

    # elevenlabs_lib.play_speech(
    #     "Nichts geht jemals weg, bevor es uns gelehrt hat, was wir wissen müssen."
    # )

    recognize_speech()

    print(result)

    return ""

    # “start” a file with its associated program
    os.startfile(r"C:\Users\Emse\Downloads\Ed.jpg")

    command = ""
    # Tasks
    if True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("The Current Time is " + current_time)

    if True:
        os.system()
        print("Opening Slack")

    if "close slack" in command:
        os.system("open /Applications/Slack.app")
        print("Closing Slack")


main()
