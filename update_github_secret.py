import os
from github import Github
from nacl import encoding, public
import base64
import requests

def encrypt(public_key: str, secret_value: str) -> str:
    """Encrypt a Unicode string using the public key."""
    public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def update_github_repo_secret(repo_full_name, secret_name, secret_value, github_token):
    """
    更新 GitHub 仓库的指定机密。
    :param repo_full_name: 仓库的完整名称，例如 "owner/repo"
    :param secret_name: 要更新的机密名称
    :param secret_value: 机密的新值
    :param github_token: 具有 repo 权限的 GitHub Personal Access Token
    """
    try:
        g = Github(github_token)
        repo = g.get_repo(repo_full_name)

        # 获取仓库的公钥
        # PyGithub 似乎没有直接提供获取 Actions Secrets Public Key 的方法
        # 需要直接使用 requests 库调用 GitHub API
        # 或者使用 PyGithub 的 _requester 属性
        # 暂时使用 requests 库
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        public_key_url = f"https://api.github.com/repos/{repo_full_name}/actions/secrets/public-key"
        response = requests.get(public_key_url, headers=headers)
        response.raise_for_status()
        public_key_data = response.json()
        
        public_key = public_key_data['key']
        public_key_id = public_key_data['key_id']

        # 加密机密值
        encrypted_value = encrypt(public_key, secret_value)

        # 更新机密
        update_secret_url = f"https://api.github.com/repos/{repo_full_name}/actions/secrets/{secret_name}"
        payload = {
            "encrypted_value": encrypted_value,
            "key_id": public_key_id
        }
        response = requests.put(update_secret_url, headers=headers, json=payload)
        response.raise_for_status()

        print(f"成功更新 GitHub 仓库 '{repo_full_name}' 的机密 '{secret_name}'。")
        return True

    except Exception as e:
        print(f"更新 GitHub 机密 '{secret_name}' 过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    # 示例用法
    # 请勿将敏感信息直接硬编码在代码中
    # 这些值应该从环境变量或安全配置中获取
    test_repo_full_name = os.getenv('GITHUB_REPOSITORY') # 例如 "your_username/your_repo"
    test_secret_name = "WJKC_TOKENS"
    test_secret_value = "new_wjkc_token_value"
    test_github_token = os.getenv('GH_TOKEN') # 具有 repo 权限的 Personal Access Token

    if test_repo_full_name and test_github_token:
        success = update_github_repo_secret(
            test_repo_full_name,
            test_secret_name,
            test_secret_value,
            test_github_token
        )
        if success:
            print("机密更新测试成功。")
        else:
            print("机密更新测试失败。")
    else:
        print("请设置环境变量 GITHUB_REPOSITORY 和 GH_TOKEN 进行测试。")