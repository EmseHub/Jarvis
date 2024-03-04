import time
import re

import os.path

import pickle

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait

from selenium.common import NoSuchElementException, ElementNotInteractableException

from helpers.helpers import (
    parse_string_from_textfile,
    parse_object_from_jsonfile,
    write_object_to_jsonfile,
)

BROWSER_DATA_PATH = "jarvis/tasks/agents/selenium_lib/browser_data"
SELENIUM_SCRIPTS_PATH = "jarvis/tasks/agents/selenium_lib/browser_scripts"


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
    local_storage = driver.execute_script(
        parse_string_from_textfile(SELENIUM_SCRIPTS_PATH + "/export_local_storage.js")
    )
    if local_storage is not None:
        # pickle.dump(local_storage, open(filepath, "wb"))
        write_object_to_jsonfile(filepath, local_storage)


def load_local_storage(driver, name_website, is_refreshing_website=True):
    filepath = f"{BROWSER_DATA_PATH}/local_storage_{name_website}.json"
    if os.path.exists(filepath):
        print("local_storage da")
        # local_storage = pickle.load(open(filepath, "rb"))
        local_storage = parse_object_from_jsonfile(filepath)
        driver.execute_script(
            parse_string_from_textfile(SELENIUM_SCRIPTS_PATH + "/import_local_storage.js"),
            local_storage,
        )
        if is_refreshing_website:
            driver.refresh()
        return True
    return False


def save_session_storage(driver, name_website):
    filepath = f"{BROWSER_DATA_PATH}/session_storage_{name_website}.json"
    session_storage = driver.execute_script(
        parse_string_from_textfile(SELENIUM_SCRIPTS_PATH + "/export_session_storage.js")
    )
    if session_storage is not None:
        write_object_to_jsonfile(filepath, session_storage)


def load_session_storage(driver, name_website, is_refreshing_website=True):
    filepath = f"{BROWSER_DATA_PATH}/session_storage_{name_website}.json"
    if os.path.exists(filepath):
        print("session_storage da")
        session_storage = parse_object_from_jsonfile(filepath)
        driver.execute_script(
            parse_string_from_textfile(SELENIUM_SCRIPTS_PATH + "/import_session_storage.js"),
            session_storage,
        )
        if is_refreshing_website:
            driver.refresh()
        return True
    return False


def save_indexed_db(driver, name_website):
    filepath = f"{BROWSER_DATA_PATH}/indexed_db_{name_website}.json"
    # arguments[arguments.length - 1] (last argument) is used by Selenium as callback funktion
    indexed_db = driver.execute_async_script(
        parse_string_from_textfile(SELENIUM_SCRIPTS_PATH + "/export_indexed_db.js")
    )
    if indexed_db is not None:
        write_object_to_jsonfile(filepath, indexed_db)


def load_indexed_db(driver, name_website, is_refreshing_website=True):
    filepath = f"{BROWSER_DATA_PATH}/indexed_db_{name_website}.json"

    if os.path.exists(filepath):
        print("indexed_db da")
        indexed_db = parse_object_from_jsonfile(filepath)
        # arguments[arguments.length - 1] (last argument) is used by Selenium as callback funktion
        driver.execute_async_script(
            parse_string_from_textfile(SELENIUM_SCRIPTS_PATH + "/import_indexed_db.js"), indexed_db
        )
        if is_refreshing_website:
            driver.refresh()
        return True
    return False


def save_cache_storage(driver, name_website):
    filepath = f"{BROWSER_DATA_PATH}/cache_storage_{name_website}.json"
    # arguments[arguments.length - 1] (last argument) is used by Selenium as callback funktion
    cache_storage = driver.execute_async_script(
        parse_string_from_textfile(SELENIUM_SCRIPTS_PATH + "/export_cache_storage.js")
    )
    if cache_storage is not None:
        # write_object_to_jsonfile(filepath, cache_storage)
        write_object_to_jsonfile(filepath, cache_storage, ensure_ascii=False)


def load_cache_storage(driver, name_website, is_refreshing_website=True):
    filepath = f"{BROWSER_DATA_PATH}/cache_storage_{name_website}.json"

    if os.path.exists(filepath):
        print("cache_storage da")
        cache_storage = parse_object_from_jsonfile(filepath)
        # arguments[arguments.length - 1] (last argument) is used by Selenium as callback funktion
        driver.execute_async_script(
            parse_string_from_textfile(SELENIUM_SCRIPTS_PATH + "/import_cache_storage.js"),
            cache_storage,
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
    save_cache_storage(driver, name_website)


def load_browser_data(driver, name_website, is_refreshing_website=True):

    is_cookies_loaded = load_cookies(driver, name_website, False)
    is_local_storage_loaded = load_local_storage(driver, name_website, False)
    is_session_storage_loaded = load_session_storage(driver, name_website, False)
    is_indexed_db_loaded = load_indexed_db(driver, name_website, False)
    is_cache_storage_loaded = load_cache_storage(driver, name_website, False)

    if (
        is_cookies_loaded
        or is_local_storage_loaded
        or is_session_storage_loaded
        or is_indexed_db_loaded
        or is_cache_storage_loaded
    ):
        if is_refreshing_website:
            driver.refresh()
        return True
    return False
