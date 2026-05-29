# Security Policy

## Credentials

This project requires several API keys and credentials. **Never commit them to the repository.**

| File | Contains | Action |
|---|---|---|
| `backend/.env` | API keys, tokens | gitignored — use `env.example` |
| `backend/credentials/*.json` | Google service account | gitignored |
| `firmware/include/config.h` | WiFi password, backend URL | gitignored — use `config.example.h` |

## Device API Key

For production use, set `DEVICE_API_KEY` in `.env`. The ESP32 must send this as the `X-Device-Key` header. Without it set, the endpoint is open (suitable for local network only).

## Google Sheets Access

The service account should have **Viewer** access for read-only sync and **Editor** only if you use the Telegram bot to write new transactions. Grant the minimum required permission.

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Email: **vanduongk1309@gmail.com**

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact

I will respond within 7 days.
