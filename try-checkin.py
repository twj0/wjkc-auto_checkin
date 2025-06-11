from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options  # <-- 导入Options模块
import time

# --- 1. 配置您的账户信息 ---
USERNAME = "jjiliang62@gmail.com"
PASSWORD = "123456wjkc" # <--- 请务必在这里填入您的密码
# -----------------------------

LOGIN_URL = "https://wjkc.lol/login#/login"

def run_local_selenium_test():
    print("--- 启动【修复版-本地测试】Selenium脚本 ---")
    
    # --- 关键修复步骤: 添加Chrome启动选项 ---
    options = Options()
    # 这个参数是解决问题的核心，它命令浏览器忽略SSL证书相关的错误
    options.add_argument('--ignore-certificate-errors')
    # 为了确保浏览器窗口足够大，所有元素可见，我们让它最大化启动
    options.add_argument('--start-maximized')
    
    print(">> [步骤1] 正在以“宽容模式”启动Chrome浏览器...")
    try:
        service = ChromeService(ChromeDriverManager().install())
        # 在启动时，将我们设置好的options参数应用进去
        driver = webdriver.Chrome(service=service, options=options)
        print("   ✅ 浏览器启动成功！")
    except Exception as e:
        print(f"   ❌ 浏览器启动失败！错误: {e}")
        return

    try:
        print("\n>> [步骤2] 正在导航至登录页面...")
        driver.get(LOGIN_URL)
        wait = WebDriverWait(driver, 20)
        
        print("   > 正在输入邮箱...")
        email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='邮箱']")))
        email_input.send_keys(USERNAME)

        print("   > 正在输入密码...")
        password_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='密码']")
        password_input.send_keys(PASSWORD)
        
        print("   > 正在点击登录按钮...")
        login_button = driver.find_element(By.XPATH, "//button[contains(span, '登 录')]")
        login_button.click()

        print("\n>> [步骤3] 登录成功，等待签到按钮出现...")
        checkin_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(span, '每日签到')]")))
        
        print("   > 签到按钮已出现，正在点击...")
        checkin_button.click()
        
        print("   > 签到完成！正在等待服务器的提示信息...")
        success_toast = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '成功') or contains(text(), '已签到')]")))
        
        print("\n" + "="*40)
        print("   🎉🎉🎉 **本地测试成功！** 🎉🎉🎉")
        print(f"   ✅ 脚本在您的电脑上成功完成了签到！")
        print(f"   服务器的提示信息是: 【{success_toast.text}】")
        print("="*40)

    except Exception as e:
        print(f"\n❌ 执行失败：在自动化操作过程中发生错误。")
        print(f"   错误详情: {e}")
        # 错误时截图，方便我们看到浏览器卡在了哪一步
        driver.save_screenshot('local_error_screenshot.png')
        print("   (已将浏览器当前画面截图为 local_error_screenshot.png)")
    finally:
        print("\n>> [步骤4] 测试完成，将在10秒后自动关闭浏览器...")
        time.sleep(10)
        driver.quit()

if __name__ == "__main__":
    if "your_password_here" in PASSWORD:
        print("!! 错误：请先在脚本中填写您的账户密码 !!")
    else:
        run_local_selenium_test()