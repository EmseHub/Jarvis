import requests

from helpers.helpers import write_text_to_textfile


def get_reponse_text(url):

    response = requests.get(url)

    print("Status Code:")
    print(response.status_code)

    response_text = response.text

    write_text_to_textfile("tmp_get_response.html", response_text)

    return response_text
