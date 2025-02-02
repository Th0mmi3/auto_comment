import time
import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys

# Configure logging
logging.basicConfig(filename="pump_fun_tracker.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Set up Chrome WebDriver with a unique Selenium profile
chrome_options = Options()

# Use a separate Selenium profile to stay logged in
profile_path = os.path.join(os.getcwd(), "selenium_profile")
if not os.path.exists(profile_path):
    os.makedirs(profile_path)

chrome_options.add_argument(f"--user-data-dir={profile_path}")  # Use isolated profile

# Avoid bot detection
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

# Start WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Track seen coins to avoid duplicates
tracked_coins = set()

def get_coins():
    """Extracts all coins currently on the board."""
    try:
        driver.get("https://pump.fun/board")
        time.sleep(5)

        coin_list_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@data-sentry-component="CoinList"]'))
        )
        coins = coin_list_div.find_elements(By.XPATH, './div')  # Each coin is a direct child <div>

        detected_coins = {}
        for coin in coins:
            coin_id = coin.get_attribute("id")  # Unique ID for each coin
            coin_name = coin.text.split("\n")[0]  # Extract name
            coin_url = f"https://pump.fun/coin/{coin_id}"  # Construct the URL

            if coin_id and coin_name:
                detected_coins[coin_id] = (coin_name, coin_url)
        return detected_coins

    except Exception as e:
        logging.error(f"Error retrieving coins: {e}")
        return {}

def leave_comment(coin_url):
    """Navigates to the coin page, extracts the correct coin name, and posts a comment."""
    try:
        driver.get(coin_url)
        time.sleep(5)  # Allow time for page to load

        # Step 1: Extract the actual coin name from the coin page
        coin_name_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "text-[#F8FAFC]") and contains(@class, "font-medium")]'))
        )
        coin_name = coin_name_element.text.split("(")[0].strip()  # Extract only the name (remove supply info)
        print(f"✅ Extracted coin name: {coin_name}")

        # Step 2: Click "Post a reply" to open the comment box
        post_reply_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "post a reply") and contains(@class, "cursor-pointer")]'))
        )
        post_reply_button.click()
        print(f"✅ Clicked 'Post a reply' button for {coin_name}")
        time.sleep(2)  # Allow comment box to appear

        # Step 3: Locate the <textarea> for writing the comment
        comment_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//textarea[@id="text" and contains(@placeholder, "comment")]'))
        )
        print(f"✅ Found comment box for {coin_name}")

        # Step 4: Enter comment text
        comment_text = f"This coin, {coin_name}, looks interesting!"
        comment_box.send_keys(comment_text)
        time.sleep(2)  # Simulate human delay

        # Step 5: Click the "post reply" button (force-click if needed)
        post_reply_button_final = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "post reply") and contains(@class, "bg-green-400")]'))
        )
        driver.execute_script("arguments[0].click();", post_reply_button_final)  # Force-click
        print(f"✅ Clicked 'Post reply' button for {coin_name}")

        time.sleep(3)  # Wait for comment to post

        print(f"💬 Comment posted on {coin_name}: {comment_text}")
        logging.info(f"Commented on {coin_name}: {comment_text}")

    except Exception as e:
        logging.error(f"Failed to post comment on {coin_url}: {e}")
        print(f"❌ Failed to post comment on {coin_url}. Error: {e}")



def track_pump_fun():
    """Continuously monitors the pump.fun board for new coins and comments on them."""
    while True:
        try:
            new_coins = get_coins()
            
            for coin_id, (name, url) in new_coins.items():
                if coin_id not in tracked_coins:
                    tracked_coins.add(coin_id)
                    log_message = f"New coin detected, URL: {url}"
                    print(log_message)
                    logging.info(log_message)

                    # Leave a comment on the new coin's page
                    leave_comment(url)

            time.sleep(10)  # Check for new coins every 10 seconds
            
        except Exception as e:
            logging.error(f"Error accessing pump.fun: {e}")
            time.sleep(60)  # Wait before retrying in case of failure

# Run tracker
if __name__ == "__main__":
    track_pump_fun()
