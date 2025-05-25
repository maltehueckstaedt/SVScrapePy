import time
from selenium.webdriver.common.by import By

def click_next_page(driver, css_next_page="#genSearchRes\\:id3f3bd34c5d6b1c79\\:id3f3bd34c5d6b1c79Navi2next", max_attempts=10):
    for attempt in range(1, max_attempts + 1):


        # Seite nach unten scrollen
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        try:
            weiter_button = driver.find_element(By.CSS_SELECTOR, css_next_page)
            weiter_button.click()
            time.sleep(3)
        except Exception as e:
            continue

        # Prüfe, ob wieder auf der Übersichtsseite (nach erfolgreichem Klick)
        try:
            driver.find_element(By.CSS_SELECTOR, "#genSearchRes\\:genericSearchResult > div.text_white_searchresult > span")
            break
        except:
            continue

import re
import pandas as pd

def clean_prefixes(df):
    for col in df.columns:
        col_str = str(col).strip()
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(f"^{re.escape(col_str)}", "", regex=True)
            .str.strip()
            .replace("nan", pd.NA)
        )
    return df

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def select_semester_and_set_courses(driver, base_url, num_sem_selector, num_courses,
                                     css_sem_dropdown, css_search_field, num_courses_selector):
    try:
        driver.get(base_url)
        time.sleep(1)

        # Dropdown klicken
        dropdown = driver.find_element(By.CSS_SELECTOR, css_sem_dropdown)
        dropdown.click()
        time.sleep(0.5)

        # Dynamischen Selector bauen
        base_selector = css_sem_dropdown.rsplit("_", 1)[0]
        full_selector = f"{base_selector}_{num_sem_selector}"
        semester = driver.find_element(By.CSS_SELECTOR, full_selector)
        semester.click()
        time.sleep(0.5)

        # Suche auslösen
        search_field = driver.find_element(By.CSS_SELECTOR, css_search_field)
        search_field.click()
        search_field.send_keys(Keys.ENTER)
        time.sleep(1)

        # Seite nach oben scrollen
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.2)

        # Eingabefeld leeren + neue Kursanzahl setzen
        input_field = driver.find_element(By.CSS_SELECTOR, num_courses_selector)
        input_field.send_keys(Keys.CONTROL + "a")
        input_field.send_keys(Keys.BACKSPACE)
        input_field.send_keys(str(num_courses))
        input_field.send_keys(Keys.ENTER)
        time.sleep(1)

        print("✔️ Fertig.")

    except Exception as e:
        print(f"❌ Fehler: {e}")
        return