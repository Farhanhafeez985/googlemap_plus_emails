# Google Maps Scraper + Email Extractor

A Python-based automation tool that scrapes business data from Google Maps and optionally extracts emails from business websites.

---

# 📌 Table of Contents

- Project Overview  
- Features  
- Requirements  
- Installation  
- Setup (Windows / macOS / Linux)  
- Input Format  
- How to Run  
- Output Files  
- Automation Mode  
- Notes  

---

# 🚀 Project Overview

This project automates lead generation using Google Maps.

It consists of two main components:

1. **Google Maps Scraper**
   - Extracts business information from Google Maps
   - Saves data into CSV format

2. **Email Scraper (Optional)**
   - Reads generated CSV file
   - Visits websites
   - Extracts additional email addresses

> ⚠️ Note: The first script already extracts emails using a browser extension. The second script improves email coverage.

---

# ✨ Features

- Google Maps business scraping
- Automated scrolling & data extraction
- Email extraction from websites
- CSV-based structured output
- Cross-platform support (Windows / macOS / Linux)
- One-click automation script available

---

# ⚙️ Requirements

- Python 3.10
- Internet connection
- Chromium browser (Playwright)
- Windows / macOS / Linux

---

# 📦 Installation

## 1. Extract Project

Download and unzip the project folder.

---

## 2. Install Dependencies

```bash
pip3 install scrapy
pip3 install openpyxl==3.1.5
pip3 install playwright==1.58.0
pip3 install pyexcel==0.7.4
pip3 install pyexcel-io==0.6.7
pip3 install scrapy-xlsx==0.1.1
```

Install Playwright browsers:

```bash
playwright install
```

---

# 🖥️ Setup

## Windows

Install Python 3.10:

https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe

✔ Add Python to PATH during installation

Verify:
```bash
python --version
```

---

## macOS

Install Python 3.10:

https://www.python.org/ftp/python/3.10.0/python-3.10.0post2-macos11.pkg

Setup:

```bash
pip3 install virtualenv
cd <project-folder>
virtualenv myenv --python=python3.10
source myenv/bin/activate
```

---

## Linux

```bash
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.10 python3-pip
pip3 install virtualenv
```

Setup environment:

```bash
cd <project-folder>
virtualenv myenv --python=python3.10
source myenv/bin/activate
```

---

# 📥 Input Format

Input file must be named:

```bash
input.csv
```

### Format:

```csv
keyword,business_type,city,state,country
Nepali real estate agent,real estate agent,New York City,NY,United States
```

### Notes:

- All columns are required
- Multiple rows supported
- Update file for new scraping campaigns

---

# ▶️ How to Run

Make sure you are inside the project directory (`scrapy.cfg` must exist).

---

## Step 1: Run Google Maps Scraper

### macOS / Linux

```bash
python3 GoogleMap_Scraper.py
```

### Windows

```bash
GoogleMap_Scraper_runner.bat
```

---

## Step 2: Run Email Scraper (Optional)

### macOS / Linux

```bash
scrapy crawl email_spider
```

### Windows

```bash
email_scraper_runner.bat
```

---

# 📤 Output Files

## Google Maps Output
```
Output/
```

## Email Scraper Output
```
Scraped_records_email/
```

---

# 🤖 Automation (Recommended)

A master script is available for full automation.

## What it does

- Runs Google Maps scraper
- Waits for completion
- Runs email scraper automatically
- Produces final output

---

## Run Automation

### macOS / Linux
```bash
python3 master_run.py
```

### Windows
```bash
python master_run.py
```

---

# ⚡ Benefits of Automation

- Single command execution
- No manual intervention
- Ensures correct execution order
- Prevents missing file errors

---

# 📝 Notes

- Keep internet stable during scraping
- Do not close terminal while running scripts
- Do not put system to sleep during execution

---

# ✅ License / Usage

For personal and business automation use.