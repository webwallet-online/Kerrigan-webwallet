# 🔐 Kerrigan Web Wallet

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Non-Custodial](https://img.shields.io/badge/Non--Custodial-Yes-brightgreen)](https://github.com)
[![Open Source](https://img.shields.io/badge/Open%20Source-Yes-blue)](https://github.com)

> **A secure, open source, non-custodial web wallet for Kerrigan (KRGN) cryptocurrency.**
> 
> *Your keys, your coins. Always.*

## 📖 Overview

Kerrigan Web Wallet is a **non-custodial** web-based wallet for the Kerrigan (KRGN) blockchain. It allows users to manage their KRGN coins directly from their browser **without ever exposing their private keys to the server**.

### 🎯 Key Features

| Feature | Description |
|---------|-------------|
| 🔐 **Non-Custodial** | Private keys never leave your browser. You remain in full control. |
| 💻 **Web-Based** | No installation required. Works on any modern browser. |
| 🔒 **Secure by Design** | Keys are generated and stored in your browser's localStorage. |
| 🛡️ **Anti-Spam Protection** | Rate limiting prevents abuse by IP address. |
| 📱 **Responsive** | Works on desktop, tablet, and mobile devices. |
| 🌐 **Open Source** | 100% transparent code. Anyone can audit. |

## 🏗️ Architecture

The system has three parts that work together:

**1. The User's Browser (Frontend)**
Private keys are generated here, stored in localStorage, and transactions are signed here. Private keys never leave your browser.

**2. Your Server (Backend)**
Only stores public addresses and login keys. Never sees private keys. Verifies user identity and relays signed transactions to the node.

**3. The Kerrigan Node (Blockchain)**
The network's ledger. Stores all transactions and confirms balances. Your server talks to it to check balances and broadcast transactions.

**How it works:**

- **Registration:** Browser generates seed phrase and public address. Sends ONLY the public address to the server. Server returns a login key.
- **Login:** Browser sends login key to server. Server returns address and balance.
- **Balance Check:** Server queries the Kerrigan node and returns the result.
- **Send Coins:** Browser signs transaction with private key (locally). Sends signed transaction to server. Server relays to the Kerrigan node.

**The bottom line:** Your private keys never travel. Only already-signed transactions do. We cannot take your money. We cannot see your keys.

## 🔒 Security Model

### What Makes This Wallet Non-Custodial?

| Aspect | How it Works |
|--------|--------------|
| **Key Generation** | Your seed phrase is generated in your browser using cryptographically secure random number generation. |
| **Key Storage** | Keys are stored in your browser's `localStorage`. Never transmitted to any server. |
| **Server Role** | The server only: stores public addresses, authenticates users, and relays already-signed transactions. |
| **Private Keys** | NEVER touch the server. NEVER stored in any database. NEVER transmitted over the network. |

### What the Server Stores

| Data | Stored? | Notes |
|------|---------|-------|
| Private Keys | ❌ NEVER | This is the core security promise |
| Seed Phrases | ❌ NEVER | The seed never leaves your browser |
| Public Addresses | ✅ Yes | Required to identify your wallet |
| Login Keys | ✅ Yes | For session management |
| IP Addresses | ✅ Yes | For rate limiting and security logs |

### Security Best Practices Implemented

- ✅ **Rate Limiting** - Prevents brute force and spam attacks
- ✅ **Input Validation** - All user inputs are validated and sanitized
- ✅ **Session Expiry** - Automatic logout after 2 hours of inactivity
- ✅ **Non-Custodial by Design** - No private key storage on server

## 🔍 How to Audit

This wallet is 100% transparent. You can verify:

1. **No private key storage** - Check `server.py` lines 200-220
2. **No key transmission** - Search for "privkey" in the codebase
3. **Rate limiting** - Lines 77-112 protect against spam
4. **Address validation** - Lines 153-159 ensure valid Kerrigan addresses

Run locally and inspect network traffic to confirm no keys leave your browser.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Kerrigan node running with RPC enabled on port 7121
- SSL certificate for production (Let's Encrypt recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/kerrigan-wallet.git
cd kerrigan-wallet

# Install dependencies
pip install flask flask-cors flask-session requests

# Run the server
python server.py
Server Configuration
The server runs on port 8086 by default. Make sure your Kerrigan node RPC is accessible at 127.0.0.1:7121 with credentials:

python
RPC_USER = "your_rpc_username"
RPC_PASS = "your_rpc_password"
RPC_PORT = 7121
📡 API Endpoints
Method	Endpoint	Description
POST	/register	Register a new wallet (send ONLY public address)
POST	/login	Authenticate with login key
POST	/balance	Get wallet balance (requires session)
POST	/balance_by_key	Get balance using login key (no session needed)
POST	/broadcast	Broadcast a signed transaction
POST	/logout	End user session
GET	/health	Health check endpoint
Example API Calls
bash
# Register (client sends public address only)
curl -X POST http://localhost:8086/register \
  -H "Content-Type: application/json" \
  -d '{"address": "KERRI...G4N"}'

# Login
curl -X POST http://localhost:8086/login \
  -H "Content-Type: application/json" \
  -d '{"key": "your_login_key"}'

# Get balance by key (no session needed)
curl -X POST http://localhost:8086/balance_by_key \
  -H "Content-Type: application/json" \
  -d '{"key": "your_login_key"}'

# Health check
curl http://localhost:8086/health
Project Structure
text
kerrigan-wallet/
├── server.py              # Flask backend (non-custodial)
├── index.html             # Frontend interface with terminal style
├── styles.css             # Styling
├── requirements.txt       # Python dependencies
├── .gitignore             # Files to exclude from git
├── kerrigan-logo.png      # Logo asset
└── README.md              # This file
Apache Configuration (Production)
apache
<VirtualHost *:80>
    ServerName kerrigan.yourdomain.com
    Redirect permanent / https://kerrigan.yourdomain.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName kerrigan.yourdomain.com

    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/kerrigan.yourdomain.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/kerrigan.yourdomain.com/privkey.pem

    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8086/
    ProxyPassReverse / http://127.0.0.1:8086/

    ErrorLog ${APACHE_LOG_DIR}/kerrigan-error.log
    CustomLog ${APACHE_LOG_DIR}/kerrigan-access.log combined
</VirtualHost>
```

What You Won't Find
❌ No privkey fields in database schema

❌ No endpoints that accept private keys

❌ No storage of seed phrases on server

❌ No way for the server to access your funds

🤝 Contributing
Fork the repository

Create your feature branch (git checkout -b feature/amazing-feature)

Commit your changes (git commit -m 'Add amazing feature')

Push to the branch (git push origin feature/amazing-feature)

Open a Pull Request

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

⚠️ Disclaimer
THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.

You are responsible for backing up your own private keys and seed phrases.

The developers are not responsible for any loss of funds.

Always verify the code before using with significant amounts.

This is a non-custodial wallet. The server never has access to your keys.

🙏 Acknowledgments
Built with Flask and Kerrigan RPC

Inspired by non-custodial wallet best practices

Terminal UI design from the crypto community

Made with 🔒 for the Kerrigan community
