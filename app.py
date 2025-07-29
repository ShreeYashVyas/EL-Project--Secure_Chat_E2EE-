from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import json
from datetime import datetime
import eventlet
import eventlet.wsgi

LOG_FILE = 'chat_logs.enc'

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app, async_mode='eventlet')

# In-memory user store: {username: {public_key, sid}}
users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    # Join user to their own room for direct messaging
    join_room(request.sid)

@socketio.on('register')
def handle_register(data):
    username = data.get('username')
    public_key = data.get('public_key')
    if not username or not public_key:
        emit('register_response', {'success': False, 'error': 'Missing username or public key'})
        return
    
    # Join user to their own room for direct messaging
    join_room(request.sid)
    users[username] = {'public_key': public_key, 'sid': request.sid}
    emit('register_response', {'success': True, 'username': username})
    print(f"User {username} registered with SID: {request.sid}")
    # Notify all users of new user list
    emit('user_list', {'users': list(users.keys())}, broadcast=True)

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