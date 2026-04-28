import re
import os
import hashlib
import time
import uuid


def slugify(text):
    """Generate a URL-friendly slug from text."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-_')


def generate_slug(title):
    """Generate unique slug from title."""
    base = slugify(title)
    if not base:
        base = 'post'
    timestamp = int(time.time())
    return f'{base}-{timestamp}'


def allowed_file(filename, allowed_extensions=None):
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'ico'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_upload(file, upload_folder):
    """Save uploaded file and return the saved filename."""
    if file and allowed_file(file.filename):
        ext = os.path.splitext(file.filename)[1].lower() or '.png'
        unique_name = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(upload_folder, unique_name)
        file.save(filepath)
        return unique_name
    return None


def truncate_html(text, length=200):
    """Truncate text to given length, preserving words."""
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + '...'


def strip_html(text):
    """Remove HTML tags from text."""
    return re.sub(r'<[^>]+>', '', text)


def format_date(date_str, fmt='%Y-%m-%d'):
    """Format a date string."""
    if not date_str:
        return ''
    from datetime import datetime
    try:
        dt = datetime.strptime(date_str[:19], '%Y-%m-%d %H:%M:%S')
        return dt.strftime(fmt)
    except (ValueError, IndexError):
        return date_str[:10]
