import re

from requests_html import HTMLSession, AsyncHTMLSession

from helpers.helpers import write_text_to_textfile, url_encode

# Doku:
# https://requests.readthedocs.io/projects/requests-html/en/latest/
# https://pypi.org/project/requests-html/

# div.find("a", containing="itemprop")
# div.find("div.myclassA.myclassB h1", first=True).text
# div.find("div[data-ext-provider-name]", first=False)
# div.search(">Stand: {}<")[0]
# div.attrs.get("class")


get_error_msg = lambda website_name : f"Es tut mir leid, bei der Abfrage von {website_name} ist es zu einem unerwarteten Fehler gekommen."
get_bad_response_msg = lambda website_name, status_code : f"Die Website {website_name} ist leider nicht erreichbar (Status-Code {status_code})."


async def async_get(url):
    asession = AsyncHTMLSession()
    response = await asession.get(url)
    return response.text
    # IN MAIN: result = asyncio.run(requests_html_lib.requests_html_lib.async_get(url))


def sample(search_term):
    try:
        # title_converted = re.sub(r"\s+", "+", search_term)
        title_converted = url_encode(search_term)
        url = f"https://www.bing.com/search?q={title_converted}"

        print(url)

        session = HTMLSession()
        response = session.get(url)

        if not (response and response.status_code == 200 ):
            return get_bad_response_msg("bing.com", response.status_code)
        
        response_text = response.text
        write_text_to_textfile("tmp_get_response.html", response_text)

        return "DONE"
    except Exception as e:
        print(e)
        return get_error_msg("bing.com")



def wer_streamt_es(title):
    try:
        session = HTMLSession()

        # Seite mit Suchergebnissen laden
        # title_converted = re.sub(r"\s+", "+", title)
        title_converted = url_encode(title)
        url = f"https://www.werstreamt.es/filme-serien/?q={title_converted}"
        print(url)
        response = session.get(url)

        if not (response and response.status_code == 200 ):
            return get_bad_response_msg("werstreamt.es", response.status_code)

        anchor = response.html.find(".results li[data-avastatus] a", first=True)

        if not anchor or not anchor.absolute_links:
            return f'Auf werstreamt.es wurde nichts zum Suchwort "{title}" gefunden.'

        # Seite des ersten Treffers laden und Verfügbarkeiten auslesen
        url = f"https://www.werstreamt.es/{list(anchor.links)[0]}"
        response = session.get(f"{url}")

        divs_container = response.html.find("div[data-ext-type]", first=True)
        divs_provider = divs_container.find("div[data-ext-provider-name]", first=False)

        is_any_flatrate = False
        provider_dicts = []

        for div in divs_provider:
            provider_name = div.attrs.get("data-ext-provider-name")
            date = div.search(">Stand: {}<")[0]
            provider_dict = {"name": provider_name, "date": date, "flatrate": False}

            div_flatrate = div.find("div.columns.small-4", first=True)
            small = div_flatrate.find("small", first=True)
            icon = div_flatrate.find("i", first=True)

            if small.text == "Flatrate" and "fi-check" in icon.attrs.get("class"):
                provider_dict["flatrate"] = True
                is_any_flatrate = True

            provider_dicts.append(provider_dict)

        media_type = divs_container.attrs.get("data-ext-type")
        media_title = divs_container.find("div.ContentSummary h1", first=True).text

        # Antwort verfassen
        result = "Laut werstreamt.es ist "
        result += (
            "der Film "
            if media_type == "Movie"
            else ("die Serie " if media_type == "Show" else "das Medium ")
        )
        result += f'"{media_title}" '

        if is_any_flatrate:
            provider_with_flatrate_dicts = [
                provider_dict for provider_dict in provider_dicts if provider_dict["flatrate"]
            ]
            result += "aktuell "
            if len(provider_with_flatrate_dicts) == 1:
                result += f"nur bei {provider_with_flatrate_dicts[0]["name"]} kostenfrei verfügbar (Stand {provider_with_flatrate_dicts[0]["date"]})."
            else:
                result += f"bei "
                for provider_with_flatrate_dict in provider_with_flatrate_dicts[:-2]:
                    result += f"{provider_with_flatrate_dict["name"]} (Stand {provider_with_flatrate_dict["date"]}), "

                result += (
                    f"{provider_with_flatrate_dict[-2]["name"]} (Stand {provider_with_flatrate_dict[-2]["date"]}) "
                    f"und {provider_with_flatrate_dict[-1]["name"]} (Stand {provider_with_flatrate_dict[-1]["date"]}) "
                    "kostenfrei verfügbar."
                )
        else:
            result += "nach aktuellem Stand bei keinem Anbieter kostenfrei verfügbar."

        return result
    except Exception as e:
        print(e)
        return get_error_msg("werstreamt.es")
