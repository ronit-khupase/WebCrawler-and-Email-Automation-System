# WebCrawler and Email Automation System

A **production-ready lead generation and email automation tool** built using Python.

This system automatically:

* Finds business websites using Google Custom Search API
* Scrapes websites to extract emails, phone numbers, and business details
* Generates a CSV file of leads
* Sends automated outreach emails via Gmail SMTP

The tool can also import an existing CSV file and send emails directly.

---

# Features

* Google Custom Search API integration
* Website scraping using BeautifulSoup
* Email extraction using Regex
* Duplicate website filtering
* CSV export and import support
* Automated email campaigns
* Environment variable support using `.env`
* Logging system for monitoring execution
* Production-ready modular code structure

---

# Tech Stack

* Python
* Requests
* BeautifulSoup
* Pandas
* Regex
* Gmail SMTP
* Google Custom Search API

---

# Project Structure

```
project/
│
├── main.py
├── requirements.txt
├── .env
├── .gitignore
│
├── logs/
│   └── system.log
│
└── output/
    └── leads_YYYYMMDD.csv
```

---

# Installation

Clone the repository:

```
git clone https://github.com/ronit-khupase/WebCrawler-and-Email-Automation-System.git
```

Move into the project folder:

```
cd WebCrawler-and-Email-Automation-System
```

Install dependencies:

```
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the root directory.

Example:

```
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_custom_search_engine_id

SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password

MAX_GOOGLE_RESULTS=100
REQUEST_TIMEOUT=10
EMAIL_DELAY_SECONDS=3
```

**Important:**
Use a **Gmail App Password** instead of your real Gmail password.

---

# How It Works

### Mode 1 — Website Crawling

Run the script:

```
python main.py
```

Enter a keyword such as:

```
digital marketing agency india
```

The system will:

1. Search Google for relevant websites
2. Scrape websites
3. Extract business contact details
4. Generate a CSV file of leads
5. Automatically send outreach emails

---

### Mode 2 — CSV Import

You can also send emails using an existing CSV file.

Example input:

```
leads.csv
```

The system will read the CSV file and send emails to all valid email addresses.

---

# Output Example

```
Crawling Completed Successfully
----------------------------------
Input : digital marketing agency india
Websites Found : 80
Valid Leads : 25
Time Taken : 14 sec
CSV Generated : output/leads_20260310_203500.csv
----------------------------------
Starting Email Campaign...
```

---

# Logging

All system logs are stored in:

```
logs/system.log
```

This helps track:

* API failures
* scraping issues
* email sending errors

---

# Security

Sensitive credentials are stored in `.env` and excluded using `.gitignore`.

Never commit `.env` to GitHub.

---

# Future Improvements

* Multi-threaded scraping for faster crawling
* Email template customization
* Web dashboard for campaign management
* Email tracking and analytics
* Docker containerization

---

# Author

**Ronit Khupase**

GitHub:
https://github.com/ronit-khupase

---

# License

This project is open-source and available under the MIT License.
