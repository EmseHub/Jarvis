import os
import re
import sys
import unicodedata
from time import sleep

from requests_html import HTMLSession, AsyncHTMLSession

from helpers.helpers import write_text_to_textfile, url_encode, remove_expressions_at_start

# Doku:
# https://requests.readthedocs.io/projects/requests-html/en/latest/
# https://pypi.org/project/requests-html/

# div.find("a", containing="itemprop")
# div.find("div.myclassA.myclassB h1", first=True).text
# div.find("div[data-ext-provider-name]", first=False)
# div.search(">Stand: {}<")[0]
# div.attrs.get("class")


get_error_msg = (
    lambda website_name: f"Es tut mir leid, bei der Abfrage von {website_name} ist es zu einem unerwarteten Fehler gekommen."
)
get_bad_response_msg = (
    lambda website_name, status_code: f"Die Website {website_name} ist leider nicht erreichbar (Status-Code {status_code})."
)


async def async_get(url):
    asession = AsyncHTMLSession()
    response = await asession.get(url)
    return response.text
    # IN MAIN: result = asyncio.run(requests_html_lib.requests_html_lib.async_get(url))


def sample(search_term):
    try:
        title_converted = url_encode(search_term)
        url = f"https://www.bing.com/search?q={title_converted}"

        print(url)

        session = HTMLSession()
        response = session.get(url)

        if not (response and response.status_code == 200):
            return get_bad_response_msg("bing.com", response.status_code)

        response_text = response.text
        write_text_to_textfile("tmp_get_response.html", response_text)

        return "DONE"
    except Exception as e:
        print(e)
        return get_error_msg("bing.com")


def wikipedia(search_term, is_summary_only=True):
    result_text = None
    is_successful = False
    suggestion = None
    get_return_value = lambda: (result_text, is_successful, suggestion)

    try:
        session = HTMLSession()

        # Seite mit Suchergebnissen laden
        url = f"https://de.wikipedia.org/w/index.php?go=Artikel&search={url_encode(search_term)}"
        response = session.get(url, allow_redirects=True)
        if not (response and response.status_code == 200):
            result_text = get_bad_response_msg("de.wikipedia.org", response.status_code)
            return get_return_value()

        write_text_to_textfile("tmp_get_response.html", response.text)

        div_content = response.html.find("div#mw-content-text", first=True)
        if not div_content:
            # Gar kein auslesbarer Inhalt
            result_text = f'Wikipedia liefert zur Anfrage "{search_term}" leider kein verwertbares Ergebnis.'
            return get_return_value()

        div_searchresults = div_content.find("div.searchresults", first=True)

        if div_searchresults:
            # A: Kein Treffer, Weiterleitung zur Auswahl ähnlicher Artikel (Bundeskanzzler)
            result_text = f'In der deutschsprachigen Wikipedia existiert kein Artikel zu "{search_term}".'
            a_first_suggestion = div_searchresults.find(
                "div.mw-search-results-container > ul.mw-search-results > li a", first=True
            )
            if a_first_suggestion and a_first_suggestion.text:
                suggestion = a_first_suggestion.text
                result_text += f' Meintest Du "{suggestion}"?'
            return get_return_value()

        p_first = div_content.find("div.mw-content-ltr > p", first=True)
        if (
            p_first
            and p_first.text
            and (
                p_first.text.strip().lower().startswith(search_term.lower().strip())
                and p_first.text.strip().lower().endswith(("steht für:", "steht"))
            )
        ):
            # B: Mehrere Treffer, Weiterleitung zur Auswahl der verfügbaren Artikel (Bundeskanzler)
            result_text = f'Zu "{search_term}" wurden mehrere Artikel gefunden.'

            a_first_suggestion = div_content.find("div.mw-content-ltr > ul > li > a", first=True)

            if a_first_suggestion and a_first_suggestion.text and a_first_suggestion.attrs.get("title"):
                suggestion = a_first_suggestion.attrs.get("title")
                result_text += f' Soll ich den ersten Treffer, "{suggestion}", ausgeben?'
            return get_return_value()

        children_content = div_content.find("div.mw-content-ltr > *", first=False)
        if children_content:
            # C: Eindeutiger Treffer, Weiterleitung zum einzigen Artikel (Octopath Traveler)
            remove_line_breaks_and_styling = lambda text: " ".join(
                [line for line in text.splitlines() if (line and not line.strip().startswith(".mw-parser-output"))]
            )
            result_text = ""
            for child in children_content:
                tag = child.tag.lower()
                if is_summary_only and (tag == "div") and (child.attrs.get("id") == "toc"):
                    break
                if tag == "h2" and child.find("span#Weblinks, span#Einzelnachweise", first=True):
                    break
                if (
                    (tag == "p")
                    or (tag.startswith("h") and len(tag) == 2)
                    or ((tag == "div") and (child.attrs.get("class")[0] == "Vorlage_Zitat"))
                ):
                    result_text += remove_line_breaks_and_styling(child.text) + "\n\n"
                elif tag == "a":
                    result_text += remove_line_breaks_and_styling(child.text)

            # Quellenverweise etc. entfernen
            result_text = re.sub(r"\[([^\[\]]+)\]", "", result_text)
            # Mehrfache Leerzeichen auf eines reduzieren
            result_text = re.sub(r" +", " ", result_text).strip()
            is_successful = True

        if not result_text:
            result_text = "Der Algorithmus zum Auslesen von Wikipedia muss überarbeitet werden."
            is_successful = False

        return get_return_value()

    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        result_text = get_error_msg("de.wikipedia.org")
        return get_return_value()


def bing(search_term):
    try:
        session = HTMLSession()

        # Seite mit Suchergebnissen laden
        url = f"https://www.bing.com/search?q={url_encode(search_term)}"
        response = session.get(url, allow_redirects=True)
        if not (response and response.status_code == 200):
            return get_bad_response_msg("bing.com", response.status_code)

        response_text = response.text
        write_text_to_textfile("tmp_get_response.html", response_text)

        lis_result = response.html.find("ol#b_results > li.b_algo", first=False)

        if not lis_result:
            return f'Auf Bing wurde nichts zur Suchanfrage "{search_term}" gefunden.'

        # Suchergebnisse zusammenstellen
        search_result_dicts = []
        for li in lis_result:
            div_source_name = li.find("div.tptxt > div.tptt", first=True)
            source_name = div_source_name.text if div_source_name else None

            a_title = li.find("h2 > a", first=True)
            title = a_title.text if a_title else None
            url = list(a_title.links)[0] if (a_title and a_title.links) else None

            span_date = li.find(".news_dt", first=True)
            date = span_date.text if span_date else None

            p_infotext = li.find("div.b_caption > p", first=True)
            infotext = p_infotext.text if p_infotext else None

            if not infotext:
                continue

            # infotext = unicodedata.normalize("NFKD", infotext)
            infotext = remove_expressions_at_start(
                text=infotext, expressions_to_remove=["WEB", date, "·"], is_word_boundary=False, is_case_sensitive=True
            ).strip()

            search_result_dicts.append(
                {"source_name": source_name, "url": url, "title": title, "date": date, "infotext": infotext}
            )

        # Antwort verfassen
        if search_result_dicts:
            first_search_result_dict = search_result_dicts[0]

            result = f"Hier ist der Inhalt "
            result += (
                f"von {first_search_result_dict['source_name']}, dem ersten Treffer"
                if first_search_result_dict["source_name"]
                else "des ersten Treffers"
            )
            result += ":\n" + first_search_result_dict["infotext"]
            if first_search_result_dict["date"]:
                result += f" (Stand {first_search_result_dict['date']})"

            return result

        return f'Keiner der Treffer von Bing enthält auslesbare Informationen zur Suchanfrage "{search_term}".'

    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return get_error_msg("bing.com")


def wer_streamt_es(title):
    try:
        session = HTMLSession()

        # Seite mit Suchergebnissen laden
        url = f"https://www.werstreamt.es/filme-serien/?q={url_encode(title)}"
        response = session.get(url)

        if not (response and response.status_code == 200):
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
            provider_dict = {"name": provider_name, "date": date, "is_in_flatrate": False}

            # Standard-Layout bei Filmen
            div_flatrate = div.find("div.columns.small-4", first=True)
            if div_flatrate:
                small = div_flatrate.find("small", first=True)
                icon = div_flatrate.find("i", first=True) if small else None

                if small and small.text == "Flatrate" and "fi-check" in icon.attrs.get("class"):
                    provider_dict["is_in_flatrate"] = True
            # Bei Serien manchmal andere GUI
            else:
                div_flatrate = div.find("div.columns.medium-9.large-10", first=True)
                span_flatrate = div.find("span.flatrate2", first=True) if div_flatrate else None
                if span_flatrate and span_flatrate.text == "Flatrate":
                    provider_dict["is_in_flatrate"] = True

            if provider_dict["is_in_flatrate"] == True:
                is_any_flatrate = True

            provider_dicts.append(provider_dict)

        media_type = divs_container.attrs.get("data-ext-type")
        media_title = divs_container.find("div.ContentSummary h1", first=True).text

        # Antwort verfassen
        result = "Laut werstreamt.es ist "
        result += "der Film " if media_type == "Movie" else ("die Serie " if media_type == "Show" else "das Medium ")
        result += f'"{media_title}" '

        if is_any_flatrate:
            provider_with_flatrate_dicts = [
                provider_dict for provider_dict in provider_dicts if provider_dict["is_in_flatrate"]
            ]
            result += "aktuell "
            if len(provider_with_flatrate_dicts) == 1:
                result += f"nur bei {provider_with_flatrate_dicts[0]['name']} kostenfrei verfügbar (Stand {provider_with_flatrate_dicts[0]['date']})."
            else:
                result += f"bei "
                for provider_with_flatrate_dict in provider_with_flatrate_dicts[:-2]:
                    result += f"{provider_with_flatrate_dict['name']} (Stand {provider_with_flatrate_dict['date']}), "

                result += (
                    f"{provider_with_flatrate_dict[-2]['name']} (Stand {provider_with_flatrate_dict[-2]['date']}) "
                    f"und {provider_with_flatrate_dict[-1]['name']} (Stand {provider_with_flatrate_dict[-1]['date']}) "
                    "kostenfrei verfügbar."
                )
        else:
            result += "nach aktuellem Stand bei keinem Anbieter kostenfrei verfügbar."

        return result
    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

        return get_error_msg("werstreamt.es")
