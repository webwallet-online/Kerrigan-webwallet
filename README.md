# 🔐 Kerrigan Web Wallet

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Non-Custodial](https://img.shields.io/badge/Non--Custodial-Yes-brightgreen)](https://github.com)
[![Open Source](https://img.shields.io/badge/Open%20Source-Yes-blue)](https://github.com)

> **A secure, non-custodial web wallet for Kerrigan (KRGN) cryptocurrency.**
> 
> *Your keys, your coins. Always.*

## 📖 Overview

Kerrigan Web Wallet is a **non-custodial** web-based wallet for the Kerrigan (KRGN) blockchain. It allows users to manage their KRGN coins directly from their browser **without ever exposing their private keys to the server**.

### 🎯 Key Features

| Feature | Description |
|---------|-------------|
| 🔐 **Non-Custodial** | Private keys never leave your browser. You remain in full control. |
| 💻 **Web-Based** | No installation required. Works on any modern browser. |
| 🔒 **Secure by Design** | All transaction signing happens client-side. The server only relays signed transactions. |
| 🛡️ **Anti-Spam Protection** | Rate limiting prevents abuse by IP address. |
| 📱 **Responsive** | Works on desktop, tablet, and mobile devices. |
| 🌐 **Open Source** | 100% transparent code. Anyone can audit. |

## 🏗️ Architecture




## 🔒 Security Model

### What Makes This Wallet Non-Custodial?

| Aspect | How it Works |
|--------|--------------|
| **Key Generation** | Your private keys are generated in your browser using cryptographically secure random number generation. |
| **Key Storage** | Keys are stored in your browser's `localStorage`. **Never** transmitted to any server. |
| **Transaction Signing** | All transaction signing happens in your browser using `bitcoinjs-lib` or similar client-side libraries. |
| **Server Role** | The server only: stores public addresses, authenticates users, and relays already-signed transactions. |
| **Private Keys** | **NEVER** touch the server. **NEVER** stored in any database. **NEVER** transmitted over the network. |

### What the Server Stores

| Data | Stored? | Notes |
|------|---------|-------|
| Private Keys | ❌ **NEVER** | This is the core security promise |
| Seed Phrases | ❌ **NEVER** | The seed never leaves your browser |
| Public Addresses | ✅ Yes | Required to identify your wallet |
| Login Keys | ✅ Yes | For session management |
| IP Addresses | ✅ Yes | For rate limiting and security logs |
| Transaction History | ✅ Yes | Public blockchain data |

### Security Best Practices Implemented

- ✅ **HttpOnly Cookies** - Prevents XSS access to session cookies
- ✅ **Secure Cookie Flag** - Cookies only sent over HTTPS
- ✅ **SameSite=Lax** - CSRF protection
- ✅ **Rate Limiting** - Prevents brute force and spam attacks
- ✅ **Input Validation** - All user inputs are validated and sanitized
- ✅ **Environment Variables** - No hardcoded credentials in code
- ✅ **Session Expiry** - Automatic logout after 2 hours of inactivity

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Kerrigan node running with RPC enabled
- SSL certificate for production (Let's Encrypt recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/kerrigan-wallet.git
cd kerrigan-wallet

# Install dependencies
pip install -r requirements.txt

# Copy environment variables template
cp .env.example .env

# Edit .env with your RPC credentials
nano .env

# Run the server
python server.py

# RPC Configuration
RPC_USER=your_rpc_username
RPC_PASS=your_rpc_password
RPC_PORT=7121

# Flask Security
SECRET_KEY=your_super_secret_key_here  # Generate with: python -c "import secrets; print(secrets.token_hex(32))"

# Server Configuration
PORT=8085


📡 API Endpoints
Method	Endpoint	Description
POST	/register	Register a new wallet (send ONLY public address)
POST	/login	Authenticate with login key
POST	/balance	Get wallet balance
POST	/broadcast	Broadcast a signed transaction
POST	/logout	End user session
GET	/health	Health check endpoint


# Register (client sends public address only)
curl -X POST https://your-server.com/register \
  -H "Content-Type: application/json" \
  -d '{"address": "KERRI...G4N"}'

# Login
curl -X POST https://your-server.com/login \
  -H "Content-Type: application/json" \
  -d '{"key": "your_login_key"}'

# Broadcast signed transaction
curl -X POST https://your-server.com/broadcast \
  -H "Content-Type: application/json" \
  -d '{"signed_tx": "020000000001..."}'


kerrigan-wallet/
├── server.py              # Flask backend (non-custodial)
├── index.html             # Frontend interface
├── styles.css             # Styling
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Files to exclude from git
├── kerrigan-logo.png      # Logo asset
├── Conthrax-SemiBold.otf  # Custom font
└── README.md              # This file


Key Security Points in server.py
Line Range	What to Verify
200-220	No private key storage
58-63	Session cookie security flags
77-112	Rate limiting implementation
153-159	Address validation
280-310	Transaction broadcast (no key handling)


What You Won't Find
❌ No privkey fields in database schema

❌ No endpoints that accept private keys

❌ No dumpprivkey RPC calls

❌ No storage of seed phrases

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

You are responsible for backing up your own private keys.

The developers are not responsible for any loss of funds.

Always verify the code before using with significant amounts.

🙏 Acknowledgments
Built with Flask, bitcoinjs-lib, and the Kerrigan blockchain

Inspired by non-custodial wallet best practices

Security audit recommendations from the open-source community

📞 Support
GitHub Issues: Report a bug

Security Concerns: Email security@yourdomain.com
