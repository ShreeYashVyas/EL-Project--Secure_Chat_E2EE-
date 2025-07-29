
let socket;
let username = '';
let rsaKeyPair = null;
let publicKeys = {};

async function generateRSAKeyPair() {
    return await window.crypto.subtle.generateKey(
        {
            name: 'RSA-OAEP',
            modulusLength: 2048,
            publicExponent: new Uint8Array([1, 0, 1]),
            hash: 'SHA-256',
        },
        true,
        ['encrypt', 'decrypt']
    );
}

async function exportPublicKey(key) {
    const spki = await window.crypto.subtle.exportKey('spki', key);
    return btoa(String.fromCharCode(...new Uint8Array(spki)));
}

async function registerUser() {
    username = document.getElementById('username').value;
    if (!username) return alert('Enter username');
    rsaKeyPair = await generateRSAKeyPair();
    const pubKeyB64 = await exportPublicKey(rsaKeyPair.publicKey);
    socket = io();
    socket.emit('register', {username: username, public_key: pubKeyB64});
    document.getElementById('username').disabled = true;
    
    // Set up message receiving handler
    socket.on('receive_message', async (data) => {
        // Only decrypt if this message is for us
        if (data.to !== username) return;
        const encryptedKeyB64 = data.encrypted_keys[username];
        if (!encryptedKeyB64) return;
        try {
            const encryptedKey = Uint8Array.from(atob(encryptedKeyB64), c => c.charCodeAt(0));
            const aesKeyRaw = await decryptAESKeyWithRSA(encryptedKey, rsaKeyPair.privateKey);
            const aesKey = await window.crypto.subtle.importKey('raw', aesKeyRaw, { name: 'AES-GCM' }, false, ['decrypt']);
            const ciphertext = Uint8Array.from(atob(data.encrypted_message), c => c.charCodeAt(0));
            const iv = Uint8Array.from(atob(data.iv), c => c.charCodeAt(0));
            const plaintext = await decryptMessageAES(aesKey, iv, ciphertext);
            const messagesDiv = document.getElementById('messages');
            const messageElement = document.createElement('div');
            messageElement.innerHTML = `<b>${data.from}:</b> ${plaintext}`;
            messagesDiv.appendChild(messageElement);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        } catch (error) {
            console.error('Error decrypting message:', error);
        }
    });
    
    socket.on('register_response', (data) => {
        if (data.success) {
            socket.emit('get_public_keys');
        } else {
            alert('Registration failed: ' + data.error);
        }
    });
    socket.on('public_keys', (data) => {
        publicKeys = data;
        // Remove own key
        delete publicKeys[username];
        updateRecipientList();
    });
    socket.on('user_list', (data) => {
        // Always refresh public keys when user list changes
        socket.emit('get_public_keys');
    });
    socket.on('message_sent', (data) => {
        if (!data.success) {
            console.error(`Failed to send message: ${data.error}`);
        }
    });
}

async function importPublicKey(spkiB64) {
    const binary = Uint8Array.from(atob(spkiB64), c => c.charCodeAt(0));
    return await window.crypto.subtle.importKey(
        'spki',
        binary,
        {
            name: 'RSA-OAEP',
            hash: 'SHA-256',
        },
        true,
        ['encrypt']
    );
}

async function generateAESKey() {
    return await window.crypto.subtle.generateKey(
        { name: 'AES-GCM', length: 256 },
        true,
        ['encrypt', 'decrypt']
    );
}

async function exportAESKey(key) {
    const raw = await window.crypto.subtle.exportKey('raw', key);
    return new Uint8Array(raw);
}

async function encryptAESKeyWithRSA(aesKeyRaw, publicKey) {
    return new Uint8Array(await window.crypto.subtle.encrypt(
        { name: 'RSA-OAEP' },
        publicKey,
        aesKeyRaw
    ));
}

async function encryptMessageAES(aesKey, plaintext) {
    const enc = new TextEncoder();
    const iv = window.crypto.getRandomValues(new Uint8Array(12));
    const ciphertext = await window.crypto.subtle.encrypt(
        { name: 'AES-GCM', iv: iv },
        aesKey,
        enc.encode(plaintext)
    );
    return { ciphertext: new Uint8Array(ciphertext), iv };
}

async function decryptAESKeyWithRSA(encryptedKey, privateKey) {
    return await window.crypto.subtle.decrypt(
        { name: 'RSA-OAEP' },
        privateKey,
        encryptedKey
    );
}

async function decryptMessageAES(aesKey, iv, ciphertext) {
    const plaintext = await window.crypto.subtle.decrypt(
        { name: 'AES-GCM', iv: iv },
        aesKey,
        ciphertext
    );
    return new TextDecoder().decode(plaintext);
}

async function sendMessage() {
    const msg = document.getElementById('message').value;
    if (!msg) return;
    const recipient = document.getElementById('recipient').value;
    if (!recipient) {
        alert('Select a recipient.');
        return;
    }
    const aesKey = await generateAESKey();
    const aesKeyRaw = await exportAESKey(aesKey);
    const pubKeyB64 = publicKeys[recipient];
    const pubKey = await importPublicKey(pubKeyB64);
    const encrypted = await encryptAESKeyWithRSA(aesKeyRaw, pubKey);
    const encryptedKeyB64 = btoa(String.fromCharCode(...encrypted));
    const { ciphertext, iv } = await encryptMessageAES(aesKey, msg);
    const messageData = {
        to: recipient,
        from: username,
        encrypted_message: btoa(String.fromCharCode(...ciphertext)),
        iv: btoa(String.fromCharCode(...iv)),
        encrypted_keys: { [recipient]: encryptedKeyB64 }
    };
    socket.emit('send_message', messageData);
    document.getElementById('message').value = '';
}

function updateRecipientList() {
    const recipientSelect = document.getElementById('recipient');
    recipientSelect.innerHTML = '';
    const users = Object.keys(publicKeys);
    for (const user of users) {
        const option = document.createElement('option');
        option.value = user;
        option.textContent = user;
        recipientSelect.appendChild(option);
    }
}
