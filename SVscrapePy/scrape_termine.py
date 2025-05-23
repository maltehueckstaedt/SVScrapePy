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