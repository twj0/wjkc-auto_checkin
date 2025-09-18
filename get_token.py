import os
import requests
import json
import base64
import hashlib

def get_wjkc_token(account_name, username, password):
    print(f"--- 正在尝试登录账户: {account_name} ---")
    
    LOGIN_URL = "https://wjkc.lol/api/user/login"
    
    # 对密码进行 MD5 哈希
    md5_password = hashlib.md5(password.encode('utf-8')).hexdigest()
    
    # 构建请求数据
    payload_data = {
        "email": username,
        "password": md5_password
    }
    
    # 对 payload_data 进行 base64 编码
    encoded_data = base64.b64encode(json.dumps(payload_data).encode('utf-8')).decode('utf-8')
    
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Origin": "https://wjkc.lol",
        "Referer": "https://wjkc.lol/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"'
    }
    
    try:
        response = requests.post(LOGIN_URL, headers=headers, json={"data": encoded_data})
        response.raise_for_status() # 检查 HTTP 错误
        
        response_json = response.json()
        
        # 检查响应中的 'data' 字段
        if 'data' in response_json:
            decoded_response_data = json.loads(base64.b64decode(response_json['data']).decode('utf-8'))
            
            if decoded_response_data.get('msg') == 'SUCCESS':
                # 登录成功，从 cookies 中获取 token
                wjkc_token = response.cookies.get('token')
                if wjkc_token:
                    print(f"成功获取到 token: {wjkc_token}")
                    return wjkc_token
                else:
                    print("登录成功但未找到 token cookie。")
                    return None
            else:
                error_msg = decoded_response_data.get('msg', '未知错误')
                print(f"登录失败: {error_msg}")
                return None
        else:
            print(f"登录响应中未找到 'data' 字段: {response_json}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"获取 token 过程中发生网络或HTTP错误: {e}")
        return None
    except json.JSONDecodeError:
        print(f"获取 token 过程中发生 JSON 解析错误: {response.text}")
        return None
    except Exception as e:
        print(f"获取 token 过程中发生未知错误: {e}")
        return None

if __name__ == "__main__":
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