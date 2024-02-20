from functions.web import requests_lib
from functions.web import selenium_lib

from functions.openai import chat_gpt

from speech_synthesis import elevenlabs_lib


# url = "https://www.google.com/search?q=wie+alt+ist+angela+merkel"
# result = requests_lib.get_reponse_text(url)


question = "Wie alt ist Angela Merkel?"

# result = selenium_lib.get_google_answer(question)

# result = selenium_lib.get_mscopilot_answer(question, False)


# result = chat_gpt.get_response("Wer ist eigentlich Angela?")
# print(result)


elevenlabs_lib.play_speech(
    "Nichts geht jemals weg, bevor es uns gelehrt hat, was wir wissen müssen."
)
