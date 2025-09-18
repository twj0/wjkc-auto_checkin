import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def get_wjkc_token(account_name, username, password):
    print(f"--- 正在尝试登录账户: {account_name} ---")
    # 配置 Chrome 选项
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")

    # 尝试从环境变量获取 ChromeDriver 路径，否则使用默认路径
    # 在 GitHub Actions 中，通常会自动安装 ChromeDriver
    driver_path = os.getenv('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver')
    service = Service(executable_path=driver_path)
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get("https://wjkc.lol/auth/login")
        print("已访问登录页面")

        # 等待用户名输入框可见
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "username"))
        )
        
        # 输入用户名和密码
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        
        # 点击登录按钮
        driver.find_element(By.ID, "login").click()
        print("已点击登录按钮")

        # 等待登录成功后的页面跳转，例如等待某个元素出现或者URL变化
        # 这里假设登录成功后会跳转到 /user 页面
        WebDriverWait(driver, 10).until(
            EC.url_contains("/user")
        )
        print("登录成功，已跳转到用户页面")

        # 获取所有 cookies
        cookies = driver.get_cookies()
        wjkc_token = None
        for cookie in cookies:
            if cookie['name'] == 'token':
                wjkc_token = cookie['value']
                break
        
        if wjkc_token:
            print(f"成功获取到 token: {wjkc_token}")
            return wjkc_token
        else:
            print("未找到 token cookie。")
            return None

    except Exception as e:
        print(f"获取 token 过程中发生错误: {e}")
        return None
    finally:
        driver.quit()

if __name__ == "__main__":
    # 示例用法 (在实际运行中，这些应该从环境变量或安全配置中获取)
    # 请勿将敏感信息直接硬编码在代码中
    test_username = os.getenv('WJKC_USERNAME')
    test_password = os.getenv('WJKC_PASSWORD')

    if test_username and test_password:
        token = get_wjkc_token("TestAccount", test_username, test_password)
        if token:
            print(f"获取到的 token 是: {token}")
        else:
            print("未能获取到 token。")
    else:
        print("请设置环境变量 WJKC_USERNAME 和 WJKC_PASSWORD 进行测试。")