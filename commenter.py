#!/usr/bin/env python3
import time
import logging
import os
import json
import uuid
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuratie ---
WALLET_FILE = "wallet.json"
LOG_FILE = "pump_fun_tracker.log"
# Indien je op een headless server werkt, zet HEADLESS op True
HEADLESS = True

# --- Logging setup ---
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def kill_existing_chrome_processes():
    """Probeert bestaande Chrome-processen te beëindigen om profielconflicten te vermijden."""
    try:
        logging.info("Killing existing Chrome processes...")
        # pkill -f chrome kan agressief zijn, maar op een dedicated server is dat vaak acceptabel.
        subprocess.run(["pkill", "-f", "chrome"], check=False)
        time.sleep(2)  # Wacht even tot processen daadwerkelijk beëindigd zijn.
    except Exception as e:
        logging.error(f"Error killing Chrome processes: {e}")

# --- Controleer of wallet.json aanwezig is ---
if not os.path.exists(WALLET_FILE):
    raise Exception("Wallet file not found. Generate one using the wallet generator.")

with open(WALLET_FILE, "r") as f:
    try:
        wallet = json.load(f)
    except json.JSONDecodeError as e:
        raise Exception(f"Error decoding {WALLET_FILE}: {e}")

SOLANA_PUBLIC_KEY = wallet.get("public_key")
SOLANA_SECRET_KEY = wallet.get("secret_key")
if not SOLANA_PUBLIC_KEY or not SOLANA_SECRET_KEY:
    raise Exception("Invalid wallet.json: missing keys.")

# --- Selenium en Chrome setup ---
kill_existing_chrome_processes()

chrome_options = Options()
# Kies een unieke gebruikersprofielmap om conflicten te voorkomen
unique_profile = f"selenium_profile_{uuid.uuid4()}"
profile_path = os.path.join(os.getcwd(), unique_profile)
chrome_options.add_argument(f"--user-data-dir={profile_path}")

# Zet opties om detectie te verminderen
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

# Indien headless gewenst (voor servers zonder GUI)
if HEADLESS:
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

# Extra beveiligingsopties kunnen hier worden toegevoegd

# Installeer en start de driver
try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
except Exception as e:
    logging.error(f"Error initializing ChromeDriver: {e}")
    raise

tracked_coins = set()

def login_with_wallet():
    try:
        driver.get("https://pump.fun/login")
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Wallet Login")]'))
        )
        login_button.click()
        time.sleep(2)
        secret_key_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Enter your secret key"]'))
        )
        secret_key_str = json.dumps(SOLANA_SECRET_KEY)
        secret_key_input.send_keys(secret_key_str)
        submit_button = driver.find_element(By.XPATH, '//button[contains(text(), "Submit")]')
        submit_button.click()
        time.sleep(5)
        msg = f"Logged in with Solana wallet {SOLANA_PUBLIC_KEY}"
        print(msg)
        logging.info(msg)
    except Exception as e:
        logging.error(f"Wallet login failed: {e}")
        print(f"Wallet login failed: {e}")

def get_coins():
    """Haalt de coins op van de pump.fun board."""
    try:
        driver.get("https://pump.fun/board")
        time.sleep(5)
        coin_list_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@data-sentry-component="CoinList"]'))
        )
        coins = coin_list_div.find_elements(By.XPATH, './div')
        detected_coins = {}
        for coin in coins:
            coin_id = coin.get_attribute("id")
            coin_name = coin.text.split("\n")[0]
            coin_url = f"https://pump.fun/coin/{coin_id}"
            if coin_id and coin_name:
                detected_coins[coin_id] = (coin_name, coin_url)
        return detected_coins
    except Exception as e:
        logging.error(f"Error retrieving coins: {e}")
        return {}

def leave_comment(coin_url):
    """Bezoekt de coinpagina en plaatst een commentaar."""
    try:
        driver.get(coin_url)
        time.sleep(5)
        coin_name_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "text-[#F8FAFC]") and contains(@class, "font-medium")]'))
        )
        coin_name = coin_name_element.text.split("(")[0].strip()
        print(f"✅ Extracted coin name: {coin_name}")
        post_reply_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "post a reply") and contains(@class, "cursor-pointer")]'))
        )
        post_reply_button.click()
        print(f"✅ Clicked 'Post a reply' button for {coin_name}")
        time.sleep(2)
        comment_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//textarea[@id="text" and contains(@placeholder, "comment")]'))
        )
        print(f"✅ Found comment box for {coin_name}")
        comment_text = f"This coin, {coin_name}, looks interesting!"
        comment_box.send_keys(comment_text)
        time.sleep(2)
        post_reply_button_final = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "post reply") and contains(@class, "bg-green-400")]'))
        )
        driver.execute_script("arguments[0].click();", post_reply_button_final)
        print(f"✅ Clicked 'Post reply' button for {coin_name}")
        time.sleep(3)
        msg = f"💬 Comment posted on {coin_name}: {comment_text}"
        print(msg)
        logging.info(f"Commented on {coin_name}: {comment_text}")
    except Exception as e:
        logging.error(f"Failed to post comment on {coin_url}: {e}")
        print(f"❌ Failed to post comment on {coin_url}. Error: {e}")

def track_pump_fun():
    """Logt in via de wallet en gaat vervolgens de board monitoren."""
    login_with_wallet()
    while True:
        try:
            new_coins = get_coins()
            for coin_id, (name, url) in new_coins.items():
                if coin_id not in tracked_coins:
                    tracked_coins.add(coin_id)
                    log_message = f"New coin detected, URL: {url}"
                    print(log_message)
                    logging.info(log_message)
                    leave_comment(url)
            time.sleep(10)
        except Exception as e:
            logging.error(f"Error accessing pump.fun: {e}")
            time.sleep(60)

if __name__ == "__main__":
    try:
        track_pump_fun()
    except KeyboardInterrupt:
        print("Script interrupted by user. Exiting...")
        logging.info("Script interrupted by user.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        # Zorg dat de driver netjes wordt afgesloten
        try:
            driver.quit()
        except Exception:
            pass
