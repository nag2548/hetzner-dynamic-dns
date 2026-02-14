# hetzner-dynamic-dns

Lightweight dynamic DNS updater for **Hetzner DNS** using the official API.

This tool updates a Hetzner DNS **A record** to match your current public IPv4 address.  
Perfect for home servers, dynamic IP connections, or self-hosted services.

---

## ✨ Features

- Updates an existing A record if IP changed
- Creates the record if it does not exist
- Uses the official Hetzner DNS API

---

## 🔧 Requirements

- Python ≥ 3.10
- A Hetzner DNS zone
- Hetzner API token with read / write permissions
