[中文](README_zh.md) | English

# HF Bucket Sync

A web-based tool for synchronizing local files with HuggingFace Bucket storage.

## Features

- 📁 Local file browser
- ☁️ HF Bucket management
- 🔄 Bidirectional sync (upload/download)
- 🔍 File filtering (by extension, path)
- ⏰ Scheduled tasks (Cron expressions)
- 📜 Sync history
- 🔔 Notifications (Telegram, ServerChan)
- 🎨 Theme (Light/Dark/System)

## Quick Start

### 1. Configure Environment

```bash
export HF_TOKEN=your_hf_token_here
export AUTH_TOKEN_SECRET=your_32+_char_secret_here
```

`AUTH_TOKEN_SECRET` notes:
- Required, minimum 32 characters.
- In `.env` for Docker Compose, avoid `$` (or escape it as `$$`) to prevent variable interpolation.

### 2. Start Services

```bash
docker-compose up -d
```

### 3. Access

- **Web UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- On first startup, the container logs print an auto-generated 14-character login password once.
- If the password is lost, reset it with:
  `docker compose run --rm app python -m backend.tools.reset_password`
- Run the reset command from the project root (where `docker-compose.yml` is located), or use:
  `docker compose -f <path-to-docker-compose.yml> run --rm app python -m backend.tools.reset_password`

## Project Structure

```
hf-bucket-sync/
├── backend/                    # FastAPI backend
│   ├── main.py                # Application entry
│   ├── api/routes/            # API routes
│   ├── services/              # Business logic
│   ├── models/                # Data models
│   └── scheduler/             # Scheduled tasks
├── web/                       # Vue 3 frontend
│   ├── src/
│   │   ├── views/            # Page components
│   │   ├── api/              # API calls
│   │   └── assets/           # Styles
│   └── package.json
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Configuration

| Env Variable | Description |
|-------------|-------------|
| HF_TOKEN | HuggingFace Access Token (required) |
| AUTH_TOKEN_SECRET | Token signing secret (required, at least 32 chars) |
| VITE_AUTH_TIMEOUT_MINUTES | Login session timeout in minutes (optional, default: 60) |
| VITE_SITE_TITLE | Website title shown in browser tab/login page (optional, default: HF Bucket Sync) |
| LOCAL_PATH | Local path for file browsing (optional) |
| VITE_CDN_BASE_URL | CDN base URL used by file links |
| VITE_LOGIN_BG_PC | Login background image URL for desktop (optional) |
| VITE_LOGIN_BG_MOBILE | Login background image URL for mobile (optional) |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/files/list | GET | Browse local directory |
| /api/buckets | GET | List HF Buckets |
| /api/buckets/{id}/tree | GET | List Bucket contents |
| /api/sync/dry-run | POST | Preview sync plan |
| /api/sync/execute | POST | Execute sync |
| /api/sync/history | GET | Sync history |
| /api/schedules | GET/POST | Schedule management |
| /api/schedules/{id} | PUT/DELETE | Update/delete schedule |
| /api/notifications/settings | GET/POST | Notification settings |
| /api/notifications/test | POST | Test notification |

## Filter Rules Example

```json
{
  "include_patterns": ["*.safetensors", "*.bin", "*.json"],
  "exclude_patterns": ["*.tmp", ".git/*", "logs/*"]
}
```

## Cron Expression Examples

| Expression | Description |
|-----------|-------------|
| `0 2 * * *` | Daily at 2:00 AM |
| `0 */4 * * *` | Every 4 hours |
| `0 0 * * 0` | Sunday midnight |
| `*/30 * * * *` | Every 30 minutes |

## License

MIT License
