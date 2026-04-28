import os
from flask import Flask, render_template, session

def create_app(config_name='development'):
    app = Flask(__name__,
                static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'),
                template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'))

    if config_name == 'production':
        app.config.from_object('config.ProductionConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')

    from blog.db import init_db
    init_db(app)

    # Ensure upload directory exists
    upload_dir = app.config.get('UPLOAD_FOLDER',
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads'))
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    @app.before_request
    def count_visitor():
        if not session.get('visitor_counted'):
            from blog.models.setting import set_setting, get_setting
            count = int(get_setting('site_visits', '0')) + 1
            set_setting('site_visits', str(count))
            session['visitor_counted'] = True

    from blog.routes.main import main_bp
    from blog.routes.admin import admin_bp
    from blog.routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.template_filter('rssdate')
    def rssdate_filter(date_str):
        from datetime import datetime
        try:
            dt = datetime.strptime(date_str[:19], '%Y-%m-%d %H:%M:%S')
            return dt.strftime('%a, %d %b %Y %H:%M:%S +0000')
        except (ValueError, IndexError):
            return date_str

    @app.template_filter('datecn')
    def datecn_filter(date_str):
        """Format 2026-04-27 -> 2026年04月27日"""
        from datetime import datetime
        try:
            dt = datetime.strptime(date_str[:10], '%Y-%m-%d')
            return dt.strftime('%Y年%m月%d日')
        except (ValueError, IndexError):
            return date_str[:10]

    @app.template_filter('slugify')
    def slugify_filter(text):
        import re
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-_')

    @app.context_processor
    def inject_globals():
        from blog.models.setting import get_all_settings
        settings = get_all_settings()
        cat_list = _get_nav_categories()
        from blog.models.setting import get_setting
        return {
            'settings': settings,
            'nav_categories': cat_list,
            'current_year': 2026,
            'visitor_count': get_setting('site_visits', '0')
        }

    @app.errorhandler(404)
    def not_found(e):
        return render_template('frontend/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('frontend/500.html'), 500

    return app


def _get_nav_categories():
    from blog.db import get_db
    db = get_db()
    rows = db.execute(
        'SELECT * FROM categories ORDER BY parent_id IS NULL, parent_id, sort_order'
    ).fetchall()
    parents = [r for r in rows if r['parent_id'] is None]
    children = [r for r in rows if r['parent_id'] is not None]
    result = []
    for p in parents:
        result.append({
            'id': p['id'],
            'name': p['name'],
            'slug': p['slug'],
            'children': [dict(c) for c in children if c['parent_id'] == p['id']]
        })
    return result
