from blog.db import query, execute
import time

_settings_cache = None
_settings_cache_time = 0
_CACHE_TTL = 60  # seconds


def get_all_settings():
    global _settings_cache, _settings_cache_time
    now = time.time()
    if _settings_cache is not None and (now - _settings_cache_time) < _CACHE_TTL:
        return _settings_cache
    rows = query('SELECT * FROM settings')
    _settings_cache = {row['key']: row['value'] for row in rows}
    _settings_cache_time = now
    return _settings_cache


def invalidate_settings_cache():
    global _settings_cache, _settings_cache_time
    _settings_cache = None
    _settings_cache_time = 0


def get_setting(key, default=''):
    row = query('SELECT value FROM settings WHERE `key` = %s', [key], one=True)
    return row['value'] if row else default


def set_setting(key, value):
    execute(
        'INSERT INTO settings (`key`, value) VALUES (%s, %s) '
        'ON DUPLICATE KEY UPDATE value = VALUES(value)',
        [key, value]
    )
    invalidate_settings_cache()


def update_settings(settings_dict):
    for key, value in settings_dict.items():
        set_setting(key, value)
