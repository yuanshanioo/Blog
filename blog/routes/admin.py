import os
import random
import time
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from blog.middleware.auth import login_required
from blog.models.user import get_user_by_username, get_user_by_id, verify_password, create_user, update_user
from blog.models.post import (get_posts, get_post_by_id, create_post, update_post,
                               delete_post, get_all_posts_admin)
from blog.models.category import (get_all_categories, get_category_by_id,
                                   create_category, update_category, delete_category,
                                   get_category_post_count)
from blog.models.link import get_all_links, get_link_by_id, create_link, update_link, delete_link
from blog.models.setting import get_all_settings, update_settings
from blog.db import query, execute
from blog.utils.helpers import allowed_file

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    ip_address = request.remote_addr or 'unknown'

    def generate_captcha():
        op = random.choice(['+', '-'])
        if op == '+':
            a, b = random.randint(1, 50), random.randint(1, 50)
            answer = a + b
        else:
            a = random.randint(10, 99)
            b = random.randint(1, a)
            answer = a - b
        session['captcha_answer'] = str(answer)
        return f'{a} {op} {b} = ?'

    def render_login():
        return render_template('admin/login.html', captcha_text=generate_captcha())

    # Check IP ban (5 failed attempts in 15 minutes)
    recent_attempts = query(
        "SELECT COUNT(*) as c FROM login_attempts "
        "WHERE ip_address = %s AND attempt_time > (NOW() - INTERVAL 15 MINUTE)",
        [ip_address], one=True
    )['c']

    if recent_attempts >= 5:
        flash('登录尝试次数过多，请 15 分钟后再试', 'error')
        return render_login()

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        captcha_input = request.form.get('captcha', '').strip()

        # Verify CAPTCHA
        correct_answer = session.pop('captcha_answer', None)
        if not correct_answer or str(captcha_input) != str(correct_answer):
            flash('验证码错误', 'error')
            return render_login()

        user = get_user_by_username(username)
        if user and verify_password(password, user['password_hash']):
            # Clear failed attempts on success
            execute("DELETE FROM login_attempts WHERE ip_address = %s", [ip_address])
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['display_name'] = user['display_name']
            session['role'] = user['role']
            flash('登录成功', 'success')
            return redirect(url_for('admin.dashboard'))

        # Record failed attempt
        execute("INSERT INTO login_attempts (ip_address) VALUES (%s)", [ip_address])
        attempts_left = max(0, 4 - recent_attempts)
        if attempts_left > 0:
            flash(f'用户名或密码错误，还剩 {attempts_left} 次尝试机会', 'error')
        else:
            flash('登录尝试次数过多，请 15 分钟后再试', 'error')

    return render_login()


@admin_bp.route('/logout')
def logout():
    session.clear()
    flash('已退出登录', 'info')
    return redirect(url_for('admin.login'))


@admin_bp.route('/')
@login_required
def dashboard():
    total_posts = query("SELECT COUNT(*) as c FROM posts", one=True)['c']
    published = query("SELECT COUNT(*) as c FROM posts WHERE status='published'", one=True)['c']
    drafts = query("SELECT COUNT(*) as c FROM posts WHERE status='draft'", one=True)['c']
    total_views = query("SELECT COALESCE(SUM(views), 0) as c FROM posts", one=True)['c']
    total_cats = query("SELECT COUNT(*) as c FROM categories", one=True)['c']
    total_links = query("SELECT COUNT(*) as c FROM links", one=True)['c']

    recent_posts = query(
        "SELECT id, title, status, created_at FROM posts ORDER BY created_at DESC LIMIT 5"
    )

    from blog.models.setting import get_setting
    visitor_count = get_setting('site_visits', '0')
    return render_template('admin/dashboard.html',
                           total_posts=total_posts, published=published,
                           drafts=drafts, total_views=total_views,
                           total_cats=total_cats, total_links=total_links,
                           recent_posts=recent_posts, visitor_count=visitor_count)


# ===== Posts Management =====

@admin_bp.route('/posts')
@login_required
def posts():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    posts_list, total = get_all_posts_admin(page=page, status=status)
    total_pages = (total + 15 - 1) // 15
    categories = get_all_categories()
    return render_template('admin/posts.html',
                           posts=posts_list, page=page, total_pages=total_pages,
                           total=total, current_status=status, categories=categories)


@admin_bp.route('/posts/create', methods=['GET', 'POST'])
@login_required
def post_create():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip()
        content = request.form.get('content', '')
        excerpt = request.form.get('excerpt', '')
        category_id = request.form.get('category_id', type=int)
        tags = request.form.get('tags', '')
        status = request.form.get('status', 'draft')
        cover_image = request.form.get('cover_image', '')

        if not title:
            flash('请输入文章标题', 'error')
        else:
            if not slug:
                from blog.utils.helpers import generate_slug
                slug = generate_slug(title)
            post_id = create_post(title, slug, content, excerpt, category_id, tags, status, cover_image)
            flash('文章创建成功', 'success')
            return redirect(url_for('admin.posts'))
    categories = get_all_categories()
    return render_template('admin/post_edit.html', post=None, categories=categories)


@admin_bp.route('/posts/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def post_edit(post_id):
    post_data = get_post_by_id(post_id)
    if not post_data:
        flash('文章不存在', 'error')
        return redirect(url_for('admin.posts'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip()
        content = request.form.get('content', '')
        excerpt = request.form.get('excerpt', '')
        category_id = request.form.get('category_id', type=int)
        tags = request.form.get('tags', '')
        status = request.form.get('status', 'draft')
        cover_image = request.form.get('cover_image', '')

        if not title:
            flash('请输入文章标题', 'error')
        else:
            update_post(post_id, title, slug, content, excerpt, category_id, tags, status, cover_image)
            flash('文章更新成功', 'success')
            return redirect(url_for('admin.posts'))

    categories = get_all_categories()
    return render_template('admin/post_edit.html', post=dict(post_data), categories=categories)


@admin_bp.route('/posts/delete/<int:post_id>', methods=['POST'])
@login_required
def post_delete(post_id):
    delete_post(post_id)
    flash('文章已删除', 'success')
    return redirect(url_for('admin.posts'))


# ===== Categories Management =====

@admin_bp.route('/categories')
@login_required
def categories():
    cats = get_all_categories()
    return render_template('admin/categories.html', categories=cats)


@admin_bp.route('/categories/create', methods=['POST'])
@login_required
def category_create():
    name = request.form.get('name', '').strip()
    slug = request.form.get('slug', '').strip()
    description = request.form.get('description', '')
    parent_id = request.form.get('parent_id', type=int)

    if not name or not slug:
        flash('分类名称和别名不能为空', 'error')
    else:
        create_category(name, slug, description, parent_id)
        flash('分类创建成功', 'success')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/categories/edit/<int:cat_id>', methods=['POST'])
@login_required
def category_edit(cat_id):
    name = request.form.get('name', '').strip()
    slug = request.form.get('slug', '').strip()
    description = request.form.get('description', '')
    parent_id = request.form.get('parent_id', type=int)

    if not name or not slug:
        flash('分类名称和别名不能为空', 'error')
    else:
        update_category(cat_id, name, slug, description, parent_id)
        flash('分类更新成功', 'success')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/categories/delete/<int:cat_id>', methods=['POST'])
@login_required
def category_delete(cat_id):
    delete_category(cat_id)
    flash('分类已删除', 'success')
    return redirect(url_for('admin.categories'))


# ===== Links Management =====

@admin_bp.route('/links')
@login_required
def links():
    links_list = get_all_links(visible_only=False)
    return render_template('admin/links.html', links=links_list)


@admin_bp.route('/links/create', methods=['POST'])
@login_required
def link_create():
    name = request.form.get('name', '').strip()
    url = request.form.get('url', '').strip()
    description = request.form.get('description', '')
    is_visible = request.form.get('is_visible', type=int, default=1)

    if not name or not url:
        flash('链接名称和地址不能为空', 'error')
    else:
        create_link(name, url, description, '', 0, is_visible)
        flash('链接创建成功', 'success')
    return redirect(url_for('admin.links'))


@admin_bp.route('/links/edit/<int:link_id>', methods=['POST'])
@login_required
def link_edit(link_id):
    name = request.form.get('name', '').strip()
    url = request.form.get('url', '').strip()
    description = request.form.get('description', '')
    is_visible = request.form.get('is_visible', type=int, default=1)

    if not name or not url:
        flash('链接名称和地址不能为空', 'error')
    else:
        update_link(link_id, name, url, description, '', 0, is_visible)
        flash('链接更新成功', 'success')
    return redirect(url_for('admin.links'))


@admin_bp.route('/links/delete/<int:link_id>', methods=['POST'])
@login_required
def link_delete(link_id):
    delete_link(link_id)
    flash('链接已删除', 'success')
    return redirect(url_for('admin.links'))


# ===== Settings =====

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        site_settings = {
            'site_title': request.form.get('site_title', ''),
            'site_subtitle': request.form.get('site_subtitle', ''),
            'site_description': request.form.get('site_description', ''),
            'site_keywords': request.form.get('site_keywords', ''),
            'posts_per_page': request.form.get('posts_per_page', '5'),
            'icp_beian': request.form.get('icp_beian', ''),
            'footer_copyright': request.form.get('footer_copyright', ''),
        }
        update_settings(site_settings)
        flash('设置已保存', 'success')
        return redirect(url_for('admin.settings'))

    current_settings = get_all_settings()
    return render_template('admin/settings.html', settings=current_settings)


# ===== Profile =====

@admin_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = get_user_by_id(session['user_id'])
    if request.method == 'POST':
        display_name = request.form.get('display_name', '')
        email = request.form.get('email', '')
        bio = request.form.get('bio', '')
        update_user(session['user_id'], display_name=display_name, email=email, bio=bio)
        session['display_name'] = display_name
        flash('个人资料已更新', 'success')
        return redirect(url_for('admin.profile'))
    return render_template('admin/profile.html', user=user)


@admin_bp.route('/upload', methods=['POST'])
@login_required
def upload_image():
    file = request.files.get('file')
    if not file or file.filename == '':
        return jsonify({'error': '未选择文件'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件类型'}), 400

    ext = os.path.splitext(file.filename)[1].lower() or '.png'
    unique_name = f"{uuid.uuid4().hex}{ext}"
    data = file.read()
    mime_type = file.content_type or 'application/octet-stream'
    user_id = session.get('user_id')

    insert_id = execute(
        "INSERT INTO uploads (filename, original_name, mime_type, size, path, data, uploader_id) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (unique_name, file.filename, mime_type, len(data), f'/media/{unique_name}', data, user_id)
    )

    return jsonify({'url': f'/media/{insert_id}', 'filename': str(insert_id)})
