# auto_checkin.py
import os
import requests
import json
import base64
from datetime import datetime, timedelta

# --- API Endpoints for wjkc.lol (Verified) ---
LOGIN_URL = "https://wjkc.lol/api/user/login"
CHECKIN_URL = "https://wjkc.lol/api/user/sign_use" # <-- The REAL check-in URL you discovered!

def send_telegram_message(message, bot_token, chat_id):
    """Sends a formatted message to a Telegram chat."""
    if not bot_token or not chat_id:
        return

    beijing_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"<b>wjkc.lol 自动签到通知</b>\n{'-'*20}\n{message}\n\n执行时间: {beijing_time}"

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": formatted_message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def run_checkin_for_account(account, bot_token, chat_id):
    """Logs in and performs the daily check-in for a single account."""
    username = account['user']
    password = account['pass']
    
    account_details = f"<b>账户:</b> {username}\n<b>密码:</b> <tg-spoiler>{password}</tg-spoiler>"
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    })

    try:
        # --- 1. Login ---
        print(f"Attempting to log in as {username}...")
        login_response = session.post(LOGIN_URL, json={'email': username, 'password': password})
        login_response.raise_for_status()
        login_json = login_response.json()

        if login_json.get('data') is None and login_json.get('token') is None:
            raise ValueError(f"Login Failed: {login_json.get('message', 'Unknown error')}")
        
        print(f"Login successful for {username}.")

        # --- 2. Check-in ---
        print(f"Performing check-in at the correct URL: {CHECKIN_URL}")
        # The body {"data":"e30="} is Base64 for an empty JSON object {}
        checkin_response = session.post(CHECKIN_URL, json={"data": "e30="})
        checkin_response.raise_for_status()
        checkin_json = checkin_response.json()

        # --- 3. Decode the Response ---
        encoded_data = checkin_json.get('data')
        if not encoded_data:
            raise ValueError("Check-in response did not contain the expected 'data' field.")
            
        decoded_json = json.loads(base64.b64decode(encoded_data))
        message = decoded_json.get('msg', 'Could not find message.')
        reward_mb = decoded_json.get('data', {}).get('signUseRewardTraffic', 0)
        
        final_message = f"{account_details}\n<b>状态:</b> 签到成功！\n<b>信息:</b> {message}\n<b>获得流量:</b> {reward_mb}MB"
        print("Check-in successful!")

    except Exception as e:
        final_message = f"{account_details}\n<b>状态:</b> 签到失败\n<b>错误:</b> {e}"
        print(f"An error occurred for {username}: {e}")
    
    # --- 4. Send Notification ---
    send_telegram_message(final_message, bot_token, chat_id)


def load_accounts_from_env():
    """Loads accounts from environment variables."""
    accounts = []
    i = 1
    while True:
        user, password = os.getenv(f'USER{i}'), os.getenv(f'PASS{i}')
        if user and password:
            accounts.append({'user': user, 'pass': password})
            i += 1
        else:
            break
    return accounts

if __name__ == "__main__":
    bot_token = os.getenv('BOT_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    accounts = load_accounts_from_env()

    if not accounts:
        print("No accounts found. For local testing, set environment variables.")
    else:
        print(f"Found {len(accounts)} account(s). Starting...")
        for acc in accounts:
            run_checkin_for_account(acc, bot_token, chat_id)
            print("-" * 25)