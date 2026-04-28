import sqlite3
import os
from flask import g

DATABASE = None


def init_db(app):
    global DATABASE
    DATABASE = app.config['DATABASE']

    # Ensure directory exists
    db_dir = os.path.dirname(DATABASE)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    # Initialize schema
    with app.app_context():
        db = get_db()
        schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            db.executescript(f.read())
        db.commit()

    @app.teardown_appcontext
    def close_db(exception):
        db = g.pop('db', None)
        if db is not None:
            db.close()


def get_db():
    if 'db' not in g:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA foreign_keys=ON')
        g.db = conn
    return g.db


def query(sql, params=None, one=False):
    db = get_db()
    cursor = db.execute(sql, params or [])
    if one:
        return cursor.fetchone()
    return cursor.fetchall()


def execute(sql, params=None):
    db = get_db()
    cursor = db.execute(sql, params or [])
    db.commit()
    return cursor.lastrowid
