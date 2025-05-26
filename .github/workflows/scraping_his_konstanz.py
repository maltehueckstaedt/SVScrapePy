from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from SVscrapePy.helpers import (
    click_next_page,
    clean_prefixes,
    select_semester_and_set_courses
)
from SVscrapePy.scrapers import (
    scrape_all_pages,
    scrape_data
)
import pandas as pd
import janitor
import re
import time

# Selenium Chrome Optionen
options = Options()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# WebDriver starten
driver = webdriver.Chrome(options=options)

# Parameter für das Scraping
base_url = "https://zeus.uni-konstanz.de/hioserver/pages/startFlow.xhtml?_flowId=searchCourseNonStaff-flow&_flowExecutionKey=e1s1"
sem_dropdown = "#genericSearchMask\\:search_e4ff321960e251186ac57567bec9f4ce\\:cm_exa_eventprocess_basic_data\\:fieldset\\:inputField_3_abb156a1126282e4cf40d48283b4e76d\\:idabb156a1126282e4cf40d48283b4e76d\\:termSelect_label"
num_sem_selector = 3
num_courses_selector = "#genSearchRes\\:id3f3bd34c5d6b1c79\\:id3f3bd34c5d6b1c79Navi2NumRowsInput"
num_courses = "300"
search_field = "#genericSearchMask\\:search_e4ff321960e251186ac57567bec9f4ce\\:cm_exa_eventprocess_basic_data\\:fieldset\\:inputField_0_1ad08e26bde39c9e4f1833e56dcce9b5\\:id1ad08e26bde39c9e4f1833e56dcce9b5"

# Scraping starten
select_semester_and_set_courses(driver, base_url, num_sem_selector, num_courses,
                                sem_dropdown, search_field, num_courses_selector)

css_max_selector = "#genSearchRes\\:id3f3bd34c5d6b1c79\\:id3f3bd34c5d6b1c79Navi2_div > div > span.dataScrollerPageText"
base_info = scrape_all_pages(driver, css_max_selector, max_pages=None)

# Vorverarbeitung
base_info = base_info.clean_names().rename(columns={"titel_der_veranstaltung": "titel"})
base_info["titel"] = (
    base_info["titel"]
    .str.replace(r"[()|+\-!\".=*„“]", " ", regex=True)
    .str.replace("İ", "", regex=False)
    .str.slice(0, 250)
)

# Reset und Detail-Scraping
driver.delete_all_cookies()
driver.get(base_url)

df = scrape_data(driver, base_info, num_sem_selector="3", sleep_time=0.5,
                 file_name="courses_w2024_Konstanz.csv")

# Speichern
df.to_csv("courses_w2024_Konstanz.csv", index=False)
driver.quit()