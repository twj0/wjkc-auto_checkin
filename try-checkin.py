import requests
import json
import base64

# --- 1. 配置您的账户信息 ---
# vvvvv  请在这里填入您那个【新账号】的邮箱和密码  vvvvv
USERNAME = "3150774524@qq.com" # 我已经帮您填好了
PASSWORD = "123456wjkc" # <-- 在这里输入新账号的密码
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

# --- API Endpoints (已验证) ---
LOGIN_URL = "https://wjkc.lol/api/user/login"
CHECKIN_URL = "https://wjkc.lol/api/user/sign_use"

def run_debug_checkin():
    print("--- 本地签到【深度调试模式】---")
    print(f"账户: {USERNAME}")
    print("-" * 30)

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    })

    try:
        # --- 登录 ---
        print("[1] 正在登录...")
        login_response = session.post(LOGIN_URL, json={'email': USERNAME, 'password': PASSWORD})
        login_response.raise_for_status()
        print("[1] ✅ 登录成功！")

        # --- 执行签到 ---
        print("\n[2] 正在执行签到...")
        checkin_response = session.post(CHECKIN_URL, json={"data": "e30="})
        checkin_response.raise_for_status()
        print("[2] ✅ 签到请求已发送！")

        # --- 解码 ---
        print("\n[3] 正在解码服务器响应...")
        encoded_data = checkin_response.json().get('data')
        if not encoded_data:
            raise ValueError("服务器响应中不含'data'字段。")
        final_data = json.loads(base64.b64decode(encoded_data))
        print("[3] ✅ 解码成功！")

        # ---【核心调试代码】---
        # 下面的代码会把解码后的所有内容，原封不动地打印出来
        print("\n" + "="*40)
        print("  解码后的服务器原始数据 (RAW DATA):")
        print("="*40)
        # 使用json.dumps让输出格式更美观，ensure_ascii=False确保中文能正常显示
        print(json.dumps(final_data, indent=2, ensure_ascii=False))
        print("="*40)

    except Exception as e:
        print(f"\n❌ 执行失败：发生错误。")
        print(f"   错误详情: {e}")


if __name__ == "__main__":
    if "your_new_account_password" in PASSWORD:
        print("!! 错误：请在脚本中填写您的新账号密码 !!")
    else:
        # 确保您是用一个【从未签到过】的新账号来运行此脚本！
        # 如果不确定，请再注册一个全新的账号来测试。
        run_debug_checkin()