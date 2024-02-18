from functions.web import requests_lib
from functions.web import selenium_lib


# url = "https://www.google.com/search?q=wie+alt+ist+angela+merkel"
# result = requests_lib.get_reponse_text(url)


question = "Wie alt ist Angela Merkel?"

# result = selenium_lib.get_google_answer(question)
result = selenium_lib.get_mscopilot_answer(question)

print(result)
