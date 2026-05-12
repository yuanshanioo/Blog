import re
import os
import time


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-_')


def generate_slug(title):
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
