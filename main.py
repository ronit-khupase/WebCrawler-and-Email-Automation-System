"""
Production-ready lead generation & email automation system.
Uses:
- Google Custom Search API
- Website scraping
- CSV export/import
- Gmail SMTP
- Environment variables (.env)
"""

# =========================================================
# IMPORTS
# =========================================================

import requests
import re
import time
import os
import smtplib
import logging
import pandas as pd

from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from urllib.parse import urlparse
from datetime import datetime
from dotenv import load_dotenv

# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

MAX_GOOGLE_RESULTS = int(os.getenv("MAX_GOOGLE_RESULTS", 100))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 10))
EMAIL_DELAY_SECONDS = int(os.getenv("EMAIL_DELAY_SECONDS", 3))

CSV_OUTPUT_DIR = "output"
LOG_DIR = "logs"

# =========================================================
# DIRECTORY SETUP
# =========================================================

os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# =========================================================
# LOGGING SETUP
# =========================================================

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "system.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# =========================================================
# REGEX PATTERNS
# =========================================================

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_REGEX = r"(\+?\d{1,3}[\s-]?)?\d{10}"
ADDRESS_KEYWORDS = ["address", "location", "office"]

# =========================================================
# UTILITY FUNCTIONS
# =========================================================

def normalize_domain(url: str) -> str:
    """Normalize website domain to detect duplicates"""
    parsed = urlparse(url)
    return parsed.netloc.lower().replace("www.", "")

# =========================================================
# GOOGLE CUSTOM SEARCH
# =========================================================

def google_search(keyword: str) -> list:
    """Fetch website URLs using Google Custom Search API"""
    urls = []
    start = 1

    while start <= MAX_GOOGLE_RESULTS:
        params = {
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_CSE_ID,
            "q": keyword,
            "start": start
        }

        response = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params=params,
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code != 200:
            logger.error("Google Custom Search API failed")
            break

        data = response.json()

        for item in data.get("items", []):
            urls.append(item.get("link"))

        start += 10

    logger.info(f"Google search returned {len(urls)} URLs")
    return urls

# =========================================================
# DUPLICATE WEBSITE FILTER
# =========================================================

def remove_duplicate_websites(urls: list) -> list:
    """Remove duplicate websites based on domain"""
    seen = set()
    unique_urls = []

    for url in urls:
        domain = normalize_domain(url)
        if domain not in seen:
            seen.add(domain)
            unique_urls.append(url)

    return unique_urls

# =========================================================
# WEBSITE SCRAPER
# =========================================================

def scrape_website(url: str) -> dict:
    """Extract business name, email, phone, address from website"""
    data = {
        "business": "",
        "email": "",
        "phone": "",
        "address": "",
        "website": url
    }

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        soup = BeautifulSoup(response.text, "html.parser")

        data["business"] = soup.title.text.strip() if soup.title else ""

        text = soup.get_text(separator=" ")

        emails = re.findall(EMAIL_REGEX, text)
        phones = re.findall(PHONE_REGEX, text)

        data["email"] = emails[0] if emails else ""
        data["phone"] = phones[0] if phones else ""

        for tag in soup.find_all(["p", "div", "span"]):
            content = tag.get_text().lower()
            if any(keyword in content for keyword in ADDRESS_KEYWORDS):
                data["address"] = tag.get_text(strip=True)
                break

    except Exception as e:
        logger.warning(f"Scraping failed for {url}: {e}")

    return data

# =========================================================
# CSV MANAGEMENT
# =========================================================

def export_to_csv(leads: list) -> str:
    """Export leads to CSV file"""
    filename = f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    path = os.path.join(CSV_OUTPUT_DIR, filename)

    pd.DataFrame(leads).to_csv(path, index=False)
    logger.info(f"CSV exported: {path}")

    return path

def import_csv(path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
        if df.empty:
            raise ValueError("CSV file is empty")
        return df
    except Exception as e:
        logger.error(f"CSV import failed: {e}")
        return pd.DataFrame()

# =========================================================
# EMAIL SENDER
# =========================================================

def send_emails_from_csv(df: pd.DataFrame) -> tuple:
    """Send emails using Gmail SMTP"""
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(SMTP_EMAIL, SMTP_PASSWORD)

    sent, failed = 0, 0

    for _, row in df.iterrows():
        if not row.get("email"):
            continue

        try:
            msg = MIMEText(
                f"""Hello {row['business']},

We found your website ({row['website']}) and would like to connect.

Regards,
Ronit Khupase"""
            )
            msg["From"] = SMTP_EMAIL
            msg["To"] = row["email"]
            msg["Subject"] = "Business Collaboration"

            server.sendmail(SMTP_EMAIL, row["email"], msg.as_string())
            sent += 1
            time.sleep(EMAIL_DELAY_SECONDS)

        except Exception as e:
            failed += 1
            logger.error(f"Email failed for {row['email']}: {e}")

    server.quit()
    return sent, failed

# =========================================================
# MAIN CONTROLLER
# =========================================================

def main():
    start_time = time.time()
    user_input = input("Enter keyword / website / CSV file path: ").strip()

    # ---------- CSV IMPORT MODE ----------
    if user_input.lower().endswith(".csv"):
        if not os.path.isfile(user_input):
            print("\n❌ ERROR: CSV file not found.")
            print("Please check the file path and try again.\n")
            logger.error(f"CSV file not found: {user_input}")
            return

        df = import_csv(user_input)

    # ---------- CRAWLING MODE ----------
    # ---------- CRAWLING MODE ----------
    else:
        urls = google_search(user_input)
        unique_urls = remove_duplicate_websites(urls)

        leads = []
        for url in unique_urls:
            lead = scrape_website(url)
            if lead["email"]:
                leads.append(lead)

        if not leads:
            print("\n⚠️ No valid leads found. CSV will not be generated.")
            logger.info("No valid leads found. Stopping execution.")
            return

        csv_path = export_to_csv(leads)

        elapsed = round(time.time() - start_time, 2)

        print("\n----------------------------------")
        print("Crawling Completed Successfully")
        print("----------------------------------")
        print(f"Input : {user_input}")
        print(f"Websites Found : {len(urls)}")
        print(f"Valid Leads : {len(leads)}")
        print(f"Time Taken : {elapsed} sec")
        print(f"CSV Generated : {csv_path}")
        print("----------------------------------")
        print("Starting Email Campaign...\n")

        df = import_csv(csv_path)

    # ---------- EMAIL SAFETY CHECK ----------
    if df.empty:
        print("\n⚠️ No data available for email sending. Exiting safely.")
        logger.info("No data available for email sending.")
        return

    # ---------- EMAIL SENDING ----------
    sent, failed = send_emails_from_csv(df)

    print("----------------------------------")
    print("Email Campaign Completed")
    print("----------------------------------")
    print(f"Emails Sent : {sent}")
    print(f"Failed : {failed}")
    print("----------------------------------")

# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()
