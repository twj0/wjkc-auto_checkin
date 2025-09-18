# wjkc.lol 自动签到脚本

这是一个基于 GitHub Actions 的自动化脚本，旨在每日自动为您的 `wjkc.lol` 账户执行签到任务，以保持连续签到记录并获取每日奖励。

## ✨ 主要特性

- **多账户支持**: 可通过 GitHub Secrets 配置多个账户，脚本会自动为每个账户执行签到。
- **自动 Token 更新**: 脚本现在支持通过登录凭据自动获取并更新 `token`，无需手动复制粘贴。
- **完全自动化**: 基于 GitHub Actions，每日定时自动运行，无需任何手动干预。
- **实时通知**: 支持通过 Telegram Bot 推送每次签到的结果，让您对账户状态了如指掌。


## ⚙️ 核心原理

本脚本的核心原理是**通过模拟浏览器登录获取最新的会话凭证（`token` Cookie），并使用此 `token` 来执行签到操作。** 脚本会自动管理 `token` 的更新，确保其长期有效性。

## 🚀 部署指南

请严格按照以下步骤进行配置，以确保自动化流程能够成功运行。

### 第1步：Fork 本仓库

点击本页面右上角的 **`Fork`** 按钮，将此仓库复制到您自己的 GitHub 账户下。接下来的所有操作都在您自己的仓库中进行。

### 第2步：设置 GitHub Secrets

进入您Fork后的仓库，点击 `Settings` -> `Secrets and variables` -> `Actions`。然后点击 `New repository secret`，添加以下机密信息：

-   **`WJKC_CREDENTIALS`**:
    -   **Name**: `WJKC_CREDENTIALS`
    -   **Value**: 您的 `wjkc.lol` 账户凭据，**JSON 格式的字符串**。
        *   **示例**:
            ```json
            [{"name": "MyAccount1", "username": "your_username1", "password": "your_password1"}, 
            {"name": "MyAccount2", "username": "your_username2", "password": "your_password2"}]
            ```
           `name` 字段是可选的，用于在日志中标识账户。
           请确保 `username` 和 `password` 字段正确。

-   **`GH_TOKEN`**:
    -   **Name**: `GH_TOKEN`
    -   **Value**: 一个具有 `repo` 权限的 GitHub Personal Access Token (PAT)。此 Token 用于脚本自动更新仓库中的 `WJKC_TOKENS` 机密。
        *   **如何获取**: 前往 GitHub `Settings` -> `Developer settings` -> `Personal access tokens` -> `Tokens (classic)` -> `Generate new token`。确保勾选 `repo` 权限。

-   **`WJKC_TOKENS`** (可选):
    -   **Name**: `WJKC_TOKENS` (请注意是复数`S`)
    -   **Value**: 您现有的 `wjkc.lol` token，以逗号(`,`)分隔。
        *   **用途**: 如果通过登录获取新 token 失败，脚本将回退到使用此处的 token 进行签到。
        *   **格式示例**: `cookie_value_of_account_1,cookie_value_of_account_2`

-   **`BOT_TOKEN`** (可选):
    -   **Name**: `BOT_TOKEN`
    -   **Value**: 您的Telegram机器人的Token，用于发送通知。

-   **`CHAT_ID`** (可选):
    -   **Name**: `CHAT_ID`
    -   **Value**: 您的Telegram用户ID或频道的ID，用于接收通知。

### 第3步：启动自动化

设置完Secrets后，您的自动化方案已经配置完毕。您可以等待第二天的定时任务自动运行，或者：

1.  进入仓库的 **`Actions`** 标签页。
2.  在左侧选择 **`WJKC Auto Checkin and Token Update`**。
3.  点击 **`Run workflow`** 按钮来手动触发一次，以立即验证您的配置是否成功。

## 📝 文件结构

-   **`.github/workflows/auto_checkin.yml`**: GitHub Actions的工作流配置文件，负责定时启动任务、安装依赖并运行脚本。
-   **`auto_checkin.py`**: 核心的Python脚本，负责协调 `token` 获取、更新和签到任务。
-   **`get_token.py`**: 负责使用 Selenium 模拟浏览器登录 `wjkc.lol` 并获取 `token`。
-   **`update_github_secret.py`**: 负责使用 GitHub API 更新仓库机密。

## ⚠️ 重要说明

-   脚本现在会自动尝试获取和更新 `token`，大大减少了手动维护的频率。
-   如果 `WJKC_CREDENTIALS` 配置不正确或登录失败，脚本将尝试使用 `WJKC_TOKENS` 中已有的 token 进行签到。
-   本项目仅用于学习和技术交流，请勿用于非法用途。

---

## 结果示例
我已经成功签到了五天了
如图，tg bot自动推送[image.png](/屏幕截图%202025-06-17%20145816.png)
