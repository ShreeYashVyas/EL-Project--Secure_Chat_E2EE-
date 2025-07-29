
# Secure E2EE Chat App

A secure chat application with end-to-end encryption using Flask, Flask-SocketIO, and cryptography (RSA/AES).

## Features
- End-to-end encrypted messaging (RSA/AES)
- Real-time chat (Flask-SocketIO)
- Encrypted chat logs
- Simple web UI

## Setup
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Run the server:
   ```
   python app.py
   ```
3. Open your browser at http://localhost:5000

## Usage
- Enter a username and join the chat.
- Messages are encrypted end-to-end and only decrypted on the client. 
