# -*- coding: utf-8 -*-
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# ---------------- Configuration ----------------
BASE_URL = "https://arzdigital.com/coins/"
PAGES = 10
OUTPUT_FILE = "arzdigital_data.txt"
WAIT_AFTER_LOAD = 1  # seconds

# ---------------- Selenium setup ----------------
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)
driver.execute_script(
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
)

# ---------------- Helper functions ----------------
def get_text_safe(el):
    return el.get_text(strip=True) if el else "N/A"

def get_change_text(el):
    if not el:
        return "N/A"
    text = el.get_text(strip=True)
    classes = el.get("class", [])
    if "arz-positive" in classes:
        return f"+{text}"
    if "arz-negative" in classes and not text.startswith("-"):
        return f"-{text}"
    return text

# ---------------- Main logic ----------------
all_coins = []

try:
    for page in range(1, PAGES + 1):
        url = BASE_URL if page == 1 else f"{BASE_URL}page-{page}/"
        print(f"Loading page {page}: {url}")

        driver.get(url)

        # صبر تا جدول لود شود
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "tr.arz-coin-tr"))
        )

        print("Page loaded, waiting extra 10 seconds for JS...")
        time.sleep(WAIT_AFTER_LOAD)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        rows = soup.find_all("tr", class_="arz-coin-tr")

        print(f"Found {len(rows)} coins on page {page}")

        for row in rows:
            symbol = row.get("data-symbol", "N/A")

            rank = get_text_safe(row.find("td", class_="arz-coin-table__number-td"))

            name_td = row.find("td", class_="arz-coin-table__name-td")
            name = get_text_safe(name_td.find("span")) if name_td else "N/A"

            logo_img = name_td.find("img", class_="arz-coin-image") if name_td else None
            logo = logo_img.get("data-src", "N/A") if logo_img else "N/A"

            price_usd = get_text_safe(
                row.find("td", class_="arz-coin-table__price-td")
            )

            rial_td = row.find("td", class_="arz-coin-table__rial-price-td")
            price_toman = get_text_safe(
                rial_td.find("span").find("span") if rial_td else None
            )

            market_td = row.find("td", class_="arz-coin-table__marketcap-td")
            market_usd = get_text_safe(market_td.find("span", dir="auto"))
            market_toman = get_text_safe(market_td.find("span", class_="arz-value-unit"))

            volume_td = row.find("td", class_="arz-coin-table__volume-td")
            volume_usd = get_text_safe(volume_td.find("span", dir="auto"))
            volume_toman = get_text_safe(volume_td.find("span", class_="arz-value-unit"))

            daily_td = row.find("td", class_="arz-coin-table__daily-swing-td")
            daily_change = get_change_text(daily_td.find("span") if daily_td else None)

            weekly_td = row.find("td", class_="arz-coin-table__weekly-swing-td")
            weekly_change = get_change_text(weekly_td.find("span") if weekly_td else None)

            all_coins.append({
                "Rank": rank,
                "Name": name,
                "Slug": symbol,
                "Price_USD": price_usd,
                "Price_Toman": price_toman,
                "Total_Market_USD": market_usd,
                "Total_Market_Toman": market_toman,
                "Daily_Market_USD": volume_usd,
                "Daily_Market_Toman": volume_toman,
                "Daily_Positive_Negative": daily_change,
                "Weekly_Positive_Negative": weekly_change,
                "Logo": logo,
            })

finally:
    driver.quit()

# ---------------- Write file ----------------
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for i, coin in enumerate(all_coins):
        for k, v in coin.items():
            f.write(f"{k}: {v}\n")
        if i < len(all_coins) - 1:
            f.write("***\n***\n***\n")

print(f"Saved {len(all_coins)} coins to {OUTPUT_FILE}")
