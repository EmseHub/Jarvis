import time
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from helpers.helpers import write_text_to_textfile, remove_emojis


def get_mscopilot_answer(question, is_short_answer=False):

    if not (question or question.strip()):
        return None

    driver = webdriver.Chrome()
    driver.maximize_window()

    driver.get("https://copilot.microsoft.com/")

    driver.implicitly_wait(5)

    # Datenschutzbedingungen ablehnen
    button_ablehnen = driver.find_element(By.ID, "bnp_btn_reject")
    button_ablehnen.click()

    # Text-Eingabe
    shadow_root_lvl_1 = driver.find_element(By.CSS_SELECTOR, ".cib-serp-main").shadow_root

    textarea_search = (
        shadow_root_lvl_1.find_element(By.ID, "cib-action-bar-main")
        .shadow_root.find_element(By.CSS_SELECTOR, "cib-text-input")
        .shadow_root.find_element(By.ID, "searchbox")
    )

    # Falls eine kurze Antwort ausgegeben werden soll, Länge der Antwort beschränken
    if is_short_answer:
        max_length = 500
        question = f"Antworte in maximal {max_length} Zeichen: {question}"

    textarea_search.send_keys(question)
    textarea_search.send_keys(Keys.ENTER)

    time.sleep(3)

    # Warten, bis Antwort vollständig ausgegeben ist (Kein "Antwort abbrechen")
    typing_indicator = shadow_root_lvl_1.find_element(
        By.ID, "cib-action-bar-main"
    ).shadow_root.find_element(By.CSS_SELECTOR, "cib-typing-indicator")

    while typing_indicator.is_displayed():
        time.sleep(2)

    # Antwort auslesen
    div_text_block = (
        shadow_root_lvl_1.find_element(By.ID, "cib-conversation-main")
        .shadow_root.find_element(By.CSS_SELECTOR, "cib-chat-turn")
        .shadow_root.find_element(By.CSS_SELECTOR, "cib-message-group.response-message-group")
        .shadow_root.find_element(By.CSS_SELECTOR, "cib-message")
        .shadow_root.find_element(By.CSS_SELECTOR, ".ac-textBlock")
    )

    # Falls eine kurze Antwort ausgegeben werden soll, nur den ersten Absatz ausgeben
    if is_short_answer:
        result = div_text_block.find_element(By.CSS_SELECTOR, "p").text
    else:
        result = div_text_block.text

    driver.quit()

    write_text_to_textfile("tmp_selenium_answer_raw.txt", result)

    # Antwort bereinigen

    # Emojis etc. entfernen
    result = remove_emojis(result)

    # Zeilen mit Quellenangaben entfernen
    # result = "".join([
    #     line for line in result.splitlines() if (line.strip() and not line.isnumeric())
    # ])
    # Regex für Quellenangaben
    result = re.sub(r"(\r?\n)(\d+(\r?\n))+", "", result)

    # Mehrfache Leerzeichen auf eines reduzieren
    result = re.sub(r"( ){2,}", " ", result).strip()

    write_text_to_textfile("tmp_selenium_answer_clean.txt", result)

    return result


def get_google_answer(searchterm):

    driver = webdriver.Chrome()
    driver.maximize_window()

    searchterm_converted = "wie+alt+ist+angela+merkel"

    driver.get("https://www.google.com/search?q=" + searchterm_converted)

    driver.implicitly_wait(5)

    # by_class = driver.find_element(By.CLASS_NAME, "current-stage").get_attribute("textContent")

    containing = driver.find_element(by=By.XPATH, value="//*[contains(text(),'Jahre')]")

    text = containing.text

    driver.quit()

    print("Selenium Ergebnis")
    print(text)

    return text
