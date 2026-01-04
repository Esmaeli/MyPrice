import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- تنظیمات ---
url = "https://arzdigital.com/coins/"

# --- لیستی از سلکتورها برای تست ---
selectors_to_try = [
    ("Stable XPath (Recommended)", By.XPATH, "//tr[@data-symbol='BTC']/td[3]/span/span"),
    ("CSS Selector", By.CSS_SELECTOR, "#list-price > div.arz-scroll-box > div > table > tbody > tr:nth-child(1) > td.arz-coin-table__rial-price-td.arz-sort-value > span > span"),
    ("ID-based XPath", By.XPATH, '//*[@id="list-price"]/div[2]/div/table/tbody/tr[1]/td[3]/span/span'),
    ("Full XPath", By.XPATH, '/html/body/main/div/section/section[2]/div[3]/section/div[2]/div/table/tbody/tr[1]/td[3]/span/span'),
]

# --- تنظیمات پیشرفته Chrome برای جلوگیری از شناسایی ---
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920,1080")

user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
chrome_options.add_argument(f"user-agent={user_agent}")

chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
chrome_options.add_argument("--log-level=3")

# --- راه‌اندازی درایور ---
try:
    print("Initializing Chrome driver with advanced options...")
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    print("Driver initialized successfully.")
except Exception as e:
    print(f"Error starting driver: {e}")
    raise SystemExit(1)

successful_selector_info = None

try:
    print(f"Connecting to {url}...")
    driver.get(url)

    wait = WebDriverWait(driver, 60)
    print("Page loaded. Trying selectors...")

    # --- پیدا کردن اولین سلکتور موفق ---
    for name, by, value in selectors_to_try:
        print(f"  -> Trying selector: {name}")
        try:
            wait.until(EC.visibility_of_element_located((by, value)))
            successful_selector_info = (name, by, value)
            print(f"Success! Selector '{name}' works.")
            break
        except TimeoutException:
            print(f"     Selector '{name}' failed.")

    if not successful_selector_info:
        raise TimeoutException("No selector could find the BTC price.")

    print("-" * 40)
    print(f"Fetching BTC price using '{successful_selector_info[0]}'")

    # --- دریافت اولین قیمت ---
    price_element = driver.find_element(
        successful_selector_info[1],
        successful_selector_info[2]
    )

    current_price = price_element.text.strip()

    if not current_price:
        raise Exception("Price element found but text is empty.")

    print(f"BTC Price: {current_price}")

    # --- ذخیره در فایل ---
    with open("result.txt", "w", encoding="utf-8") as f:
        f.write(current_price)

    print("Price saved to result.txt")
    print("Script finished successfully.")

except TimeoutException as e:
    print(f"\nTimeout Error: {e}")
except Exception as e:
    print(f"\nUnexpected Error: {e}")
finally:
    try:
        driver.quit()
    except Exception:
        pass
    print("Browser closed.")
