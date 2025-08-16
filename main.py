import re
import csv
import json
import time
import os
import sys
from typing import Dict, Any, List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# ----------------------- Utilitare Chrome -----------------------

def start_chrome_debug() -> bool:
    try:
        import requests
        requests.get("http://127.0.0.1:9222/json", timeout=2)
        print("[INFO] Chrome debugging deja pornit")
        return True
    except Exception:
        print("[INFO] Pornesc Chrome cu remote debugging…")
        if sys.platform.startswith("win"):
            chrome_path = r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        elif sys.platform.startswith("darwin"):
            chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        else:
            chrome_path = "/usr/bin/google-chrome"
        try:
            import subprocess
            subprocess.Popen([
                chrome_path, "--remote-debugging-port=9222",
                "--user-data-dir=" + os.path.join(os.getcwd(), "chrome-debug-profile"),
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)
            return True
        except Exception as e:
            print(f"[WARN] Nu pot porni Chrome cu remote debugging: {e}")
            return False

def setup_driver() -> webdriver.Chrome:
    try:
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        print("[INFO] Conectat la sesiunea Chrome existentă (remote debugging)")
        return driver
    except Exception as e:
        print(f"[WARN] Conectare la remote debug eșuată: {e}")
        print("[INFO] Pornesc o sesiune Chrome nouă…")
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        try:
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception:
            pass
        return driver

# ----------------------- Helperi Selenium -----------------------

def get_text(el) -> str:
    try:
        return el.text.strip()
    except Exception:
        return ""

def safe_find(parent, by, selector):
    try:
        return parent.find_element(by, selector)
    except Exception:
        return None

def safe_finds(parent, by, selector):
    try:
        return parent.find_elements(by, selector)
    except Exception:
        return []

def js_click(driver, element) -> bool:
    try:
        driver.execute_script("arguments[0].click();", element)
        return True
    except Exception:
        try:
            element.click()
            return True
        except Exception:
            return False

# ----------------------- Filtre „All filters” -----------------------

def apply_all_filters(driver: webdriver.Chrome, wait: WebDriverWait, cfg: Dict[str, Any]) -> None:
    try:
        try:
            all_filters_btn = wait.until(EC.element_to_be_clickable((
                By.XPATH,
                '//button[contains(@class, "search-reusables__all-filters-pill-button")] | //button[normalize-space()="All filters"] | //button[contains(. ,"All filters")]'
            )))
            js_click(driver, all_filters_btn)
            print("[INFO] 'All filters' deschis")
            time.sleep(1.5)
        except Exception:
            print("[WARN] Nu am găsit butonul 'All filters'")

        date_id_map = {
            "any": "advanced-filter-timePostedRange-",
            "past_month": "advanced-filter-timePostedRange-r2592000",
            "past_week": "advanced-filter-timePostedRange-r604800",
            "past_24h": "advanced-filter-timePostedRange-r86400",
        }
        date_val = cfg.get("date_posted")
        if date_val is not None:
            target_id = date_id_map.get(str(date_val).lower())
            if target_id:
                try:
                    date_elem = wait.until(EC.presence_of_element_located((By.ID, target_id)))
                    js_click(driver, date_elem)
                    print(f"[INFO] Date posted set: {date_val}")
                except Exception as e:
                    print(f"[WARN] Nu pot seta Date Posted ({target_id}): {e}")

        exp_map = {
            1: 'advanced-filter-experience-1', 2: 'advanced-filter-experience-2',
            3: 'advanced-filter-experience-3', 4: 'advanced-filter-experience-4',
            5: 'advanced-filter-experience-5', 6: 'advanced-filter-experience-6',
        }
        exps = cfg.get("experience_level", [])
        if not isinstance(exps, list): exps = [exps]
        for lvl in exps:
            try:
                target_id = exp_map.get(int(lvl))
            except Exception:
                target_id = None
            if target_id:
                try:
                    exp_elem = wait.until(EC.presence_of_element_located((By.ID, target_id)))
                    js_click(driver, exp_elem)
                    print(f"[INFO] Experience selectat: {lvl}")
                except Exception as e:
                    print(f"[WARN] Nu pot bifa Experience {lvl}: {e}")

        remote_map = {"remote": 'advanced-filter-workplaceType-2', "on-site": 'advanced-filter-workplaceType-1', "hybrid": 'advanced-filter-workplaceType-3'}
        rems = cfg.get("remote", [])
        if not isinstance(rems, list): rems = [rems]
        for r in rems:
            target_id = remote_map.get(str(r).lower())
            if target_id:
                try:
                    rem_elem = wait.until(EC.presence_of_element_located((By.ID, target_id)))
                    js_click(driver, rem_elem)
                    print(f"[INFO] Workplace selectat: {r}")
                except Exception as e:
                    print(f"[WARN] Nu pot bifa Workplace {r}: {e}")

        if str(cfg.get("easy_apply", "")).lower() in ("1", "true", "yes"):
            try:
                elem = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@role="switch" and contains(@id,"easy-apply")]')))
                js_click(driver, elem)
                print("[INFO] Easy Apply activat")
            except Exception:
                print("[WARN] Nu am găsit toggle-ul Easy Apply")

        try:
            show_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-test-reusables-filters-modal-show-results-button="true"]')))
            js_click(driver, show_btn)
            print("[INFO] 'Show results' apăsat")
            time.sleep(2)
        except Exception as e:
            print(f"[WARN] Nu pot apăsa 'Show results': {e}")

    except Exception as e:
        print(f"[ERROR] apply_all_filters: {e}")

# ----------------------- Extractori job -----------------------

def extract_from_card(card) -> Dict[str, Any]:
    data = {"title": "", "company": "", "location": "", "observatii": [], "date_posted": ""}
    try:
        data["title"] = get_text(safe_find(card, By.XPATH, './/a[contains(@class,"job-card-list__title")]'))
        data["company"] = get_text(safe_find(card, By.XPATH, './/div[contains(@class, "artdeco-entity-lockup__subtitle")]'))
        data["location"] = get_text(safe_find(card, By.XPATH, './/li[contains(@class,"job-card-container__metadata-item")]'))
        data["observatii"] = [get_text(b) for b in safe_finds(card, By.XPATH, './/li[contains(@class,"job-card-container__footer-item")]')]
        tm = safe_find(card, By.TAG_NAME, 'time')
        if tm: data["date_posted"] = tm.get_attribute('datetime') or get_text(tm)
    except: pass
    return data

def extract_job_description(driver: webdriver.Chrome) -> str:
    for selector in ['//div[@id="job-details"]', '//div[contains(@class, "jobs-description-content__text")]']:
        try:
            return get_text(WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, selector))))
        except: continue
    return ""

def extract_from_details(driver, wait: WebDriverWait) -> Dict[str, Any]:
    out = {"title": "", "company": "", "location": "", "workplace_type": "", "date_posted": "", "observatii": [], "description": ""}
    try:
        out["title"] = get_text(safe_find(driver, By.XPATH, '//h1[contains(@class, "top-card-layout__title")]'))
        out["company"] = get_text(safe_find(driver, By.XPATH, '//a[contains(@class,"topcard__org-name-link")]'))
        location_container = safe_find(driver, By.XPATH, '//div[contains(@class, "job-details-jobs-unified-top-card__tertiary-description")]')
        if location_container:
            out["location"] = get_text(safe_find(location_container, By.XPATH, './span[1]'))
        subline_text = get_text(safe_find(driver, By.XPATH, '//div[contains(@class,"top-card-layout__second-subline")]'))
        for flag in ["Remote", "On-site", "Hybrid"]:
            if flag.lower() in subline_text.lower():
                out["workplace_type"] = flag
                break
        if safe_find(driver, By.XPATH, '//button[contains(.,"Easy Apply")]'): out["observatii"].append("Easy Apply")
        out["description"] = extract_job_description(driver)
    except: pass
    return out

# ----------------------- Flux principal + suport paginare -----------------------

def load_config() -> Dict[str, Any]:
    try:
        with open("config.json", "r", encoding="utf-8") as f: return json.load(f)
    except Exception:
        print("[ERROR] config.json nu a fost găsit sau este invalid. Folosesc setări implicite.")
        return {"search": "python romania", "pages_max": 3, "output_csv": "jobs_linkedin.csv"}

def ensure_jobs_tab(driver, wait: WebDriverWait, query: str) -> None:
    if "linkedin.com" not in driver.current_url:
        driver.get("https://www.linkedin.com/feed/")
    try:
        search_box = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[contains(@class, "search-global-typeahead__input")]')))
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.ENTER)
        time.sleep(2)
        try:
            js_click(driver, wait.until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Jobs" or .="Jobs"]'))))
            print("[INFO] Filtru Jobs activat")
        except:
            driver.get(f"https://www.linkedin.com/jobs/search/?keywords={query.replace(' ', '%20')}")
            print("[INFO] Am navigat direct la jobs search")
        time.sleep(2)
    except Exception as e:
        print(f"[WARN] Nu pot activa filtrul Jobs: {e}")

def find_next_button(driver):
    xpaths = [
        '//button[@aria-label="View next page" and not(@disabled)]',
        '//button[@aria-label="Next" and not(@disabled)]',
        '//button[contains(@class,"jobs-search-pagination__button--next") and not(@disabled)]',
        '//button[contains(.,"Next") and not(@disabled)]',
    ]
    for xp in xpaths:
        el = safe_find(driver, By.XPATH, xp)
        if el:
            return el
    return None

def get_job_ids_in_panel(panel) -> List[str]:
    ids = []
    try:
        cards = safe_finds(panel, By.XPATH, './/li[@data-occludable-job-id] | .//li[contains(@class,"jobs-search-results__list-item")]')
        for c in cards:
            jid = c.get_attribute('data-occludable-job-id')
            if not jid:
                link = safe_find(c, By.XPATH, './/a[contains(@href,"/jobs/view/")]')
                if link:
                    m = re.search(r"/jobs/view/(\d+)", link.get_attribute('href') or "")
                    if m:
                        jid = m.group(1)
            if jid:
                ids.append(jid)
    except Exception:
        pass
    return ids

def scrape_jobs_by_clicking(driver, wait: WebDriverWait, cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    results, seen_job_ids = [], set()
    pages_max = int(cfg.get("pages_max", 3))
    infinite = pages_max == 0
    page = 0

    while True:
        page += 1
        if not infinite and page > pages_max:
            break
        print(f"--- Procesare Pagina {page}{'' if infinite else '/' + str(pages_max)} ---")

        job_list_panel = None
        try:
            job_list_panel = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//div[contains(@class, "jobs-search-results-list")] | //ul[contains(@class,"jobs-search__results-list")]')
            ))
            prev_count = -1
            stable_counter = 0
            while True:
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", job_list_panel)
                time.sleep(1.2)
                job_cards_now = safe_finds(job_list_panel, By.XPATH, './/li[@data-occludable-job-id] | .//li[contains(@class,"jobs-search-results__list-item")]')
                if len(job_cards_now) == prev_count:
                    stable_counter += 1
                else:
                    stable_counter = 0
                if stable_counter >= 2:
                    break
                prev_count = len(job_cards_now)
            print(f"[INFO] Derulare completă, {prev_count if prev_count>=0 else 0} carduri încărcate.")
        except Exception as e:
            print(f"[WARN] Nu am putut derula lista de joburi: {e}")

        # capturăm lista de job id-uri vizibile pe această pagină
        current_page_job_ids = get_job_ids_in_panel(job_list_panel) if job_list_panel else []
        prev_first_id = current_page_job_ids[0] if current_page_job_ids else None

        job_cards = safe_finds(driver, By.XPATH, '//li[@data-occludable-job-id] | //li[contains(@class,"jobs-search-results__list-item")]')
        if not job_cards:
            print("[WARN] Niciun card gasit pe pagina asta.")
        for card in job_cards:
            link_el = safe_find(card, By.XPATH, './/a[contains(@href, "/jobs/view/")] | .//a[contains(@class,"job-card-list__title")]')
            if not link_el:
                continue
            link = link_el.get_attribute('href')
            job_id_match = re.search(r"/jobs/view/(\d+)", link or "")
            job_id = job_id_match.group(1) if job_id_match else (card.get_attribute("data-occludable-job-id") or "")
            if not job_id or job_id in seen_job_ids:
                continue
            seen_job_ids.add(job_id)

            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link_el)
                time.sleep(0.2)
                js_click(driver, link_el)
            except Exception:
                continue

            try:
                wait.until(EC.presence_of_element_located((
                    By.XPATH, f'//div[contains(@class,"jobs-search__job-details")]//a[contains(@href,"{job_id}")]'
                )), timeout=6)
            except Exception:
                time.sleep(1)

            card_data = extract_from_card(card)
            details = extract_from_details(driver, wait)
            row = {
                "Job ID": job_id,
                "Titlu Job": details.get("title") or card_data.get("title"),
                "Companie": details.get("company") or card_data.get("company"),
                "Locatie": details.get("location") or card_data.get("location"),
                "Tip": details.get("workplace_type"),
                "Link Job": link,
                "Data postare": card_data.get("date_posted"),
                "Observatii": "; ".join(filter(None, set(card_data.get("observatii", []) + details.get("observatii", [])))),
                "Descriere Job": details.get("description"),
            }
            results.append(row)
            print(f"[{len(results):03d}] Extras: {row['Titlu Job'][:70]} — {row['Companie'][:30]}")

        # navigare next — apasă DOAR după ce am preluat toate joburile din pagina curentă
        next_btn = find_next_button(driver)
        if next_btn:
            if not infinite and page >= pages_max:
                print("[INFO] Am atins pages_max — opresc.")
                break
            print("[INFO] Găsit buton Next — o să apăs doar după ce confirm că pagina s-a schimbat.")
            try:
                js_click(driver, next_btn)
            except Exception as e:
                print(f"[WARN] Nu am putut apăsa Next: {e}")
                break

            # așteaptă schimbarea conținutului paginii: primul job id trebuie să fie diferit
            timeout = 12
            start = time.time()
            changed = False
            while time.time() - start < timeout:
                try:
                    new_panel = driver.find_element(By.XPATH, '//div[contains(@class, "jobs-search-results-list")] | //ul[contains(@class,"jobs-search__results-list")]')
                    new_ids = get_job_ids_in_panel(new_panel)
                    if not new_ids:
                        time.sleep(0.4)
                        continue
                    # dacă nu aveam id anterior, considerăm că s-a schimbat
                    if prev_first_id is None or new_ids[0] != prev_first_id:
                        changed = True
                        break
                except Exception:
                    # dacă elementul a devenit stale sau nu găsim, oferim un mic sleep și retry
                    time.sleep(0.4)
                    continue
            if not changed:
                # fallback: dacă nu s-a schimbat după timeout, tot mergem mai departe dar semnalăm
                print("[WARN] Pagina nu s-a schimbat în timpul timeout-ului; continui oricum.")
            time.sleep(1.0)
            continue
        else:
            print("[INFO] Nu am găsit butonul Next — probabil ultima pagină.")
            break

    return results

def save_outputs(rows: List[Dict[str, Any]], cfg: Dict[str, Any]) -> None:
    fieldnames = ["Job ID", "Titlu Job", "Companie", "Locatie", "Tip", "Link Job", "Data postare", "Observatii", "Descriere Job"]
    out_csv = cfg.get("output_csv", "jobs_linkedin.csv")
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"[OK] CSV salvat: {out_csv} ({len(rows)} rânduri)")
    if out_json := cfg.get("output_json"):
        with open(out_json, "w", encoding="utf-8") as jf:
            json.dump(rows, jf, ensure_ascii=False, indent=2)
        print(f"[OK] JSON salvat: {out_json}")

def main():
    cfg = load_config()
    start_chrome_debug()
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)
    try:
        ensure_jobs_tab(driver, wait, cfg.get("search", ""))
        apply_all_filters(driver, wait, cfg)
        time.sleep(2)
        rows = scrape_jobs_by_clicking(driver, wait, cfg)
        if rows:
            save_outputs(rows, cfg)
        else:
            print("[WARN] Nu s-au extras joburi.")
    except Exception as e:
        print(f"[ERROR] Scriptul a eșuat: {e}")
    finally:
        try:
            if hasattr(driver, 'command_executor') and driver.command_executor._url and "127.0.0.1:9222" not in driver.command_executor._url:
                driver.quit()
            else:
                print("[INFO] Remote debugging activ – nu închid browserul sau driverul nu mai este valid.")
        except Exception:
            pass

if __name__ == "__main__":
    main()
