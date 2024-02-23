import time
import re

import os.path

import pickle

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.wait import WebDriverWait

from helpers.helpers import (
    parse_string_from_textfile,
    parse_object_from_jsonfile,
    write_object_to_jsonfile,
    write_text_to_textfile,
    remove_emojis,
)

BROWSER_DATA_PATH = "jarvis/tasks/agents/web/browser_data"
SELENIUM_SCRIPTS_PATH = "jarvis/tasks/agents/web/selenium_scripts"


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

    # # Datenschutzbedingungen ablehnen
    # button_ablehnen = driver.find_element(By.XPATH, "//*[ text() = 'Alle ablehnen' ]")
    # button_ablehnen.click()

    # by_class = driver.find_element(By.CLASS_NAME, "current-stage").get_attribute("textContent")

    containing = driver.find_element(by=By.XPATH, value="//*[contains(text(),'Jahre')]")

    text = containing.text

    driver.quit()

    print("Selenium Ergebnis")
    print(text)

    return text


def automate_whatsapp():
    contact = "Nikolai Rubin Langenbach"
    text = "Hey, this message was sent using Selenium"
    driver = webdriver.Chrome()
    driver.get("https://web.whatsapp.com")
    print("QR-Code scannen und Enter drücken")
    input()
    print("Angemeldet")

    xpath_input_search = "//*[@title='Sucheingabefeld']"
    input_search = WebDriverWait(driver, 50).until(
        lambda driver: driver.find_element(by=By.XPATH, value=xpath_input_search)
    )
    input_search.click()
    time.sleep(2)
    input_search.send_keys(contact)
    time.sleep(2)

    selected_contact = driver.find_element(by=By.XPATH, value=f"//span[@title='{contact}']")
    selected_contact.click()

    xpath_input_new_msg_parent = "//*[@title='Gib eine Nachricht ein.']"
    input_new_msg_parent = driver.find_element(by=By.XPATH, value=xpath_input_new_msg_parent)
    # input_new_msg = '//div[@class="copyable-text selectable-text"][@contenteditable="true"][@data-tab="10"]'
    # input_box = driver.find_element(by=By.XPATH, value=input_new_msg)
    time.sleep(2)
    # input_new_msg_parent.send_keys(text + Keys.ENTER)
    input_new_msg_parent.send_keys(text)

    print("Drücke Enter zum beenden")
    input()

    driver.quit()

    return "DONE"


def get_whatsapp_TODO():

    driver = webdriver.Chrome()
    driver.maximize_window()

    driver.get("https://web.whatsapp.com/")
    driver.implicitly_wait(5)

    name_website = "whatsapp_web"

    is_browser_data_loaded = load_browser_data(driver, name_website)
    (
        print("Daten geladen. Zum Fortfahren Enter drücken.")
        if is_browser_data_loaded
        else print("Keine Daten vorhanden/geladen. Zum Fortfahren Enter drücken.")
    )
    input()

    print("Zum Speichern Enter drücken.")
    input()

    save_browser_data(driver, name_website)
    print("Daten gespeichert.")

    print("Enter drücken, um Selenium zu beenden.")
    input()

    driver.quit()

    return "DONE"

    # FIRST TIME
    chrome_options = Options()
    chrome_options.add_argument("user-data-dir=selenium")
    driver = webdriver.Chrome(options=chrome_options)
    # for selenium 4.15.2 options instead of chrome_options
    # driver = webdriver.Chrome(options=chrome_options)
    driver.get("www.google.de")

    # NEXT TIME
    # You need to: from selenium.webdriver.chrome.options import Options
    chrome_options = Options()
    chrome_options.add_argument("user-data-dir=selenium")
    driver = webdriver.Chrome(options=chrome_options)
    # for selenium 4.15.2 options instead of chrome_options
    # driver = webdriver.Chrome(options=chrome_options)
    driver.get("www.google.de")
    # Now you can see the cookies, the settings, extensions, etc.,
    # and the logins done in the previous session are present here.

    return "DONE"


def save_cookies(driver, name_website):
    filepath = f"{BROWSER_DATA_PATH}/cookies_{name_website}.json"
    cookies = driver.get_cookies()
    # pickle.dump(cookies, open(filepath, "wb"))
    write_object_to_jsonfile(filepath, cookies)


def load_cookies(driver, name_website, is_refreshing_website=True):
    filepath = f"{BROWSER_DATA_PATH}/cookies_{name_website}.json"
    if os.path.exists(filepath):
        print("Cookies da")
        driver.delete_all_cookies()
        # cookies = pickle.load(open(filepath, "rb"))
        cookies = parse_object_from_jsonfile(filepath)
        for cookie in cookies:
            driver.add_cookie(cookie)
        if is_refreshing_website:
            driver.refresh()
        return True
    return False


def save_local_storage(driver, name_website):
    filepath = f"{BROWSER_DATA_PATH}/local_storage_{name_website}.json"
    local_storage = driver.execute_script("return window.localStorage;")
    for key in ["clear", "getItem", "key", "length", "removeItem", "setItem"]:
        if key in local_storage:
            del local_storage[key]
    # pickle.dump(local_storage, open(filepath, "wb"))
    write_object_to_jsonfile(filepath, local_storage)


def load_local_storage(driver, name_website, is_refreshing_website=True):
    filepath = f"{BROWSER_DATA_PATH}/local_storage_{name_website}.json"
    if os.path.exists(filepath):
        print("local_storage da")
        # local_storage = pickle.load(open(filepath, "rb"))
        local_storage = parse_object_from_jsonfile(filepath)

        js_script = """
        window.localStorage.clear();
        const local_storage = arguments[0];
        for (const key in local_storage) {
            if (Object.hasOwnProperty.call(local_storage, key)) {
                const element = local_storage[key];
                window.localStorage.setItem(key, element);
            }
        }
        """

        driver.execute_script(js_script, local_storage)
        if is_refreshing_website:
            driver.refresh()
        return True
    return False


def save_session_storage(driver, name_website):
    filepath = f"{BROWSER_DATA_PATH}/session_storage_{name_website}.json"
    session_storage = driver.execute_script("return window.sessionStorage;")
    for key in ["clear", "getItem", "key", "length", "removeItem", "setItem"]:
        if key in session_storage:
            del session_storage[key]
    write_object_to_jsonfile(filepath, session_storage)


def load_session_storage(driver, name_website, is_refreshing_website=True):
    filepath = f"{BROWSER_DATA_PATH}/session_storage_{name_website}.json"
    if os.path.exists(filepath):
        print("session_storage da")
        session_storage = parse_object_from_jsonfile(filepath)
        js_script = """
        window.sessionStorage.clear();
        const session_storage = arguments[0];
        for (const key in session_storage) {
            if (Object.hasOwnProperty.call(session_storage, key)) {
                const element = session_storage[key];
                window.sessionStorage.setItem(key, element);
            }
        }
        """
        driver.execute_script(js_script, session_storage)
        if is_refreshing_website:
            driver.refresh()
        return True
    return False


def save_indexed_db(driver, name_website):
    filepath = f"{BROWSER_DATA_PATH}/indexed_db_{name_website}.json"
    # arguments[arguments.length - 1] (letztes Argument) macht Selenium immer zur Callback-Funktion
    indexed_db = driver.execute_async_script(
        parse_string_from_textfile(SELENIUM_SCRIPTS_PATH + "/export_indexed_db.js")
    )
    write_object_to_jsonfile(filepath, indexed_db)


def load_indexed_db(driver, name_website, is_refreshing_website=True):
    filepath = f"{BROWSER_DATA_PATH}/indexed_db_{name_website}.json"

    if os.path.exists(filepath):
        print("indexed_db da")
        indexed_db = parse_object_from_jsonfile(filepath)
        # arguments[arguments.length - 1] (letztes Argument) macht Selenium immer zur Callback-Funktion
        driver.execute_async_script(
            parse_string_from_textfile(SELENIUM_SCRIPTS_PATH + "/import_indexed_db.js"), indexed_db
        )
        if is_refreshing_website:
            driver.refresh()
        return True
    return False


def save_browser_data(driver, name_website):

    save_cookies(driver, name_website)
    save_local_storage(driver, name_website)
    save_session_storage(driver, name_website)
    save_indexed_db(driver, name_website)


def load_browser_data(driver, name_website, is_refreshing_website=True):

    is_cookies_loaded = load_cookies(driver, name_website, False)
    is_local_storage_loaded = load_local_storage(driver, name_website, False)
    is_session_storage_loaded = load_session_storage(driver, name_website, False)
    is_indexed_db_loaded = load_indexed_db(driver, name_website, False)

    if is_refreshing_website and (
        is_cookies_loaded
        and is_local_storage_loaded
        and is_session_storage_loaded
        and is_indexed_db_loaded
    ):
        driver.refresh()
        return True
    return False
