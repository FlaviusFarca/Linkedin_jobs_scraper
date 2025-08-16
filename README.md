# 🚀 LinkedIn Jobs Scraper

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)  
[![Selenium](https://img.shields.io/badge/selenium-automation-green.svg)](https://www.selenium.dev/)  
[![Made with ❤️ by Flav](https://img.shields.io/badge/Made%20with-%E2%9D%A4-red)](https://github.com/<username>)  

Un script Python care automatizează căutarea de joburi pe **LinkedIn** și exportă rezultatele în **CSV** sau **JSON**.  
Ideal pentru studenți, freelanceri sau oricine vrea să își automatizeze job hunting-ul 🕵️‍♂️.

---

## ✨ Features
✔️ Caută joburi pe LinkedIn după keyword-uri (ex. `python romania`)  
✔️ Aplică filtre: experiență, remote/hybrid/on-site, Easy Apply, dată postare  
✔️ Salvează rezultatele în **CSV** și/sau **JSON**  
✔️ Suport pentru paginare automată  
✔️ Rulează Chrome cu *remote debugging* pentru a părea mai “uman” 😏  

---

## 🛠️ Setup

1. Clone repo:
   ```bash
   git clone https://github.com/<username>/linkedin_jobs_scraper.git
   cd linkedin_jobs_scraper
2. Instalează dependențele:
   pip install -r requirements.txt
3. Creează un fișier config.json cu setările:
   {
  "search": "python romania",
  "date_posted": "past_week",
  "experience_level": [1,2],
  "remote": ["remote"],
  "easy_apply": true,
  "pages_max": 3,
  "output_csv": "jobs_linkedin.csv",
  "output_json": "jobs_linkedin.json"
  }
4. Rulează scriptul
   python main.py

| Job ID   | Titlu Job        | Companie | Locatie | Tip    | Link Job | Data postare | Observatii | Descriere Job |
| -------- | ---------------- | -------- | ------- | ------ | -------- | ------------ | ---------- | ------------- |
| 12345678 | Python Developer | Google   | Remote  | Remote | link...  | 2025-08-15   | Easy Apply | ...           |


⚙️ Requirements
  Python 3.8+
  Chrome instalat
  Selenium + webdriver-manager

⚠️ Disclaimer
Acest script este făcut doar pentru scop educațional.
LinkedIn are reguli stricte legate de scraping și automatizare. Folosește-l pe riscul tău ⚡.
