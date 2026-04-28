import hashlib
import os
from blog.db import query, execute


def hash_password(password):
    """Hash password using PBKDF2-SHA256."""
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt + key


def verify_password(password, stored):
    """Verify password against stored hash."""
    salt = stored[:32]
    key = stored[32:]
    new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return key == new_key


def get_user_by_id(user_id):
    return query('SELECT id, username, display_name, email, avatar, bio, role FROM users WHERE id = ?',
                 [user_id], one=True)


def get_user_by_username(username):
    return query('SELECT * FROM users WHERE username = ?', [username], one=True)


def create_user(username, password, display_name='', email='', role='editor'):
    pw_hash = hash_password(password)
    return execute(
        'INSERT INTO users (username, password_hash, display_name, email, role) VALUES (?, ?, ?, ?, ?)',
        [username, pw_hash, display_name, email, role]
    )


def update_user(user_id, display_name=None, email=None, bio=None, avatar=None):
    fields = []
    params = []
    if display_name is not None:
        fields.append('display_name = ?')
        params.append(display_name)
    if email is not None:
        fields.append('email = ?')
        params.append(email)
    if bio is not None:
        fields.append('bio = ?')
        params.append(bio)
    if avatar is not None:
        fields.append('avatar = ?')
        params.append(avatar)
    if not fields:
        return
    params.append(user_id)
    execute(f'UPDATE users SET {", ".join(fields)} WHERE id = ?', params)


def change_password(user_id, new_password):
    pw_hash = hash_password(new_password)
    execute('UPDATE users SET password_hash = ? WHERE id = ?', [pw_hash, user_id])
