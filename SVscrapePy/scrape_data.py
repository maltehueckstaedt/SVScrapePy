def scrape_data(driver, missing_data, num_sem_selector, file_name):
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
                time.sleep(.5)

                css_sem_num = f"#genericSearchMask\\:search_e4ff321960e251186ac57567bec9f4ce\\:cm_exa_eventprocess_basic_data\\:fieldset\\:inputField_3_abb156a1126282e4cf40d48283b4e76d\\:idabb156a1126282e4cf40d48283b4e76d\\:termSelect_{num_sem_selector}"
                driver.find_element(By.CSS_SELECTOR, css_sem_num).click()
                time.sleep(.5)

                driver.find_element(By.CSS_SELECTOR, "#genericSearchMask\\:buttonsBottom\\:toggleSearchShowAllCriteria").click()
                time.sleep(.5)

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
                        time.sleep(0.5)
                if not ccs_nummer:
                    print(f"[{i}] Kurs nicht gefunden: {titel} ({nummer}) – Feld 'Nummer' nicht erschienen")
                    break

                ccs_nummer.clear()
                if pd.notna(nummer):
                    ccs_nummer.send_keys(str(nummer))
                time.sleep(.5)

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
                        time.sleep(0.5)
                if not ccs_find:
                    print(f"[{i}] Kein Treffer für Kurs: {titel} ({nummer})")
                    break

                ccs_find.click()
                time.sleep(.5)

                semester = driver.find_element(By.CSS_SELECTOR, "#detailViewData\\:tabContainer\\:term-selection-container\\:termPeriodDropDownList_label").text
                scraping_datum = pd.Timestamp.today().date()

                termine = scrape_termine(driver)
                inhalte = scrape_inhalte(driver)
                module = scrape_module(driver)
                studiengaenge = scrape_zugeordnete_studiengaenge(driver)

                row_data = {
                    'semester': semester,
                    'scraping_datum': scraping_datum,
                    'titel': titel,
                    'nummer': nummer,
                }

                if isinstance(termine, pd.DataFrame) and not termine.empty:
                    row_data.update(termine.iloc[0].to_dict())
                    row_data.pop("titel", None)
                    row_data.pop("nummer", None)

                if isinstance(inhalte, pd.DataFrame) and not inhalte.empty:
                    row_data['inhalte'] = inhalte
                if isinstance(module, pd.DataFrame) and not module.empty:
                    row_data['module'] = module
                if isinstance(studiengaenge, pd.DataFrame) and not studiengaenge.empty:
                    row_data['studiengaenge'] = studiengaenge

                result_df = pd.concat([result_df, pd.DataFrame([row_data])], ignore_index=True)

                driver.find_element(By.CSS_SELECTOR, "#statusLastLink1").click()
                time.sleep(.5)

            except Exception as e:
                print(f"[{i}] Fehler bei Kurs: {titel} ({nummer}): {e}")
                continue

    finally:
        result_df = result_df.clean_names()
        result_df.to_pickle(file_name)
        print(f"\nDaten gespeichert in {file_name} mit {len(result_df)} Zeilen.")

    return result_df
