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