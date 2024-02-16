from selenium.webdriver.common.by import By
from selenium import webdriver


print("Selenium Test")


def test_0():
    driver = webdriver.Chrome()

    driver.get("https://www.google.com/search?q=wie+alt+ist+angela+merkel")

    driver.implicitly_wait(0.5)

    # text_box = driver.find_element(by=By.NAME, value="my-text")
    # submit_button = driver.find_element(by=By.CSS_SELECTOR, value="button")
    # by_class = driver.find_element(By.CLASS_NAME, "current-stage").get_attribute("textContent")
    # message = driver.find_element(by=By.ID, value="message")

    containing = driver.find_element(
        by=By.XPATH, value="//*[contains(text(),'Jahre')]"
    )

    # text_box.send_keys("Selenium")
    # submit_button.click()

    text = containing.text

    driver.quit()

    print("Selenium Ergebnis")
    print(text)

    return text


def test_a():
    driver = webdriver.Chrome()

    driver.get("https://www.selenium.dev/selenium/web/web-form.html")

    title = driver.title

    driver.implicitly_wait(0.5)

    text_box = driver.find_element(by=By.NAME, value="my-text")
    submit_button = driver.find_element(by=By.CSS_SELECTOR, value="button")

    text_box.send_keys("Selenium")
    submit_button.click()

    message = driver.find_element(by=By.ID, value="message")
    text = message.text

    driver.quit()

    print("Selenium Ergebnis")
    print(text)
