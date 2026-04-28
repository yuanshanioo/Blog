from flask import Blueprint, render_template, request, abort, redirect, url_for, make_response, jsonify, send_from_directory, current_app
from blog.models.post import (get_posts, get_post_by_slug, get_archives,
                               search_posts, increment_views, get_recent_posts,
                               get_popular_posts)
from blog.models.category import get_category_by_slug, get_category_post_count
from blog.models.link import get_all_links
from blog.models.setting import get_all_settings
from blog.db import query

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    posts, total = get_posts(page=page, per_page=per_page)
    total_pages = (total + per_page - 1) // per_page
    return render_template('frontend/index.html',
                           posts=posts, page=page, total_pages=total_pages,
                           total=total)


@main_bp.route('/category/<slug>')
def category(slug):
    cat = get_category_by_slug(slug)
    if not cat:
        abort(404)
    page = request.args.get('page', 1, type=int)
    per_page = 5
    posts, total = get_posts(page=page, per_page=per_page, category_slug=slug)
    total_pages = (total + per_page - 1) // per_page
    return render_template('frontend/category.html',
                           posts=posts, category=cat,
                           page=page, total_pages=total_pages, total=total)


@main_bp.route('/archives')
def archives():
    archive_data = get_archives()
    return render_template('frontend/archive.html', archives=archive_data)


@main_bp.route('/about')
def about():
    return render_template('frontend/about.html')


@main_bp.route('/links')
def links():
    links_list = get_all_links(visible_only=True)
    return render_template('frontend/links.html', links=links_list)


@main_bp.route('/search')
def search():
    keyword = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    results = []
    total = 0
    total_pages = 0
    if keyword:
        results, total = search_posts(keyword, page=page)
        total_pages = (total + 5 - 1) // 5
    return render_template('frontend/search.html',
                           keyword=keyword, posts=results,
                           page=page, total_pages=total_pages, total=total)


@main_bp.route('/post/<slug>')
def post(slug):
    post_data = get_post_by_slug(slug)
    if not post_data:
        abort(404)
    increment_views(post_data['id'])
    recent = get_recent_posts(5)
    popular = get_popular_posts(5)

    # Extract table of contents from content
    from blog.utils.helpers import slugify
    toc = []
    content = post_data['content']
    for line in content.split('\n'):
        if line.startswith('## '):
            text = line[3:].strip()
            if text:
                toc.append({'level': 2, 'text': text, 'id': slugify(text)})
        elif line.startswith('### '):
            text = line[4:].strip()
            if text:
                toc.append({'level': 3, 'text': text, 'id': slugify(text)})

    # Estimate reading time (Chinese: ~300 chars/min, English: ~200 words/min)
    word_count = len(content.replace(' ', ''))
    read_time = max(1, round(word_count / 300))

    return render_template('frontend/post.html',
                           post=post_data, recent=recent, popular=popular,
                           toc=toc, read_time=read_time, word_count=word_count)


@main_bp.route('/api/search-suggestions')
def search_suggestions():
    q = request.args.get('q', '').strip()
    if not q or len(q) < 1:
        return jsonify({'suggestions': [], 'hot': []})
    suggestions = query(
        "SELECT title, slug FROM posts WHERE status='published' AND title LIKE ? LIMIT 8",
        [f'%{q}%']
    )
    return jsonify({'suggestions': [dict(s) for s in suggestions]})


@main_bp.route('/api/hot-searches')
def hot_searches():
    hot = get_popular_posts(5)
    return jsonify({'hot': [{'title': p['title'], 'slug': p['slug']} for p in hot]})


@main_bp.route('/media/<path:filename>')
def serve_upload(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@main_bp.route('/feed')
@main_bp.route('/rss')
def feed():
    posts, _ = get_posts(page=1, per_page=20)
    settings = get_all_settings()
    xml = render_template('feed.xml', posts=posts, settings=settings)
    response = make_response(xml)
    response.content_type = 'application/xml; charset=utf-8'
    return response
