from flask import Flask, render_template, request, session, send_file
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import json
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

LOG_FILE = 'chat_logs.enc'
REPORT_FILE = 'project_report.pdf'
sections = [
    ("Introduction", "This project implements a secure real-time chat application with end-to-end encryption (E2EE) using public key cryptography. The goal is to ensure that only intended recipients can read the messages, providing privacy and security for users."),
    ("Abstract", "The chat application leverages RSA for key exchange and AES for encrypting messages. Each user generates an RSA keypair, shares their public key, and uses AES for message encryption. The AES key is securely shared with recipients using RSA encryption. All messages are transmitted and stored in encrypted form, ensuring confidentiality even if the server is compromised."),
    ("Tools Used", "- Python 3\n- Flask & Flask-SocketIO\n- cryptography (RSA/AES)\n- reportlab (for PDF generation)\n- HTML/JavaScript (WebCrypto API)"),
    ("Steps Involved in Building the Project", "1. Set up Flask backend with SocketIO for real-time communication.\n2. Implement user registration and RSA keypair generation (client-side).\n3. Exchange public keys between users via the server.\n4. Encrypt messages with AES; encrypt AES key with recipient's RSA public key.\n5. Relay encrypted messages and keys via the server.\n6. Decrypt messages only on the client side.\n7. Store encrypted chat logs on the server.\n8. Generate this report as a project summary."),
    ("Conclusion", "The project demonstrates a practical approach to secure, real-time communication using end-to-end encryption. By combining RSA and AES, it ensures that messages remain confidential and accessible only to intended recipients, even if the server is compromised.")
]

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app, async_mode='eventlet')

# In-memory user store: {username: {public_key, sid}}
users = {}

@app.route('/')
def index():
    return render_template('index.html')

    f.write(json.dumps(log_entry) + '\n')


@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    to_remove = None
    for u, v in users.items():
        if v['sid'] == request.sid:
            to_remove = u
            break
    if to_remove:
        del users[to_remove]
        print(f"User {to_remove} removed from users list")
        emit('user_list', {'users': list(users.keys())}, broadcast=True)


# --- Report generation and route ---
def generate_report():
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "Secure Chat E2EE Project Report")
    y -= 40
    c.setFont("Helvetica", 12)
    for title, content in sections:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, title)
        y -= 20
        c.setFont("Helvetica", 12)
        for line in content.split('\n'):
            for subline in [line[i:i+90] for i in range(0, len(line), 90)]:
                c.drawString(60, y, subline)
                y -= 16
                if y < 60:
                    c.showPage()
                    y = height - 50
        y -= 16
        if y < 60:
            c.showPage()
            y = height - 50
    c.save()
    buffer.seek(0)
    return buffer

@app.route('/report')
def report():
    pdf_buffer = generate_report()
    return send_file(pdf_buffer, as_attachment=True, download_name=REPORT_FILE, mimetype='application/pdf')

if __name__ == '__main__':
    socketio.run(app, debug=True)

@socketio.on('get_public_keys')
def handle_get_public_keys():
    # Send all users' public keys
    emit('public_keys', {u: users[u]['public_key'] for u in users})

@socketio.on('send_message')
def handle_send_message(data):
    # data: {to, from, encrypted_message, encrypted_keys: {recipient: encrypted_aes_key}, iv}
    to = data.get('to')
    sender = data.get('from')
    
    if to in users:
        # Send message to recipient
        emit('receive_message', data, room=users[to]['sid'])
        # Send confirmation to sender
        emit('message_sent', {'success': True, 'to': to})
        print(f"Message sent from {sender} to {to}")
    else:
        # Send error to sender if recipient not found
        emit('message_sent', {'success': False, 'error': f'User {to} not found', 'to': to})
        print(f"Failed to send message: User {to} not found")
    
    # Store encrypted log
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'from': sender,
        'to': to,
        'encrypted_message': data.get('encrypted_message'),
        'iv': data.get('iv'),
        'encrypted_keys': data.get('encrypted_keys')
    }
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry) + '\n')

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    # Remove user by sid
    to_remove = None
    for u, v in users.items():
        if v['sid'] == request.sid:
            to_remove = u
            break
    if to_remove:
        del users[to_remove]
        print(f"User {to_remove} removed from users list")
        emit('user_list', {'users': list(users.keys())}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)