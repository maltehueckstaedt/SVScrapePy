def scrape_module(driver,
                  css_module_tab="#detailViewData\\:tabContainer\\:term-planning-container\\:tabs\\:modulesCourseOfStudiesTab > span:nth-child(1)",
                  css_module_content="#detailViewData\\:tabContainer\\:term-planning-container\\:modules\\:moduleAssignments",
                  max_attempts=10):
    
    zugeordnete_module_tibble = pd.DataFrame()

    for attempt in range(1, max_attempts + 1):
        try:
            module_tab = driver.find_element("css selector", css_module_tab)
            module_tab.click()
        except WebDriverException:
            continue

        try:
            module_element = driver.find_element("css selector", css_module_content)
        except WebDriverException:
            return zugeordnete_module_tibble

        if module_element:
            html = module_element.get_attribute("outerHTML")
            soup = BeautifulSoup(html, "html.parser")
            tables = tables = pd.read_html(StringIO(str(soup)), flavor="bs4")

            if len(tables) >= 2:
                zugeordnete_module_tibble = clean_prefixes(tables[1])
                zugeordnete_module_tibble.columns = zugeordnete_module_tibble.columns.astype(str)
            return zugeordnete_module_tibble

    return zugeordnete_module_tibble