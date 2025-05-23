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