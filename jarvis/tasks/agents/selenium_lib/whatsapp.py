import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait

from selenium.common import NoSuchElementException, ElementNotInteractableException

from tasks.agents.selenium_lib.general import save_browser_data, load_browser_data


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

    options = webdriver.ChromeOptions()
    # WebDriver führt Aktionen bereits aus, bevor document.readyState == "complete" (Default ist normal)
    options.page_load_strategy = "none"
    # options.addArguments("user-data-dir=/path/to/your/custom/profile")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    # wait = WebDriverWait(driver, 20)

    driver.get("https://web.whatsapp.com/")
    # driver.get("https://www.mydealz.de/share/button/login")

    # Laden der Website abbrechen
    driver.execute_script("window.stop();")

    # driver.implicitly_wait(5)

    # execute a script (first) on every page load
    # lib_script = parse_string_from_textfile("jarvis/tasks/agents/selenium/js_libs/dexie.min.js")
    # driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": lib_script})

    name_website = "whatsapp_web"

    is_browser_data_loaded = load_browser_data(driver, name_website, is_refreshing_website=False)

    if is_browser_data_loaded:
        print("Daten geladen.")
    else:
        print("Keine Daten vorhanden/geladen.")
        driver.refresh()

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
