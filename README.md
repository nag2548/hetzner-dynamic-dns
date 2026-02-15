# hetzner-dynamic-dns

Lightweight dynamic DNS updater for **Hetzner DNS** using the official API.

This tool updates a Hetzner DNS **A record** to match your current public IPv4 address.  
Perfect for home servers, dynamic IP connections, or self-hosted services.

---

## ✨ Features

- Updates an existing A record if IP changed
- Creates the record if it does not exist
- Uses the official Hetzner Cloud API

---

## 🔧 Requirements

- Python ≥ 3.10
- A Hetzner DNS zone
- Hetzner API token with read/write permissions
- Dependency management:
    - Recommended: **uv** (used in the instructions below)
    - Alternative: any standard Python virtual environment + dependency installer

---

## 🚀 Server usage (cron)

### 1) Get the code onto the server

```bash
git clone https://github.com/nag2548/hetzner-dynamic-dns 
cd hetzner-dynamic-dns
```

### 2) Configure environment variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Fill in:

- `ZONE_NAME` — your DNS zone (e.g. `example.com`)
- `RECORD_NAME` — the record name inside the zone (e.g. `home` or `dyn`)
- `API_TOKEN` — Hetzner API token with DNS read/write permissions

### 3) Install dependencies (recommended one-time step)

Using `uv`:

```bash
uv sync
```

This prepares the project environment ahead of time so the cron job doesn’t download/install packages at runtime.

### 4) Test run manually

From the project directory:

```bash
uv run python -m src.hetzner_dynamic_dns
```

### 5) Add a cron job

Edit your crontab:

```bash
crontab -e
```

Example: run every 5 minutes and write logs to a file:

```bash
*/5 * * * * cd /absolute/path/to/hetzner-dynamic-dns && /absolute/path/to/uv run python -m src.hetzner_dynamic_dns
```

Notes:

- Use **absolute paths** in cron (`/absolute/path/to/...`) because cron runs with a minimal `PATH`.
- The `cd ...` ensures the project root is the working directory (useful if you rely on `.env`).
