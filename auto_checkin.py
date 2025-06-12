# auto_checkin.py (Final Multi-Account Version for GitHub Actions)
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
    # 为多账户优化的消息头部
    header = "<b>wjkc.lol 多账户签到通知</b>"
    formatted_message = f"{header}\n{'-'*20}\n{message}"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": formatted_message, "parse_mode": "HTML"}
    try: requests.post(url, data=payload)
    except Exception as e: print(f"[Telegram Error] {e}")

# --- 主函数 (现在处理单个Token) ---
def run_checkin_for_token(token_name, wjkc_token, bot_token, chat_id):
    print(f"--- Processing Token: {token_name} ---")
    session = requests.Session()
    session.cookies.update({"token": wjkc_token})
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'})
    
    final_message = "" # 用于拼接单个账户的推送消息

    try:
        # Step 1: Check-in
        checkin_response = session.post(CHECKIN_URL, json={"data": "e30="})
        checkin_response.raise_for_status()
        checkin_result_decoded = json.loads(base64.b64decode(checkin_response.json().get('data')))
        
        message = checkin_result_decoded.get('msg', 'N/A')
        if message == "SUCCESS":
            reward_mb = checkin_result_decoded.get('data', {}).get('addTraffic', 0) / (1024*1024)
            status_text = f"✅ 签到成功！获得 {reward_mb:.2f}MB"
        else:
            status_text = f"🟡 无需签到 (已签到)"
        
        print(f"  > Check-in status: {status_text}")
        
        # Step 2: Get User Info
        userinfo_response = session.post(USER_INFO_URL, json={"data": "e30="})
        userinfo_decoded = json.loads(base64.b64decode(userinfo_response.json().get('data')))
        
        if userinfo_decoded.get('msg') != 'SUCCESS':
            raise ValueError("Token凭证可能已失效，无法查询用户信息。")
        
        email = userinfo_decoded.get('data', {}).get('email', '未知账户')
        traffic_left_gb = userinfo_decoded.get('data', {}).get('traffic', 0) / (1024*1024*1024)
        
        final_message = f"<b>账户:</b> {email}\n<b>状态:</b> {status_text}\n<b>剩余流量:</b> {traffic_left_gb:.2f}GB"

    except Exception as e:
        final_message = f"<b>令牌:</b> {token_name}\n<b>状态:</b> ❌ 任务失败\n<b>错误:</b> {e}"
        print(f"  > An error occurred: {e}")
    
    # 每个账户执行完毕后，都发送一次消息
    send_telegram_message(final_message, bot_token, chat_id)


# --- 脚本入口 (现在可以加载多个Token) ---
def load_tokens_from_env():
    """从GitHub环境变量加载所有 WJKC_TOKEN """
    tokens = {}
    i = 1
    while True:
        token_name = f'WJKC_TOKEN{i}'
        token_value = os.getenv(token_name)
        if token_value:
            tokens[token_name] = token_value
            i += 1
        else:
            # 如果 WJKC_TOKEN1 都不存在，尝试寻找旧的 WJKC_TOKEN
            if i == 1 and os.getenv('WJKC_TOKEN'):
                tokens['WJKC_TOKEN'] = os.getenv('WJKC_TOKEN')
            break
    return tokens

if __name__ == "__main__":
    bot_token = os.getenv('BOT_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    all_tokens = load_tokens_from_env()
    
    if not all_tokens:
        print("❌ [错误] 未在GitHub Secrets中找到任何 WJKC_TOKEN。")
    else:
        print(f"✅ Found {len(all_tokens)} account token(s). Starting automation...")
        for name, value in all_tokens.items():
            run_checkin_for_token(name, value, bot_token, chat_id)
            print("-" * 40)
    print("All jobs completed.")