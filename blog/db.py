import os
from datetime import date, datetime

import pymysql
from flask import g

DB_CONFIG = None


def init_db(app):
    global DB_CONFIG
    DB_CONFIG = {
        'host': app.config['MYSQL_HOST'],
        'port': app.config['MYSQL_PORT'],
        'user': app.config['MYSQL_USER'],
        'password': app.config['MYSQL_PASSWORD'],
        'database': app.config['MYSQL_DATABASE'],
        'charset': app.config.get('MYSQL_CHARSET', 'utf8mb4'),
        'cursorclass': pymysql.cursors.DictCursor,
        'autocommit': False,
    }

    with app.app_context():
        db = get_db()
        schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            for statement in split_sql_statements(f.read()):
                with db.cursor() as cursor:
                    cursor.execute(statement)
        db.commit()

    @app.teardown_appcontext
    def close_db(exception):
        db = g.pop('db', None)
        if db is not None:
            db.close()


def split_sql_statements(sql):
    lines = []
    for line in sql.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('--'):
            continue
        lines.append(line)
    return [stmt.strip() for stmt in '\n'.join(lines).split(';') if stmt.strip()]


def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(**DB_CONFIG)
    return g.db


def format_row_dates(row):
    if row is None:
        return None
    for key, value in row.items():
        if isinstance(value, datetime):
            row[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(value, date):
            row[key] = value.strftime('%Y-%m-%d')
    return row


def query(sql, params=None, one=False):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(sql, params or ())
        if one:
            return format_row_dates(cursor.fetchone())
        return [format_row_dates(row) for row in cursor.fetchall()]


def execute(sql, params=None):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(sql, params or ())
        db.commit()
        return cursor.lastrowid
