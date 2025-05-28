import os
import re
import time
import pandas as pd
from io import StringIO
from bs4 import BeautifulSoup
from tqdm import tqdm
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException

from SVscrapePy.helpers import clean_prefixes, click_next_page, clean_names 


def scrape_studiengaenge_module_html(driver, css_tab, sleep_time=0.5):
    try:
        try_with_retries(lambda: wait_and_click(driver, By.CSS_SELECTOR, css_tab))
        time.sleep(sleep_time)
    except:
        return None
    return driver.page_source


import time
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import re

def scrape_inhalte(driver,
                   css_inhalte_tab="#detailViewData\\:tabContainer\\:term-planning-container\\:tabs\\:contentsTab > span:nth-child(1)",
                   css_container="#detailViewData\\:tabContainer\\:term-planning-container\\:j_id_6s_13_2_%d_1",
                   css_title_selector="#detailViewData\\:tabContainer\\:term-planning-container\\:j_id_6s_13_2_%d_1\\:collapsiblePanel > div.box_title > div > div.layoutFieldsetTitle.collapseTitle > h2",
                   css_content_selector="#detailViewData\\:tabContainer\\:term-planning-container\\:j_id_6s_13_2_%d_1\\:collapsiblePanel > div.box_content > fieldset",
                   max_attempts=10):

    def check_network_errors():
        return False

    def clean_name(name):
        name = name.strip().lower()
        name = re.sub(r"[^a-z0-9_]+", "_", name)
        name = re.sub(r"_+", "_", name)
        name = name.strip("_")
        return name

    for attempt in range(max_attempts):
        print(f"Versuch Registerkarte >>Inhalte<< zu finden Nr. {attempt + 1} von maximal {max_attempts} ...")

        try:
            inhalte_tab = driver.find_element(By.CSS_SELECTOR, css_inhalte_tab)
            inhalte_tab.click()
        except Exception as e:
            print(f"Fehler beim Klicken auf das Inhalte-Tab-Element: {e}")
            if check_network_errors():
                continue

        print("Starte das Scraping der Registerkarte >>Inhalte<<")

        found_containers = 0
        try:
            for i in range(21):
                css = css_container % i
                elements = driver.find_elements(By.CSS_SELECTOR, css)
                if elements:
                    found_containers += 1
        except Exception as e:
            print(f"Fehler beim Zaehlen der Container: {e}")

        if found_containers == 0:
            print("Keine Container gefunden")
            return pd.DataFrame()

        print(f"Anzahl gefundener Container: {found_containers}")
        container_dict = {}

        for i in range(found_containers):
            title_text = None
            content_text = None

            try:
                title_element = driver.find_element(By.CSS_SELECTOR, css_title_selector % i)
                title_text = title_element.text.strip()
            except NoSuchElementException:
                print(f"Fehler: Kein Titelelement fuer Container {i} gefunden")
                if check_network_errors():
                    continue

            try:
                content_element = driver.find_element(By.CSS_SELECTOR, css_content_selector % i)
                content_text = content_element.text.strip()
            except NoSuchElementException:
                print(f"Fehler: Kein Inhaltselement fuer Container {i} gefunden")
                if check_network_errors():
                    continue

            if title_text and content_text:
                container_dict[clean_name(title_text)] = content_text

        return pd.DataFrame([container_dict])

    print(f"Maximale Anzahl an Versuchen ({max_attempts}) erreicht. Scraping wird abgebrochen.")
    return pd.DataFrame()

from SVscrapePy.helpers import wait_and_click
from SVscrapePy.helpers import scrape_termine, wait_and_find, try_with_retries


def scrape_data(driver, missing_data, num_sem_selector, file_name, sleep_time=0.5, base_url=None, driver_restart_fn=None):
    total = len(missing_data)
    result_df = pd.DataFrame()

    try:
        progress = tqdm(range(total), desc="Scraping", unit="Kurs")
        for i in progress:
            if i > 0 and i % 100 == 0 and driver_restart_fn and base_url:
                print(f"[{i}] Neustart des Browsers...")
                driver.quit()
                driver = driver_restart_fn()
                driver.get(base_url)
                time.sleep(5)

            titel = missing_data.iloc[i]['titel']
            nummer = missing_data.iloc[i]['nummer']
            progress.set_description(f"Scraping: {str(titel)[:50]}")

            try:
                wait_and_click(driver, By.CSS_SELECTOR, "#genericSearchMask\\:search_e4ff321960e251186ac57567bec9f4ce\\:cm_exa_eventprocess_basic_data\\:fieldset\\:inputField_3_abb156a1126282e4cf40d48283b4e76d\\:idabb156a1126282e4cf40d48283b4e76d\\:termSelect_label")
                wait_and_click(driver, By.CSS_SELECTOR, f"#genericSearchMask\\:search_e4ff321960e251186ac57567bec9f4ce\\:cm_exa_eventprocess_basic_data\\:fieldset\\:inputField_3_abb156a1126282e4cf40d48283b4e76d\\:idabb156a1126282e4cf40d48283b4e76d\\:termSelect_{num_sem_selector}")
                wait_and_click(driver, By.CSS_SELECTOR, "#genericSearchMask\\:buttonsBottom\\:toggleSearchShowAllCriteria")
                time.sleep(sleep_time)

                feld_titel = wait_and_find(driver, By.CSS_SELECTOR, "#genericSearchMask\\:search_e4ff321960e251186ac57567bec9f4ce\\:cm_exa_eventprocess_basic_data\\:fieldset\\:inputField_0_1ad08e26bde39c9e4f1833e56dcce9b5\\:id1ad08e26bde39c9e4f1833e56dcce9b5")
                feld_titel.clear()
                feld_titel.send_keys(titel)

                ccs_nummer = None
                for _ in range(30):
                    try:
                        ccs_nummer = driver.find_element(By.CSS_SELECTOR, "#genericSearchMask\\:search_e4ff321960e251186ac57567bec9f4ce\\:cm_exa_eventprocess_basic_data\\:fieldset\\:inputField_2_7cc364bde72c1b1262427dc431caece3\\:id7cc364bde72c1b1262427dc431caece3")
                        break
                    except:
                        time.sleep(sleep_time)

                if not ccs_nummer:
                    print(f"[{i}] Kurs nicht gefunden: {titel} ({nummer}) – Feld 'Nummer' nicht erschienen")
                    continue

                ccs_nummer.clear()
                if pd.notna(nummer):
                    ccs_nummer.send_keys(str(nummer))
                time.sleep(sleep_time)

                try:
                    driver.execute_script("let btn = document.getElementById('pwaInstallBtn'); if (btn) { btn.remove(); }")
                    wait_and_click(driver, By.CSS_SELECTOR, "#genericSearchMask\\:buttonsBottom\\:search")
                    time.sleep(sleep_time)
                except Exception as e:
                    print(f"[{i}] Fehler beim Klicken auf Suche: {e}")
                    continue

                ccs_find = None
                for _ in range(30):
                    try:
                        ccs_find = driver.find_element(By.CSS_SELECTOR, "#genSearchRes\\:id3f3bd34c5d6b1c79\\:id3f3bd34c5d6b1c79Table\\:0\\:tableRowAction")
                        break
                    except:
                        time.sleep(sleep_time)

                if not ccs_find:
                    print(f"[{i}] Kein Treffer für Kurs: {titel} ({nummer})")
                    continue

                ccs_find.click()
                time.sleep(sleep_time)

                semester = wait_and_find(driver, By.CSS_SELECTOR, "#detailViewData\\:tabContainer\\:term-selection-container\\:termPeriodDropDownList_label").text
                scraping_datum = pd.Timestamp.today().date()

                termine = scrape_termine(driver)
                inhalte = scrape_inhalte(driver)
                full_html = scrape_studiengaenge_module_html(
                    driver,
                    css_tab="#detailViewData\\:tabContainer\\:term-planning-container\\:tabs\\:modulesCourseOfStudiesTab > span:nth-child(1)",
                    sleep_time=sleep_time
                )

                row_data = {
                    'semester': semester,
                    'scraping_datum': scraping_datum,
                    'titel': titel,
                    'nummer': nummer,
                    'studiengaenge_module_html': full_html
                }

                if isinstance(termine, pd.DataFrame) and not termine.empty:
                    row_data.update(termine.iloc[0].to_dict())
                    row_data.pop("titel", None)
                    row_data.pop("nummer", None)

                if isinstance(inhalte, pd.DataFrame) and not inhalte.empty:
                    row_data['inhalte'] = inhalte

                result_df = pd.concat([result_df, pd.DataFrame([row_data])], ignore_index=True)

                wait_and_click(driver, By.CSS_SELECTOR, "#statusLastLink1")
                time.sleep(sleep_time)

            except Exception as e:
                print(f"[{i}] Fehler bei Kurs: {titel} ({nummer}): {e}")
                continue

    finally:
        result_df = clean_names(result_df)
        result_df.to_csv(file_name, index=False)
        print(f"\nDaten gespeichert in {file_name} mit {len(result_df)} Zeilen.")

    return result_df


import re
import time
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
from tqdm import tqdm
from selenium.webdriver.common.by import By

def scrape_all_pages(driver, css_max_selector, max_pages=None):
    # Seitenanzahl ermitteln
    selector = driver.find_element(By.CSS_SELECTOR, css_max_selector)
    selector_text = selector.text.strip()
    match = re.search(r"\d+$", selector_text)
    if not match:
        raise ValueError("Konnte Seitenzahl nicht extrahieren.")
    select_end = int(match.group())

    if max_pages is not None:
        select_end = min(select_end, max_pages)

    all_tables = []

    for i in tqdm(range(1, select_end + 1), desc="Scraping Seiten", unit="Seite"):
        print(f"\n→ Starte Scraping der Base-Informationen für Seite {i}")

        table_element = driver.find_element(By.CSS_SELECTOR, "#genSearchRes\\:id3f3bd34c5d6b1c79\\:id3f3bd34c5d6b1c79Table")
        table_html = table_element.get_attribute("outerHTML")

        soup = BeautifulSoup(table_html, "html.parser")
        table = pd.read_html(StringIO(str(soup)), header=0, flavor="bs4")[0]
        table = clean_prefixes(table)
        all_tables.append(table)

        click_next_page(driver)
        time.sleep(3)

    return pd.concat(all_tables, ignore_index=True)

def scrape_termine(driver, css_labels=".labelItemLine label", css_answers=".labelItemLine .answer", max_attempts=10):
    for attempt in range(1, max_attempts + 1):
        label_texts, answer_texts = [], []

        try:
            labels = driver.find_elements("css selector", css_labels)
            label_texts = [el.text.strip() for el in labels]

            answers = driver.find_elements("css selector", css_answers)
            answer_texts = [el.text.strip() for el in answers]

        except WebDriverException:
            continue

        if not label_texts and not answer_texts:
            continue

        if label_texts and answer_texts and len(label_texts) == len(answer_texts):
            data = {label: ans for label, ans in zip(label_texts, answer_texts)}
            return pd.DataFrame([data])

    return pd.DataFrame()