def scrape_zugeordnete_studiengaenge(driver,
    css_zugeordnete_studiengaenge="#detailViewData\\:tabContainer\\:term-planning-container\\:courseOfStudies\\:courseOfStudyAssignments\\:courseOfStudyAssignmentsTable",
    max_attempts=10):

    zugeord_studgaenge_df = pd.DataFrame()

    for attempt in range(1, max_attempts + 1):
        try:
            element = driver.find_element("css selector", css_zugeordnete_studiengaenge)
        except WebDriverException:
            continue

        if element:
            html = element.get_attribute("outerHTML")
            soup = BeautifulSoup(html, "html.parser")
            tables = tables = pd.read_html(StringIO(str(soup)), flavor="bs4")

            if tables:
                df = clean_prefixes(tables[0])
                df.columns = [
                    re.sub(r"_(sortierbare_spalte|aufwarts_sortieren)", "", col)
                    for col in df.columns.astype(str)
                ]
                if not df.isna().all().all():
                    return df
                else:
                    return zugeord_studgaenge_df

    return zugeord_studgaenge_df
