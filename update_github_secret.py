import os
import base64
import requests

def encrypt(public_key: str, secret_value: str) -> str | None:
    """Encrypt a Unicode string using the public key.

    Returns base64 ciphertext on success, or None if PyNaCl is missing.
    """
    try:
        from nacl import encoding as nacl_encoding, public as nacl_public
    except Exception:
        print("缺少依赖 PyNaCl，无法加密并更新 GitHub Secrets。请在运行环境安装 PyNaCl。")
        return None

    pk = nacl_public.PublicKey(public_key.encode("utf-8"), nacl_encoding.Base64Encoder())
    sealed_box = nacl_public.SealedBox(pk)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def _hint_from_http_error(resp: requests.Response) -> str:
    try:
        data = resp.json()
        message = str(data.get("message", ""))
    except Exception:
        message = resp.text or ""

    hints = []

    if resp.status_code == 401:
        hints.append("令牌无效或已过期（401）。请重新生成 PAT 并更新 GH_TOKEN。")

    if resp.status_code == 403:
        if "Resource protected by organization SSO" in message:
            hints.append("组织启用了 SSO。请在 GitHub 的 Authorized OAuth Apps 中为该 PAT 开启 SSO 权限。")
        if "Resource not accessible by integration" in message:
            hints.append("GITHUB_TOKEN 无法管理仓库 Secrets。请使用具备权限的个人访问令牌 (PAT) 通过 GH_TOKEN 传入。")
        if "Must have admin rights to Repository" in message or "must be an admin" in message.lower():
            hints.append("当前令牌对应账户对仓库无管理员权限。请将该账户加入仓库并授予 Admin/维护者权限，或改用拥有权限的 PAT。")
        # Fine-grained PAT 常见问题：未勾选必要权限
        if "fine-grained" in message.lower() or "permissions" in message.lower():
            hints.append("若使用细粒度 PAT，请为目标仓库授予：Actions (Read and write) 与 Repository secrets/variables (Read and write)。")

    if resp.status_code == 404:
        hints.append("找不到资源（404）。请检查 repo 全名是否正确，或 PAT 是否被授予对该仓库的访问权限。")

    # 附上服务端返回信息，便于排查
    base_info = f"HTTP {resp.status_code}: {message.strip()}"
    hints.insert(0, base_info)
    return " \n- ".join(hints)


def update_github_repo_secret(repo_full_name, secret_name, secret_value, github_token):
    """
    更新 GitHub 仓库的指定机密。
    :param repo_full_name: 仓库的完整名称，例如 "owner/repo"
    :param secret_name: 要更新的机密名称
    :param secret_value: 机密的新值
    :param github_token: 具有 repo 权限的 GitHub Personal Access Token
    """
    try:
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
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            print("获取仓库 Actions 公钥失败。")
            print(_hint_from_http_error(response))
            return False
        public_key_data = response.json()
        
        public_key = public_key_data['key']
        public_key_id = public_key_data['key_id']

        # 加密机密值
        encrypted_value = encrypt(public_key, secret_value)
        if not encrypted_value:
            return False

        # 更新机密
        update_secret_url = f"https://api.github.com/repos/{repo_full_name}/actions/secrets/{secret_name}"
        payload = {
            "encrypted_value": encrypted_value,
            "key_id": public_key_id
        }
        response = requests.put(update_secret_url, headers=headers, json=payload)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            print("更新仓库机密失败。")
            print(_hint_from_http_error(response))
            return False

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
