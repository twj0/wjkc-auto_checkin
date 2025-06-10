import requests
import json
import base64

# --- 1. 配置您的账户信息 ---
# vvvvv  请在这里填入您的邮箱和密码  vvvvv
DOMAIN = "https://wjkc.lol"
USERNAME = ""  # <-- 1. PUT YOUR EMAIL HERE
PASSWORD = "123456wjkc"          # <-- 2. PUT YOUR PASSWORD HERE
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

# --- API Endpoints (已验证) ---
LOGIN_URL = "https://wjkc.lol/api/user/login"
CHECKIN_URL = "https://wjkc.lol/api/user/sign_use"

def run_local_checkin_test():
    """
    一个专为本地测试设计的函数，会详细打印每一步的执行过程和结果。
    """
    print("--- 本地签到测试开始 ---")
    print(f"账户: {USERNAME}")
    print("-" * 26)

    # session会话对象，用于在登录后保持状态
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    })

    try:
        # --- 第1步：登录 ---
        print(f"[1] 正在尝试登录...")
        print(f"   -> 地址: {LOGIN_URL}")
        
        login_payload = {'email': USERNAME, 'password': PASSWORD}
        login_response = session.post(LOGIN_URL, json=login_payload)
        login_response.raise_for_status()  # 如果服务器返回错误状态码 (如404, 500)，会在此抛出异常
        
        login_json = login_response.json()
        if login_json.get('data') is None and login_json.get('token') is None:
            raise ValueError(f"登录失败，服务器消息: {login_json.get('message', '未知错误')}")
        
        print("[1] ✅ 登录成功！服务器已授权访问。")
        print("-" * 26)

        # --- 第2步：执行签到 ---
        print(f"[2] 正在执行签到...")
        print(f"   -> 地址: {CHECKIN_URL}")

        # 发送签到请求，我们使用之前登录成功的同一个session对象
        checkin_payload = {"data": "e30="} # 这个是固定的请求体
        checkin_response = session.post(CHECKIN_URL, json=checkin_payload)
        checkin_response.raise_for_status()
        checkin_json = checkin_response.json()
        
        print("[2] ✅ 签到请求已成功发送并收到响应！")
        print("-" * 26)

        # --- 第3步：解码并分析结果 ---
        print("[3] 正在解码服务器返回的签到数据...")

        encoded_data = checkin_json.get('data')
        if not encoded_data:
            raise ValueError("签到响应中没有找到预期的'data'字段。")

        # Base64解码
        decoded_bytes = base64.b64decode(encoded_data)
        # 将解码后的JSON字符串转换为Python字典
        final_data = json.loads(decoded_bytes)
        
        print("[3] ✅ 解码成功！")
        print("-" * 26)

        # --- 最终结果展示 ---
        print("\n---  🎉 签到最终结果 🎉  ---")
        # 从解码后的数据中提取信息
        message = final_data.get('msg', '没有消息')
        reward_mb = final_data.get('data', {}).get('signUseRewardTraffic', 0)
        
        print(f"服务器消息: {message}")
        print(f"获得流量: {reward_mb} MB")
        print("----------------------------")


    except requests.exceptions.HTTPError as http_err:
        print(f"\n❌ 执行失败：服务器返回了错误状态码。")
        print(f"   错误详情: {http_err}")
        print(f"   请检查URL是否正确，或服务器是否正常运行。")
    except Exception as e:
        print(f"\n❌ 执行失败：脚本在运行时发生了一个意外错误。")
        print(f"   错误详情: {e}")


# --- 脚本主入口 ---
if __name__ == "__main__":
    if "your_email@example.com" in USERNAME or "your_password" in PASSWORD:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!  错误：请先在脚本中填写您的 USERNAME 和 PASSWORD  !!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    else:
        # 在运行前，请确保您已经安装了requests库
        # 打开终端/命令行，运行: pip install requests
        run_local_checkin_test()