import os
import requests
import json
import base64
import hashlib
from datetime import datetime, timedelta

# --- API Endpoints ---
BASE_URL = "https://wjkc.lol/"
LOGIN_URL = "https://wjkc.lol/api/user/login"
CHECKIN_URL = "https://wjkc.lol/api/user/sign_use"
USER_INFO_URL = "https://wjkc.lol/api/user/userinfo"

# --- Telegram Bot ---
def send_telegram_message(messages, bot_token, chat_id):
    if not bot_token or not chat_id or not messages: return
    header = f"<b>wjkc.lol 签到通知</b> ({len(messages)}个账户)"
    full_message = header + "\n" + "\n".join(messages)
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": full_message, "parse_mode": "HTML"}
    try: requests.post(url, data=payload)
    except Exception as e: print(f"[Telegram Error] {e}")

# --- 主函数 ---
def run_final_checkin_flow(username, password):
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'})

    try:
        # --- 步骤1: 访问主页，获取初始会话Cookie ---
        print(f"[{username}] > 步骤1: 正在访问主页获取会话Cookie...")
        session.get(BASE_URL, timeout=15).raise_for_status()
        if not session.cookies.get_dict(): raise ValueError("未能获取到初始会话Cookie！")
        print(f"[{username}] > 步骤1: ✅ 成功获取会话Cookie！")

        # --- 步骤2: 准备登录请求体 (MD5加密 + 双重包装) ---
        print(f"[{username}] > 步骤2: 正在准备加密登录请求...")
        m = hashlib.md5()
        m.update(password.encode('utf-8'))
        encrypted_password = m.hexdigest()
        
        inner_payload_str = json.dumps({"email": username, "password": encrypted_password})
        encoded_payload = base64.b64encode(inner_payload_str.encode('utf-8')).decode('utf-8')
        final_payload = {"data": encoded_payload}
        
        # --- 步骤3: 携带Cookie，发送加密的登录请求 ---
        login_response = session.post(LOGIN_URL, json=final_payload)
        login_response.raise_for_status()
        
        # --- 步骤4: 从响应中解码并提取Token ---
        login_result_encoded = login_response.json().get('data')
        login_result_decoded = json.loads(base64.b64decode(login_result_encoded))
        
        if login_result_decoded.get('msg') != 'SUCCESS':
            raise ValueError(f"登录失败: {login_result_decoded.get('msg')}")
            
        token = login_result_decoded.get('data', {}).get('token')
        if not token: raise ValueError("登录成功，但未能获取到Token！")
        
        print(f"[{username}] > 步骤2-4: ✅ 登录成功，并成功获取Token！")
        
        # --- 步骤5: 佩戴Token，执行签到 ---
        print(f"[{username}] > 步骤5: 正在执行签到...")
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
        
        # --- 步骤6: 查询最终状态 ---
        userinfo_response = session.post(USER_INFO_URL, json={"data": "e30="})
        userinfo_decoded = json.loads(base64.b64decode(userinfo_response.json().get('data')))
        real_days = userinfo_decoded.get('data', {}).get('continueSignUseDay', '未知')
        traffic_gb = userinfo_decoded.get('data', {}).get('traffic', 0) / (1024*1024*1024)
        
        return f"<b>账户:</b> {username}\n<b>状态:</b> {status_text}\n<b>连续签到:</b> {real_days} 天\n<b>剩余流量:</b> {traffic_gb:.2f}GB\n{'-'*20}"

    except Exception as e:
        error_message = f"<b>账户:</b> {username}\n<b>状态:</b> ❌ 任务失败\n<b>错误:</b> {e}\n{'-'*20}"
        print(f"[{username}] ❌ 任务失败: {e}")
        return error_message


# --- 脚本入口 ---
def load_accounts_from_env():
    accounts, i = [], 1
    while True:
        user, password = os.getenv(f'USER{i}'), os.getenv(f'PASS{i}')
        if user and password: accounts.append({'user': user, 'pass': password}); i += 1
        else:
            if i > 20: break # 防止无限循环
            i += 1
            continue
    return accounts

if __name__ == "__main__":
    all_accounts = load_accounts_from_env()
    if not all_accounts:
        print("❌ 未在环境变量中找到任何账户 (e.g., USER1, PASS1).")
    else:
        print(f"✅ 找到 {len(all_accounts)} 个账户。开始执行签到任务...")
        results_for_telegram = []
        for acc in all_accounts:
            result = run_final_checkin_flow(acc['user'], acc['pass'])
            results_for_telegram.append(result)
        
        send_telegram_message(results_for_telegram, os.getenv('BOT_TOKEN'), os.getenv('CHAT_ID'))

    print("所有任务已完成。")