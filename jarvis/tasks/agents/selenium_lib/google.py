import re

from selenium import webdriver
from selenium.webdriver.common.by import By


def get_google_answer(searchterm):

    driver = webdriver.Chrome()
    driver.maximize_window()

    searchterm_converted = re.sub(r"\s+", "+", searchterm)
    # searchterm_converted = "wie+alt+ist+angela+merkel"

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
