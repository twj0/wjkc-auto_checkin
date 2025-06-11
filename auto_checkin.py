# auto_checkin.py (Final version for GitHub Actions)
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def run_selenium_checkin(username, password):
    print(f"--- Starting check-in process for {username} in GitHub Actions environment ---")
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--ignore-certificate-errors") # 在服务器环境中，这个参数依然有益无害

    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        print("  > Headless browser started successfully in the cloud.")
    except Exception as e:
        print(f"  [FATAL] Failed to initialize browser on GitHub Runner: {e}")
        return

    try:
        print("  > Navigating to login page...")
        driver.get("https://wjkc.lol/login#/login")
        wait = WebDriverWait(driver, 30) # 增加等待时间，因为云端网络可能稍慢
        
        print("  > Entering credentials and logging in...")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='邮箱']"))).send_keys(username)
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='密码']").send_keys(password)
        driver.find_element(By.XPATH, "//button[contains(span, '登 录')]").click()

        print("  > Login successful, waiting for check-in button...")
        checkin_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(span, '每日签到')]")))
        
        print("  > Clicking the check-in button...")
        checkin_button.click()
        
        print("  > Waiting for success message...")
        success_toast = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '成功') or contains(text(), '已签到')]")))
        
        print("\n" + "="*40)
        print("  🎉🎉🎉 **MISSION ACCOMPLISHED!** 🎉🎉🎉")
        print(f"  ✅ Account '{username}' successfully checked in via GitHub Actions.")
        print(f"  ✅ Server Response: 【{success_toast.text}】")
        print("="*40)

    except Exception as e:
        print(f"\n❌ An error occurred during the automation process.")
        print(f"   Error details: {e}")
        error_screenshot_path = f'/tmp/error_screenshot_{username}.png'
        driver.save_screenshot(error_screenshot_path)
        print(f"   (A screenshot has been saved to the runner at {error_screenshot_path} for debugging)")
    finally:
        print("  > Closing the browser.")
        driver.quit()

# 从环境变量加载账户信息的函数...
def load_accounts_from_env():
    accounts, i = [], 1
    while True:
        user, password = os.getenv(f'USER{i}'), os.getenv(f'PASS{i}')
        if user and password: accounts.append({'user': user, 'pass': password}); i += 1
        else: break
    return accounts

if __name__ == "__main__":
    accounts = load_accounts_from_env()
    if not accounts: print("No accounts configured in GitHub Secrets (USER1, PASS1, etc.).")
    else:
        print(f"Found {len(accounts)} account(s). Starting automation...")
        for acc in accounts: run_selenium_checkin(acc['user'], acc['pass']); print("-" * 40)
    print("All jobs completed.")