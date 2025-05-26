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
        tab = driver.find_element("css selector", css_tab)
        tab.click()
        time.sleep(sleep_time)
    except WebDriverException:
        return None

    return driver.page_source 

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


def scrape_inhalte(driver,
                   css_inhalte_tab="#detailViewData\\:tabContainer\\:term-planning-container\\:tabs\\:contentsTab > span:nth-child(1)",
                   css_container="#detailViewData\\:tabContainer\\:term-planning-container\\:j_id_6s_13_2_%d_1",
                   css_title_selector="#detailViewData\\:tabContainer\\:term-planning-container\\:j_id_6s_13_2_%d_1\\:collapsiblePanel > div.box_title > div > div.layoutFieldsetTitle.collapseTitle > h2",
                   css_content_selector="#detailViewData\\:tabContainer\\:term-planning-container\\:j_id_6s_13_2_%d_1\\:collapsiblePanel > div.box_content > fieldset",
                   max_attempts=10):

    container_data = pd.DataFrame()

    for attempt in range(1, max_attempts + 1):
        try:
            inhalte_tab = driver.find_element("css selector", css_inhalte_tab)
            inhalte_tab.click()
            time.sleep(1)
        except WebDriverException:
            continue

        elem_open = driver.find_elements("css selector", "button[aria-label='Zuklappen des Abschnitts: Inhalte']")
        if len(elem_open) == 0:
            elem_closed = driver.find_elements("css selector", "a[aria-label='Öffnen des Abschnitts: Inhalte']")
            if len(elem_closed) > 0:
                elem_closed[0].click()
                time.sleep(1)
            else:
                return container_data

        found_containers = 0
        try:
            for i in range(21):
                css = css_container % i
                elements = driver.find_elements("css selector", css)
                if len(elements) > 0:
                    found_containers += 1
        except WebDriverException:
            continue

        if found_containers == 0:
            return container_data

        container_dict = {}

        for i in range(found_containers):
            title_selector = css_title_selector % i
            content_selector = css_content_selector % i

            try:
                titel = driver.find_element("css selector", title_selector)
                content_text = driver.find_element("css selector", content_selector).text
                if titel.text and content_text:
                    container_dict[titel.text] = content_text
            except WebDriverException:
                continue

        if container_dict:
            container_data = pd.DataFrame([container_dict])
            return container_data

    return None


def scrape_data(driver, missing_data, num_sem_selector, file_name, sleep_time=0.5):
    total = len(missing_data)
    result_df = pd.DataFrame()

    base_name = file_name.replace(".csv", "").replace(".pkl", "")
    counter = 1
    while True:
        new_file_name = f"{base_name}_{counter}.pkl"
        if not os.path.exists(new_file_name):
            file_name = new_file_name
            break
        counter += 1

    try:
        progress = tqdm(range(total), desc="Scraping", unit="Kurs")
        for i in progress:
            titel = missing_data.iloc[i]['titel']
            nummer = missing_data.iloc[i]['nummer']
            progress.set_description(f"Scraping: {str(titel)[:50]}")

            try:
                driver.find_element(By.CSS_SELECTOR, "#genericSearchMask\\:search_e4ff321960e251186ac57567bec9f4ce\\:cm_exa_eventprocess_basic_data\\:fieldset\\:inputField_3_abb156a1126282e4cf40d48283b4e76d\\:idabb156a1126282e4cf40d48283b4e76d\\:termSelect_label").click()
                time.sleep(sleep_time)

                css_sem_num = f"#genericSearchMask\\:search_e4ff321960e251186ac57567bec9f4ce\\:cm_exa_eventprocess_basic_data\\:fieldset\\:inputField_3_abb156a1126282e4cf40d48283b4e76d\\:idabb156a1126282e4cf40d48283b4e76d\\:termSelect_{num_sem_selector}"
                driver.find_element(By.CSS_SELECTOR, css_sem_num).click()
                time.sleep(sleep_time)

                driver.find_element(By.CSS_SELECTOR, "#genericSearchMask\\:buttonsBottom\\:toggleSearchShowAllCriteria").click()
                time.sleep(sleep_time)

                feld_titel = driver.find_element(By.CSS_SELECTOR, "#genericSearchMask\\:search_e4ff321960e251186ac57567bec9f4ce\\:cm_exa_eventprocess_basic_data\\:fieldset\\:inputField_0_1ad08e26bde39c9e4f1833e56dcce9b5\\:id1ad08e26bde39c9e4f1833e56dcce9b5")
                feld_titel.clear()
                feld_titel.send_keys(titel)

                start_time = time.time()
                ccs_nummer = None
                while time.time() - start_time < 30:
                    try:
                        ccs_nummer = driver.find_element(By.CSS_SELECTOR, "#genericSearchMask\\:search_e4ff321960e251186ac57567bec9f4ce\\:cm_exa_eventprocess_basic_data\\:fieldset\\:inputField_2_7cc364bde72c1b1262427dc431caece3\\:id7cc364bde72c1b1262427dc431caece3")
                        break
                    except:
                        time.sleep(sleep_time)
                if not ccs_nummer:
                    print(f"[{i}] Kurs nicht gefunden: {titel} ({nummer}) – Feld 'Nummer' nicht erschienen")
                    break

                ccs_nummer.clear()
                if pd.notna(nummer):
                    ccs_nummer.send_keys(str(nummer))
                time.sleep(sleep_time)

                try:
                    driver.find_element(By.CSS_SELECTOR, "#genericSearchMask\\:buttonsBottom\\:search").click()
                except Exception as e:
                    print(f"[{i}] Fehler beim Klicken auf Suche: {e}")
                    break

                start_time = time.time()
                ccs_find = None
                while time.time() - start_time < 30:
                    try:
                        ccs_find = driver.find_element(By.CSS_SELECTOR, "#genSearchRes\\:id3f3bd34c5d6b1c79\\:id3f3bd34c5d6b1c79Table\\:0\\:tableRowAction")
                        break
                    except:
                        time.sleep(sleep_time)
                if not ccs_find:
                    print(f"[{i}] Kein Treffer für Kurs: {titel} ({nummer})")
                    break

                ccs_find.click()
                time.sleep(sleep_time)

                semester = driver.find_element(By.CSS_SELECTOR, "#detailViewData\\:tabContainer\\:term-selection-container\\:termPeriodDropDownList_label").text
                scraping_datum = pd.Timestamp.today().date()

                termine = scrape_termine(driver)
                inhalte = scrape_inhalte(driver)

                # Neuer Aufruf: gesamte HTML-Seite nach Klick laden
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

                driver.find_element(By.CSS_SELECTOR, "#statusLastLink1").click()
                time.sleep(sleep_time)

            except Exception as e:
                print(f"[{i}] Fehler bei Kurs: {titel} ({nummer}): {e}")
                continue

    finally:
        result_df = clean_names(result_df)
        result_df.to_pickle(file_name)
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