#!/usr/bin/env python3
"""
Kerrigan Web Wallet - Non-Custodial Backend

A secure, transparent, non-custodial web wallet for Kerrigan (KRGN) cryptocurrency.
Private keys never leave the user's browser. The server only stores public addresses.

Features:
- Non-custodial: Keys are generated and stored client-side
- Rate limiting: Prevents abuse by IP address
- REST API: Register, login, balance, broadcast
- Session management: Secure cookie-based sessions
- Open source: 100% transparent and auditable

Environment variables required:
- RPC_USER: Kerrigan node RPC username
- RPC_PASS: Kerrigan node RPC password
- RPC_PORT: Kerrigan node RPC port (default: 7121)
- SECRET_KEY: Flask session secret key (auto-generated if not set)
"""

import os
import json
import secrets
import time
import re
from datetime import timedelta
from collections import defaultdict
import requests
import base64
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from flask_session import Session

# ============================================================================
# FLASK APPLICATION SETUP
# ============================================================================

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app, supports_credentials=True)

# Session configuration
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = True  # Set to False if using HTTP only
app.config["SESSION_COOKIE_SAMESITE"] = 'Lax'
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=2)
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024  # 1MB max request size
Session(app)

# ============================================================================
# RATE LIMITING (Anti-Spam)
# ============================================================================

registrations_by_ip = defaultdict(list)
login_attempts_by_ip = defaultdict(list)
broadcasts_by_ip = defaultdict(list)

MAX_REGISTRATIONS_PER_HOUR = 5
MAX_LOGIN_ATTEMPTS_PER_MINUTE = 10
MAX_BROADCASTS_PER_IP = 20

def clean_old_entries(records, max_age_seconds):
    """Remove entries older than max_age_seconds"""
    now = time.time()
    return [t for t in records if now - t < max_age_seconds]

def is_rate_limited(records, max_count, time_window_seconds, identifier):
    """Check if an IP has exceeded its rate limit"""
    cleaned = clean_old_entries(records, time_window_seconds)
    records[:] = cleaned
    if len(cleaned) >= max_count:
        return True
    records.append(time.time())
    return False

# ============================================================================
# RPC CONFIGURATION (Connect to Kerrigan Node)
# ============================================================================
# IMPORTANT: Use environment variables for credentials - NEVER hardcode!
# Set these in your production environment:
#   export RPC_USER=your_rpc_username
#   export RPC_PASS=your_rpc_password
#   export RPC_PORT=7121

RPC_USER = os.environ.get('RPC_USER', 'rpcuser')
RPC_PASS = os.environ.get('RPC_PASS', 'rpcpassword')
RPC_PORT = os.environ.get('RPC_PORT', '7121')
RPC_URL = f"http://127.0.0.1:{RPC_PORT}"

# ============================================================================
# USER DATABASE (Stores ONLY public addresses - NO PRIVATE KEYS!)
# ============================================================================

USERS_FILE = "users.json"

def load_users():
    """Load users from JSON file (public addresses only)"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            return {}
    return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

user_keys = load_users()

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def is_valid_address(address):
    """Validate Kerrigan address format (starts with K, 30-40 chars)"""
    if not address:
        return False
    if len(address) < 30 or len(address) > 40:
        return False
    if not address.startswith('K'):
        return False
    return True

def is_valid_transaction_hex(tx_hex):
    """Validate transaction hex format"""
    if not tx_hex:
        return False
    return bool(re.match(r'^[0-9a-fA-F]{64,}$', tx_hex))

# ============================================================================
# RPC HELPERS (Communicate with Kerrigan Node)
# ============================================================================

def rpc_call(method, params=None):
    """Make JSON-RPC call to the Kerrigan node"""
    if params is None:
        params = []
    payload = {
        "jsonrpc": "1.0",
        "id": "kerrigan",
        "method": method,
        "params": params
    }
    auth_str = f"{RPC_USER}:{RPC_PASS}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + base64.b64encode(auth_str.encode()).decode()
    }
    try:
        response = requests.post(RPC_URL, headers=headers, data=json.dumps(payload), timeout=30)
        return response.json()
    except Exception as e:
        return {"error": str(e), "result": None}

def get_balance(address):
    """Get balance for a given public address"""
    try:
        result = rpc_call("getbalance", [address])
        if result.get("error"):
            return 0
        return result.get("result", 0)
    except Exception:
        return 0

def broadcast_transaction(signed_tx_hex):
    """Broadcast a signed transaction to the network"""
    try:
        result = rpc_call("sendrawtransaction", [signed_tx_hex])
        if result.get("error"):
            raise Exception(result["error"])
        return result.get("result")
    except Exception as e:
        raise Exception(f"Broadcast failed: {e}")

# ============================================================================
# STATIC FILE SERVING
# ============================================================================

@app.route('/')
def serve_index():
    """Serve the main frontend interface"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static assets (CSS, JS, images, fonts)"""
    allowed_extensions = ('.html', '.css', '.js', '.ico', '.png', '.jpg', '.svg', '.txt', '.otf', '.ttf', '.woff', '.woff2')
    if not any(path.endswith(ext) for ext in allowed_extensions):
        return "Forbidden", 403
    if '..' in path or path.startswith('.'):
        return "Forbidden", 403
    return send_from_directory('.', path)

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route("/register", methods=["POST"])
def register():
    """
    🔐 NON-CUSTODIAL REGISTRATION
    =============================
    The client generates its own private key and sends ONLY the public address.
    This server NEVER sees or stores the private key.
    """
    ip = request.remote_addr
    
    if is_rate_limited(registrations_by_ip[ip], MAX_REGISTRATIONS_PER_HOUR, 3600, ip):
        return jsonify({"error": "Too many registrations. Please wait."}), 429
    
    try:
        data = request.json
        address = data.get("address") if data else None
        
        if not address or not is_valid_address(address):
            return jsonify({"error": "Invalid address format"}), 400
        
        login_key = secrets.token_hex(16)
        user_keys[login_key] = {
            "address": address,
            "created_ip": ip,
            "created_at": time.time()
        }
        save_users(user_keys)
        
        return jsonify({
            "success": True,
            "login_key": login_key,
            "address": address
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/login", methods=["POST"])
def login():
    """Authenticate user and establish session"""
    ip = request.remote_addr
    
    if is_rate_limited(login_attempts_by_ip[ip], MAX_LOGIN_ATTEMPTS_PER_MINUTE, 60, ip):
        return jsonify({"error": "Too many login attempts. Please wait."}), 429
    
    try:
        data = request.json
        key = data.get("key")
        
        if not key or key not in user_keys:
            return jsonify({"error": "Invalid login key"}), 401
        
        session["user_key"] = key
        session.permanent = True
        address = user_keys[key]["address"]
        balance = get_balance(address)
        
        return jsonify({
            "success": True,
            "address": address,
            "balance": balance
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/balance", methods=["POST"])
def balance():
    """Get current balance for the logged-in user (requires session)"""
    try:
        key = session.get("user_key")
        if not key or key not in user_keys:
            return jsonify({"error": "Not logged in"}), 401
        address = user_keys[key]["address"]
        balance = get_balance(address)
        return jsonify({"success": True, "balance": balance})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/balance_by_key", methods=["POST"])
def balance_by_key():
    """Get balance using login key directly (no session required)"""
    try:
        data = request.json
        key = data.get("key")
        if not key or key not in user_keys:
            return jsonify({"error": "Invalid login key"}), 401
        address = user_keys[key]["address"]
        balance = get_balance(address)
        return jsonify({"success": True, "address": address, "balance": balance})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/broadcast", methods=["POST"])
def broadcast():
    """
    🔐 NON-CUSTODIAL TRANSACTION BROADCAST
    ======================================
    The client signs the transaction in its browser using its private key.
    The server receives ONLY the already-signed transaction hex.
    The server NEVER sees the private key!
    """
    ip = request.remote_addr
    
    if is_rate_limited(broadcasts_by_ip[ip], MAX_BROADCASTS_PER_IP, 60, ip):
        return jsonify({"error": "Too many transactions. Please wait."}), 429
    
    try:
        key = session.get("user_key")
        if not key or key not in user_keys:
            return jsonify({"error": "Not logged in"}), 401
        
        data = request.json
        signed_tx = data.get("signed_tx")
        
        if not signed_tx or not is_valid_transaction_hex(signed_tx):
            return jsonify({"error": "Invalid transaction format"}), 400
        
        tx_hash = broadcast_transaction(signed_tx)
        return jsonify({"success": True, "tx_hash": tx_hash})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/logout", methods=["POST"])
def logout():
    """Clear user session"""
    session.clear()
    return jsonify({"success": True})


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint for monitoring"""
    return jsonify({"status": "healthy", "non_custodial": True})


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    PORT = int(os.environ.get('PORT', 8086))
    HOST = os.environ.get('HOST', '0.0.0.0')
    
    print("=" * 60)
    print("Kerrigan Web Wallet - Non-Custodial Backend")
    print("=" * 60)
    print(f"RPC URL: {RPC_URL}")
    print(f"Server running on http://{HOST}:{PORT}")
    print("=" * 60)
    print("🔐 SECURITY: This server NEVER stores private keys")
    print("📖 Open Source: https://github.com/YOUR_USERNAME/kerrigan-wallet")
    print("=" * 60)
    
    app.run(host=HOST, port=PORT, debug=False)
