from tasks.agents import selenium_lib, requests_lib, requests_html_lib, openai
import asyncio


from speech_synthesis import elevenlabs_lib

result = "NIX"

url = "https://www.google.com/search?q=wie+alt+ist+angela+merkel"
# result = requests_lib.requests_lib.get_reponse_text(url)

# result = requests_html_lib.requests_html_lib.wer_streamt_es("Army of Darkness")


question = "Wie alt ist Angela Merkel?"
# result = selenium_lib.google.get_google_answer(question)

# result = selenium_lib.ms_copilot.get_mscopilot_answer(question, is_short_answer=True)


# result = openai.chat_gpt.get_response("Wer ist eigentlich Angela?")

# result = selenium_lib.whatsapp.get_whatsapp_TODO()
print(result)


# elevenlabs_lib.play_speech(
#     "Nichts geht jemals weg, bevor es uns gelehrt hat, was wir wissen müssen."
# )
