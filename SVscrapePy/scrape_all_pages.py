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