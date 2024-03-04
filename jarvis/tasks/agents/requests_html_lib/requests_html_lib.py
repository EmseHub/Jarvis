import re


from requests_html import HTMLSession, AsyncHTMLSession


from helpers.helpers import write_text_to_textfile

# Doku:
# https://requests.readthedocs.io/projects/requests-html/en/latest/
# https://pypi.org/project/requests-html/


async def async_get(url):
    asession = AsyncHTMLSession()
    response = await asession.get(url)
    return response.text
    # IN MAIN: result = asyncio.run(requests_html_lib.requests_html_lib.async_get(url))


def wer_streamt_es(title):
    title_converted = re.sub(r"\s+", "+", title)
    url = f"https://www.werstreamt.es/filme-serien/?q={title_converted}"

    session = HTMLSession()
    response = session.get(url)
    print("Status Code:")
    print(response.status_code)

    # anchor.html.find("a", containing="itemprop")
    anchor = response.html.find(".results li[data-avastatus] a", first=True)

    if not anchor or not anchor.absolute_links:
        print(f"Suchwort {title} nicht gefunden.")
        return f"Suchwort {title} nicht gefunden."

    # Load page of movie/series
    url = f"https://www.werstreamt.es/{list(anchor.links)[0]}"
    print(url)
    response = session.get(f"{url}")

    divs_provider = response.html.find("div[data-ext-provider-name]", first=False)

    provider_dicts = []

    for div in divs_provider:

        provider_name = div.attrs["data-ext-provider-name"]
        date = div.search(">Stand: {}<")[0]
        provider_dict = {"name": provider_name, "date": date, "flatrate": False}

        div_flatrate = div.find("div.columns.small-4", first=True)
        small = div_flatrate.find("small", first=True)
        icon = div_flatrate.find("i", first=True)

        if small.text == "Flatrate" and "fi-check" in icon.attrs["class"]:
            provider_dict["flatrate"] = True

        provider_dicts.append(provider_dict)

    # print(provider_dicts)

    # small-12 columns lg-pl-0 --> Titel merken "Dune (2021)"
    # class fi-check
    #  <div class="provider" data-ext-provider-name="Netflix"
    # -> class "columns small-4" --> <i ... class="fi-check"></i>

    response_text = response.text

    write_text_to_textfile("tmp_get_response.html", response_text)

    return provider_dicts
