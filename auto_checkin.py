import os
import requests
import json
import base64
import hashlib  # <--- 导入Python标准的哈希加密库
from datetime import datetime, timedelta

# --- API Endpoints ---
LOGIN_URL = "https://wjkc.lol/api/user/login"
CHECKIN_URL = "https://wjkc.lol/api/user/sign_use"
USER_INFO_URL = "https://wjkc.lol/api/user/userinfo"

# --- Telegram Bot (Optional) ---
def send_telegram_message(messages, bot_token, chat_id):
    if not bot_token or not chat_id or not messages: return
    header = f"<b>wjkc.lol 签到通知</b> ({len(messages)}个账户)"
    full_message = header + "\n" + "\n".join(messages)
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": full_message, "parse_mode": "HTML"}
    try: requests.post(url, data=payload)
    except Exception as e: print(f"[Telegram Error] {e}")

# --- 主函数 ---
def run_checkin_flow(username, password, bot_token, chat_id):
    account_details = f"<b>账户:</b> {username}"
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'})

    try:
        # --- 步骤1:【最终的登录逻辑】对密码进行MD5加密 ---
        # 这就是我们苦苦寻找的 hl() 函数的Python实现！
        m = hashlib.md5()
        m.update(password.encode('utf-8'))
        encrypted_password = m.hexdigest()
        
        # 然后，再执行我们之前破解的“双重包装”
        inner_payload_str = json.dumps({"email": username, "password": encrypted_password})
        encoded_payload = base64.b64encode(inner_payload_str.encode('utf-8')).decode('utf-8')
        final_payload = {"data": encoded_payload}
        
        login_response = session.post(LOGIN_URL, json=final_payload)
        login_response.raise_for_status()
        
        # --- 步骤2: 从响应中解码并提取Token ---
        login_result_encoded = login_response.json().get('data')
        login_result_decoded = json.loads(base64.b64decode(login_result_encoded))
        
        if login_result_decoded.get('msg') != 'SUCCESS':
            raise ValueError(f"登录失败: {login_result_decoded.get('msg')}")
            
        token = login_result_decoded.get('data', {}).get('token')
        if not token: raise ValueError("登录成功，但未能获取到Token！")
        
        print(f"[{username}] ✅ 登录成功，并成功获取Token！")
        
        # --- 步骤3: 佩戴Token，执行签到 ---
        session.headers.update({'Authorization': token})
        checkin_response = session.post(CHECKIN_URL, json={"data": "e30="})
        checkin_response.raise_for_status()
        checkin_result_decoded = json.loads(base64.b64decode(checkin_response.json().get('data')))
        
        message = checkin_result_decoded.get('msg', 'N/A')
        status_text = ""
        if message == "SUCCESS":
            reward_mb = checkin_result_decoded.get('data', {}).get('addTraffic', 0) / (1024*1024)
            status_text = f"✅ 签到成功！获得 {reward_mb:.2f}MB"
        else:
            status_text = f"🟡 无需签到 (已签到)"
        
        print(f"[{username}] > 签到状态: {status_text}")
        
        # --- 步骤4 (可选): 获取真实的签到天数 ---
        userinfo_response = session.post(USER_INFO_URL, json={"data": "e30="})
        userinfo_decoded = json.loads(base64.b64decode(userinfo_response.json().get('data')))
        real_days = userinfo_decoded.get('data', {}).get('continueSignUseDay', '未知')
        
        return f"{account_details}\n<b>状态:</b> {status_text}\n<b>连续签到:</b> {real_days} 天\n{'-'*20}"

    except Exception as e:
        error_message = f"{account_details}\n<b>状态:</b> ❌ 任务失败\n<b>错误:</b> {e}\n{'-'*20}"
        print(f"[{username}] ❌ 任务失败: {e}")
        return error_message


# --- 脚本入口 ---
def load_accounts_from_env():
    accounts, i = [], 1
    while True:
        user, password = os.getenv(f'USER{i}'), os.getenv(f'PASS{i}')
        if user and password: accounts.append({'user': user, 'pass': password}); i += 1
        else: break
    return accounts

if __name__ == "__main__":
    all_accounts = load_accounts_from_env()
    if not all_accounts:
        print("❌ 未在环境变量中找到任何账户 (e.g., USER1, PASS1).")
    else:
        print(f"✅ 找到 {len(all_accounts)} 个账户。开始执行签到任务...")
        results_for_telegram = []
        for acc in all_accounts:
            result = run_checkin_flow(acc['user'], acc['pass'], os.getenv('BOT_TOKEN'), os.getenv('CHAT_ID'))
            results_for_telegram.append(result)
        
        send_telegram_message(results_for_telegram, os.getenv('BOT_TOKEN'), os.getenv('CHAT_ID'))

    print("所有任务已完成。")