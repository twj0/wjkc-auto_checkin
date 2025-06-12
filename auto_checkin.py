# auto_checkin.py (Final Version for GitHub Actions using Cookie)
import os
import requests
import json
import base64
from datetime import datetime, timedelta

# --- API Endpoints ---
CHECKIN_URL = "https://wjkc.lol/api/user/sign_use"
USER_INFO_URL = "https://wjkc.lol/api/user/userinfo"

# --- Telegram Bot (Optional) ---
def send_telegram_message(message, bot_token, chat_id):
    if not bot_token or not chat_id: return
    beijing_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"<b>wjkc.lol 自动签到通知</b>\n{'-'*20}\n{message}"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": formatted_message, "parse_mode": "HTML"}
    try: requests.post(url, data=payload)
    except Exception as e: print(f"[Telegram Error] {e}")

# --- 主函数 ---
def run_checkin_with_token(wjkc_token, bot_token, chat_id):
    session = requests.Session()
    # 直接使用我们从Secrets中获取的“万能钥匙”
    session.cookies.update({"token": wjkc_token})
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'})

    try:
        # --- 步骤1: 携带凭证，直接执行签到 ---
        checkin_response = session.post(CHECKIN_URL, json={"data": "e30="})
        checkin_response.raise_for_status()
        checkin_result_decoded = json.loads(base64.b64decode(checkin_response.json().get('data')))
        
        message = checkin_result_decoded.get('msg', 'N/A')
        if message == "SUCCESS":
            reward_mb = checkin_result_decoded.get('data', {}).get('addTraffic', 0) / (1024*1024) # 转换为MB
            status_text = f"签到成功！获得 {reward_mb:.2f}MB 流量。"
        else: # Handles CAN_NOT_SIGNUSE
            status_text = f"无需签到 (今天可能已签到过)。"
        
        print(f"✅ Check-in complete, Server message: {message}")
        
        # --- 步骤2: 查询账户信息以获取最新状态 ---
        userinfo_response = session.post(USER_INFO_URL, json={"data": "e30="})
        userinfo_decoded = json.loads(base64.b64decode(userinfo_response.json().get('data')))

        if userinfo_decoded.get('msg') != 'SUCCESS':
            raise ValueError("Token凭证可能已失效，无法查询用户信息。")
        
        email = userinfo_decoded.get('data', {}).get('email', '未知账户')
        traffic_left_gb = userinfo_decoded.get('data', {}).get('traffic', 0) / (1024*1024*1024)
        
        final_message = f"<b>账户:</b> {email}\n<b>状态:</b> {status_text}\n<b>剩余总流量:</b> {traffic_left_gb:.2f}GB"

    except Exception as e:
        final_message = f"<b>状态:</b> 任务失败\n<b>错误:</b> {e}"
        print(f"❌ An error occurred: {e}")
    
    send_telegram_message(final_message, bot_token, chat_id)

if __name__ == "__main__":
    wjkc_token = os.getenv('WJKC_TOKEN')
    bot_token = os.getenv('BOT_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    
    if not wjkc_token:
        print("❌ [错误] 未在GitHub Secrets中找到名为 WJKC_TOKEN 的密钥。")
    else:
        print("✅ Found WJKC_TOKEN. Starting the check-in process...")
        run_checkin_with_token(wjkc_token, bot_token, chat_id)
        print("Job completed.")