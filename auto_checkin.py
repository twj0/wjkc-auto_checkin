# auto_checkin.py (Final Stealth Version for GitHub Actions)
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def run_stealth_checkin(username, password):
    """
    Automates the check-in process using Selenium in Stealth Mode,
    optimized for a GitHub Actions environment.
    """
    print(f"--- Launching Stealth Mode for: {username} ---")
    
    # --- 配置Chrome启动选项，这是所有技术的结晶 ---
    options = Options()
    # 为服务器环境进行的基础配置
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    # 核心的隐身技术选项
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # --- 最核心的隐身技术：在加载任何页面前抹除指纹 ---
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("  > Headless browser launched in Stealth Mode.")
    except Exception as e:
        print(f"  [FATAL] Failed to initialize browser on GitHub Runner: {e}")
        return

    try:
        # --- 正常执行我们的自动化流程 ---
        driver.get("https://wjkc.lol/login#/login")
        wait = WebDriverWait(driver, 30)
        
        print("  > Logging in...")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='邮箱']"))).send_keys(username)
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='密码']").send_keys(password)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(span, '登 录')]"))).click()

        print("  > Login successful, waiting for check-in button...")
        checkin_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(span, '每日签到')]")))
        
        print("  > Clicking the check-in button...")
        checkin_button.click()
        
        print("  > Waiting for success message...")
        success_toast = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '成功') or contains(text(), '已签到')]")))
        
        print("\n" + "="*40)
        print("  🎉🎉🎉 **FINAL VICTORY!** 🎉🎉🎉")
        print(f"  ✅ Account '{username}' successfully checked in via GitHub Actions.")
        print(f"  ✅ Server Response: 【{success_toast.text}】")
        print("="*40)

    except Exception as e:
        print(f"\n❌ An error occurred during the automation process for {username}.")
        print(f"   If this final attempt fails, the website's anti-bot measures are beyond our current tools.")
        print(f"   Error details: {e}")
        # 在云端服务器上保存截图，虽然我们无法直接看到，但如果需要深入调试，这是一个线索
        driver.save_screenshot(f'error_screenshot_{username}.png')
    finally:
        print("  > Closing the browser.")
        driver.quit()

def load_accounts_from_env():
    """从GitHub环境变量加载账户信息"""
    accounts = []
    i = 1
    while True:
        user, password = os.getenv(f'USER{i}'), os.getenv(f'PASS{i}')
        if user and password: accounts.append({'user': user, 'pass': password}); i += 1
        else: break
    return accounts

if __name__ == "__main__":
    accounts = load_accounts_from_env()
    if not accounts: print("No accounts configured in GitHub Secrets (e.g., USER1, PASS1).")
    else:
        print(f"Found {len(accounts)} account(s). Starting automation...")
        for acc in accounts:
            run_stealth_checkin(acc['user'], acc['pass'])
            print("-" * 40)
    print("All jobs completed.")