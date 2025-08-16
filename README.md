🚀 LinkedIn Jobs Scraper

Un script Python care automatizează căutarea de joburi pe LinkedIn și exportă rezultatele în CSV sau JSON.
Perfect pentru studenți, freelanceri sau oricine vrea să își automatizeze job hunting-ul 🕵️‍♂️.

✨ Features

🔍 Caută joburi pe LinkedIn după keyword-uri (ex. python romania)

🎯 Aplică filtre: experiență, remote/hybrid/on-site, Easy Apply, dată postare

📑 Salvează rezultatele în CSV și/sau JSON

⏭️ Suport pentru paginare automată

🛡️ Folosește Selenium + Chrome în modul remote debugging

🛠️ Setup

Clone repo:

git clone https://github.com/<username>/linkedin_jobs_scraper.git
cd linkedin_jobs_scraper


Instalează dependențele:

pip install -r requirements.txt


Creează un config.json în care îți pui setările:

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


Rulează scriptul:

python main.py

📂 Output Example

CSV-ul generat arată cam așa:

Job ID	Titlu Job	Companie	Locatie	Tip	Link Job	Data postare	Observatii	Descriere Job
12345678	Python Developer	Google	Remote	Remote	link...	2025-08-15	Easy Apply	...
⚙️ Requirements

Python 3.8+

Chrome instalat

Selenium + webdriver-manager

⚠️ Disclaimer

Acest script este făcut doar pentru scop educațional.
LinkedIn are reguli stricte legate de scraping și automatizare. Folosește-l pe riscul tău ⚡.

🌟 Roadmap

 Export direct în Google Sheets

 Interfață web pentru configurare

 Suport pentru alte site-uri de joburi (ex: Indeed, Glassdoor)

👨‍💻 Made with ❤️ by Flav