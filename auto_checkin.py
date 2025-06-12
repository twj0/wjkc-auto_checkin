# auto_checkin.py (Final and Correct Multi-Account Version using Cookies)
import os
import requests
import json
import base64
from datetime import datetime, timedelta

# --- API Endpoints ---
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

# --- 主函数 (处理单个Token) ---
def run_checkin_for_token(token_name, wjkc_token):
    print(f"--- 正在处理账户: {token_name} ---")
    session = requests.Session()
    session.cookies.update({"token": wjkc_token.strip()}) # 使用 .strip() 清除可能存在的空格
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'})
    
    try:
        # Step 1: Check-in
        checkin_response = session.post(CHECKIN_URL, json={"data": "e30="})
        checkin_response.raise_for_status()
        checkin_result = json.loads(base64.b64decode(checkin_response.json().get('data')))
        
        message = checkin_result.get('msg', 'N/A')
        if message == "SUCCESS":
            reward_mb = checkin_result.get('data', {}).get('addTraffic', 0) / (1024*1024)
            status_text = f"✅ 签到成功！获得 {reward_mb:.2f}MB"
        else:
            status_text = f"🟡 无需签到 (已签到)"
        print(f"  > 签到状态: {status_text}")
        
        # Step 2: Get User Info
        userinfo_response = session.post(USER_INFO_URL, json={"data": "e30="})
        userinfo_result = json.loads(base64.b64decode(userinfo_response.json().get('data')))
        if userinfo_result.get('msg') != 'SUCCESS': raise ValueError("Token无效或已过期，无法查询信息。")
        
        email = userinfo_result.get('data', {}).get('email', token_name)
        traffic_gb = userinfo_result.get('data', {}).get('traffic', 0) / (1024*1024*1024)
        
        return f"<b>账户:</b> {email}\n<b>状态:</b> {status_text}\n<b>剩余流量:</b> {traffic_gb:.2f}GB\n{'-'*20}"

    except Exception as e:
        error_message = f"<b>令牌:</b> {token_name}\n<b>状态:</b> ❌ 任务失败\n<b>错误:</b> {e}\n{'-'*20}"
        print(f"  > 发生错误: {e}")
        return error_message

# --- 脚本入口 ---
def load_tokens_from_env():
    tokens_str = os.getenv('WJKC_TOKENS')
    if tokens_str:
        # 过滤掉因为额外逗号等产生的空字符串
        return {f"Token_{i+1}": token.strip() for i, token in enumerate(tokens_str.split(',')) if token.strip()}
    return {}

if __name__ == "__main__":
    all_tokens = load_tokens_from_env()
    if not all_tokens:
        print("❌ [错误] 未在GitHub Secrets中找到名为 WJKC_TOKENS 的密钥。")
    else:
        print(f"✅ 找到 {len(all_tokens)} 个账户Token。开始执行签到任务...")
        results_for_telegram = []
        for name, value in all_tokens.items():
            result = run_checkin_for_token(name, value)
            results_for_telegram.append(result)
            print("-" * 40)
        
        bot_token = os.getenv('BOT_TOKEN')
        chat_id = os.getenv('CHAT_ID')
        send_telegram_message(results_for_telegram, bot_token, chat_id)

    print("所有任务已完成。")