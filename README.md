# CWA Ingest Bot

A Telegram bot that receives EPUB files and drops them into a [Calibre-Web Automated (CWA)](https://github.com/cronitorio/calibre-web-automated) ingest directory, triggering automatic library import.

## How it works

1. You send an EPUB file to the bot on Telegram.
2. The bot validates the file (must be `.epub`, under 20 MB).
3. It downloads the file to a temporary location, sanitizes the filename, then moves it to the CWA ingest directory.
4. CWA picks it up and imports it into your Calibre library automatically.

## Installation

1. Clone this repository.
```bash
git clone https://github.com/pablo-alcaniz/cwa-ingest-bot
```
2. Enter the project directory.
```bash
cd cwa-ingest-bot
```
3. Modify `compose.yaml` as required (see Configuration section below).
4. Start the bot using Docker Compose.
```bash
docker compose up -d
```

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/ping` | Check connectivity to your CWA instance |
| `/help` | Show available commands |

## Requirements

- A running [Calibre-Web Automated](https://github.com/crocodilestick/Calibre-Web-Automated) instance with an ingest directory configured
- A Telegram bot token (obtain one from [@BotFather](https://t.me/BotFather))
- Docker + Docker Compose

Important note: make sure you set up your Telegram bot restricting user access in the BotFather settings. This bot does not implement its own authentication, so it will accept files from any Telegram user if not restricted. You can restrict access in the Bot Father > Your Bot > Bot Settings > Access > Restrict bot users. If you want to allow more than one user, you can specify what user are allowed in the same section of Bot Settings.

## Configuration

Copy `compose.yaml` and fill in the three placeholders:

| Variable | Description |
|----------|-------------|
| `BOT_TOKEN` | Telegram bot token from BotFather |
| `FULL_INGEST_DIR` | Full path to your CWA ingest directory on the host |
| `CWA_URL` | Base URL of your CWA instance (used by `/ping`) |


The container runs as UID/GID `1000:1000` by default. Adjust the `user:` field in `compose.yaml` if your ingest directory is owned by a different user.

NOTE: only modify fields marked with '[...]'. With the exception of `user:`, that only needs to be changed if your ingest directory is owned by a different user.

```yaml
volumes:
  - /path/to/your/cwa/ingest:/ingest
```

## Running

```bash
docker compose up -d
```

## Limits

- Only `.epub` files are accepted.
- Maximum file size: **20 MB** (CWA ingest limit).
