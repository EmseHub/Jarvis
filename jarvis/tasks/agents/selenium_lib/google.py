import re

from selenium import webdriver
from selenium.webdriver.common.by import By

from helpers.helpers import url_encode


def get_google_answer(search_term):

    driver = webdriver.Chrome()
    driver.maximize_window()

    driver.get("https://www.google.com/search?q=" + url_encode(search_term))

    driver.implicitly_wait(5)

    # Datenschutzbedingungen ablehnen
    button_ablehnen = driver.find_element(By.XPATH, "//*[ text() = 'Alle ablehnen' ]")
    if button_ablehnen:
        button_ablehnen.click()

    # data-attrid="DictionaryHeader" --> Es gibt dict
    # data-attrid="SenseDefinition" -> jeweils Erstes span des elem ist definition

    result = ""

    definition_elems = driver.find_elements(By.XPATH, "//div[@data-attrid='SenseDefinition']")
    if definition_elems:
        nr = 1
        for elem in definition_elems:
            span = elem.find_element(By.TAG_NAME, "span")
            result = ((f"{result}\nDefinition {nr}: " if len(definition_elems) > 1 else "") + span.text).strip()
            nr += 1

    if not result:
        result = "Kein Dict"

    driver.quit()

    print("Selenium Ergebnis")
    print(result)

    return result

    # by_class = driver.find_element(By.CLASS_NAME, "current-stage").get_attribute("textContent")

    containing = driver.find_element(by=By.XPATH, value="//*[contains(text(),'Jahre')]")
    text = containing.text


get_google_answer("was ist ein haus")
# https://www.google.com/search?q=was+ist+ein+haus
