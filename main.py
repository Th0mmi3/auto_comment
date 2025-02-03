import time
import logging
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

WALLET_FILE = "wallet.json"
if not os.path.exists(WALLET_FILE):
    raise Exception("Wallet file not found. Generate one using wallet_generator.py.")
with open(WALLET_FILE, "r") as f:
    wallet = json.load(f)
WALLET_ADDRESS = wallet.get("address")
PRIVATE_KEY = wallet.get("private_key")

logging.basicConfig(filename="pump_fun_tracker.log", level=logging.INFO, format="%(asctime)s - %(message)s")

chrome_options = Options()
profile_path = os.path.join(os.getcwd(), "selenium_profile")
if not os.path.exists(profile_path):
    os.makedirs(profile_path)
chrome_options.add_argument(f"--user-data-dir={profile_path}")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

tracked_coins = set()

def login_with_wallet():
    """
    Automatiseert het inloggen via de wallet.
    Let op: de precieze elementen en stappen hangen af van hoe pump.fun het inlogproces heeft ingericht.
    Pas de XPaths en logica aan indien nodig.
    """
    try:
        driver.get("https://pump.fun/login")
        # Wacht tot de knop 'Wallet Login' beschikbaar is (pas XPath indien nodig aan)
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Wallet Login")]'))
        )
        login_button.click()
        time.sleep(2)
        
        # Neem aan dat er een invoerveld is voor het invoeren van de private key
        private_key_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Enter your private key"]'))
        )
        private_key_input.send_keys(PRIVATE_KEY)
        
        submit_button = driver.find_element(By.XPATH, '//button[contains(text(), "Submit")]')
        submit_button.click()
        time.sleep(5)
        print(f"Logged in with wallet {WALLET_ADDRESS}")
        logging.info(f"Logged in with wallet {WALLET_ADDRESS}")
    except Exception as e:
        logging.error(f"Wallet login failed: {e}")
        print(f"Wallet login failed: {e}")

def get_coins():
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
        print(f"💬 Comment posted on {coin_name}: {comment_text}")
        logging.info(f"Commented on {coin_name}: {comment_text}")
    except Exception as e:
        logging.error(f"Failed to post comment on {coin_url}: {e}")
        print(f"❌ Failed to post comment on {coin_url}. Error: {e}")

def track_pump_fun():
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
    track_pump_fun()
