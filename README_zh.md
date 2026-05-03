[English](README.md) | 中文

# HF Bucket Sync

HuggingFace Bucket 同步工具 - 将本地文件同步到 HF Bucket 存储。

## 功能特性

- 📁 本地文件浏览
- ☁️ HF Bucket 管理
- 🔄 双向同步（上传/下载）
- 🔍 文件过滤（按扩展名、路径）
- ⏰ 定时任务（Cron 表达式）
- 📜 同步历史记录
- 🔔 通知（飞书、Telegram）
- 🎨 主题（亮色/暗色/跟随系统）

## 快速开始

### 1. 配置环境变量

```bash
export HF_TOKEN=your_hf_token_here
export AUTH_TOKEN_SECRET=your_32+_char_secret_here
```

`AUTH_TOKEN_SECRET` 说明：
- 必填，长度至少 32 位。
- 在 Docker Compose 的 `.env` 中，建议不要使用 `$`（或写成 `$$` 转义），避免被变量展开。

### 2. 启动服务

```bash
docker-compose up -d
```

### 3. 访问

- **Web UI**: http://localhost:8000
- **API 文档**: http://localhost:8000/api/docs
- 首次启动时，容器日志会打印一次自动生成的 14 位登录密码。
- 如果忘记密码，可执行重置命令：
  `docker compose run --rm app python -m backend.tools.reset_password`
- 重置命令需要在项目根目录（存在 `docker-compose.yml`）执行；或使用：
  `docker compose -f <path-to-docker-compose.yml> run --rm app python -m backend.tools.reset_password`

## 项目结构

```
hf-bucket-sync/
├── backend/                    # FastAPI 后端
│   ├── main.py                # 应用入口
│   ├── api/routes/            # API 路由
│   ├── services/              # 业务逻辑
│   ├── models/                # 数据模型
│   └── scheduler/             # 定时任务
├── web/                       # Vue 3 前端
│   ├── src/
│   │   ├── views/            # 页面组件
│   │   ├── api/              # API 调用
│   │   └── assets/           # 样式
│   └── package.json
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 配置

| 环境变量 | 说明 |
|---------|------|
| HF_TOKEN | HuggingFace Access Token（必需） |
| AUTH_TOKEN_SECRET | Token 签名密钥（必需，至少 32 位） |
| VITE_AUTH_TIMEOUT_MINUTES | 登录会话超时时间（分钟，可选，默认: 60） |
| VITE_SITE_TITLE | 网站标题（浏览器标签页/登录页，默认: HF Bucket Sync） |
| LOCAL_PATH | 本地文件浏览路径（可选） |
| VITE_CDN_BASE_URL | 文件链接使用的 CDN 基础地址 |
| VITE_LOGIN_BG_PC | 登录页桌面端背景图 URL（可选） |
| VITE_LOGIN_BG_MOBILE | 登录页移动端背景图 URL（可选） |

## API 端点

| 端点 | 方法 | 功能 |
|------|------|------|
| /api/files/list | GET | 浏览本地目录 |
| /api/buckets | GET | 列出 HF Bucket |
| /api/buckets/{id}/tree | GET | 列出 Bucket 内容 |
| /api/sync/dry-run | POST | 预览同步计划 |
| /api/sync/execute | POST | 执行同步 |
| /api/sync/history | GET | 同步历史 |
| /api/schedules | GET/POST | 定时任务管理 |
| /api/schedules/{id} | PUT/DELETE | 更新/删除定时任务 |
| /api/notifications/settings | GET/POST | 通知设置 |
| /api/notifications/test | POST | 测试通知 |

## 过滤规则示例

```json
{
  "include_patterns": ["*.safetensors", "*.bin", "*.json"],
  "exclude_patterns": ["*.tmp", ".git/*", "logs/*"]
}
```

## Cron 表达式示例

| 表达式 | 说明 |
|--------|------|
| `0 2 * * *` | 每天凌晨 2 点 |
| `0 */4 * * *` | 每 4 小时 |
| `0 0 * * 0` | 每周日凌晨 |
| `*/30 * * * *` | 每 30 分钟 |

## 许可证

MIT License
