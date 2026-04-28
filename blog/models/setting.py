from blog.db import query, execute


def get_all_settings():
    rows = query('SELECT * FROM settings')
    return {row['key']: row['value'] for row in rows}


def get_setting(key, default=''):
    row = query('SELECT value FROM settings WHERE key = ?', [key], one=True)
    return row['value'] if row else default


def set_setting(key, value):
    execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', [key, value])


def update_settings(settings_dict):
    for key, value in settings_dict.items():
        set_setting(key, value)
