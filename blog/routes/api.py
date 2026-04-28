from flask import Blueprint, jsonify, request, session
from blog.db import query
from blog.models.post import get_posts, get_post_by_slug, increment_views

api_bp = Blueprint('api', __name__)


@api_bp.route('/posts')
def api_posts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category = request.args.get('category')
    posts, total = get_posts(page=page, per_page=per_page, category_slug=category)
    return jsonify({
        'posts': [dict(p) for p in posts],
        'total': total,
        'page': page,
        'per_page': per_page
    })


@api_bp.route('/posts/<slug>')
def api_post(slug):
    post = get_post_by_slug(slug)
    if not post:
        return jsonify({'error': 'not found'}), 404
    increment_views(post['id'])
    return jsonify(dict(post))


@api_bp.route('/categories')
def api_categories():
    rows = query('SELECT * FROM categories ORDER BY sort_order')
    return jsonify([dict(r) for r in rows])


@api_bp.route('/settings')
def api_settings():
    from blog.models.setting import get_all_settings
    return jsonify(get_all_settings())


@api_bp.route('/links')
def api_links():
    links = query('SELECT * FROM links WHERE is_visible = 1 ORDER BY sort_order')
    return jsonify([dict(l) for l in links])


@api_bp.route('/stats')
def api_stats():
    total_posts = query("SELECT COUNT(*) as c FROM posts", one=True)['c']
    total_views = query("SELECT COALESCE(SUM(views), 0) as c FROM posts", one=True)['c']
    total_cats = query("SELECT COUNT(*) as c FROM categories", one=True)['c']
    return jsonify({
        'posts': total_posts,
        'views': total_views,
        'categories': total_cats
    })


@api_bp.route('/check-auth')
def check_auth():
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': session['user_id'],
                'username': session.get('username'),
                'display_name': session.get('display_name'),
                'role': session.get('role')
            }
        })
    return jsonify({'authenticated': False}), 401
