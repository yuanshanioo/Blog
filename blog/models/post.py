from blog.db import query, execute


def get_posts(page=1, per_page=5, status='published', category_slug=None):
    """Get paginated posts with optional category filter."""
    conditions = ['p.status = ?']
    params = [status]

    if category_slug:
        conditions.append('(c.slug = ? OR c2.slug = ?)')
        params.extend([category_slug, category_slug])

    where = ' AND '.join(conditions)
    offset = (page - 1) * per_page

    total = query(
        f'SELECT COUNT(*) as count FROM posts p '
        f'LEFT JOIN categories c ON p.category_id = c.id '
        f'LEFT JOIN categories c2 ON c.parent_id = c2.id '
        f'WHERE {where}',
        params, one=True
    )['count']

    posts = query(
        f'SELECT p.*, c.name as category_name, c.slug as category_slug '
        f'FROM posts p '
        f'LEFT JOIN categories c ON p.category_id = c.id '
        f'LEFT JOIN categories c2 ON c.parent_id = c2.id '
        f'WHERE {where} '
        f'ORDER BY p.created_at DESC LIMIT ? OFFSET ?',
        params + [per_page, offset]
    )

    return posts, total


def get_post_by_slug(slug):
    return query(
        'SELECT p.*, c.name as category_name, c.slug as category_slug '
        'FROM posts p LEFT JOIN categories c ON p.category_id = c.id '
        'WHERE p.slug = ?', [slug], one=True
    )


def get_post_by_id(post_id):
    return query('SELECT * FROM posts WHERE id = ?', [post_id], one=True)


def create_post(title, slug, content, excerpt='', category_id=None, tags='',
                status='draft', cover_image='', is_markdown=1):
    return execute(
        'INSERT INTO posts (title, slug, content, excerpt, category_id, tags, status, cover_image, is_markdown) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        [title, slug, content, excerpt, category_id, tags, status, cover_image, is_markdown]
    )


def update_post(post_id, title, slug, content, excerpt='', category_id=None,
                tags='', status='draft', cover_image='', is_markdown=1):
    execute(
        'UPDATE posts SET title=?, slug=?, content=?, excerpt=?, category_id=?, '
        'tags=?, status=?, cover_image=?, is_markdown=?, updated_at=CURRENT_TIMESTAMP '
        'WHERE id=?',
        [title, slug, content, excerpt, category_id, tags, status, cover_image, is_markdown, post_id]
    )


def delete_post(post_id):
    execute('DELETE FROM posts WHERE id = ?', [post_id])


def increment_views(post_id):
    execute('UPDATE posts SET views = views + 1 WHERE id = ?', [post_id])


def search_posts(keyword, page=1, per_page=5):
    """Full-text search on posts."""
    conditions = ['p.status = ?', '(p.title LIKE ? OR p.content LIKE ? OR p.excerpt LIKE ?)']
    like = f'%{keyword}%'
    params = ['published', like, like, like]
    where = ' AND '.join(conditions)
    offset = (page - 1) * per_page

    total = query(
        f'SELECT COUNT(*) as count FROM posts p WHERE {where}', params, one=True
    )['count']

    posts = query(
        f'SELECT p.*, c.name as category_name, c.slug as category_slug '
        f'FROM posts p LEFT JOIN categories c ON p.category_id = c.id '
        f'WHERE {where} ORDER BY p.created_at DESC LIMIT ? OFFSET ?',
        params + [per_page, offset]
    )
    return posts, total


def get_archives():
    """Get posts grouped by year-month for archive page."""
    posts = query(
        "SELECT p.*, strftime('%Y', p.created_at) as year, "
        "strftime('%m', p.created_at) as month, "
        "c.name as category_name "
        'FROM posts p LEFT JOIN categories c ON p.category_id = c.id '
        "WHERE p.status = 'published' "
        'ORDER BY p.created_at DESC'
    )
    archives = {}
    for post in posts:
        key = f"{post['year']}年{post['month']}月"
        if key not in archives:
            archives[key] = []
        archives[key].append(post)
    return archives


def get_recent_posts(limit=5):
    return query(
        "SELECT p.*, c.name as category_name FROM posts p "
        "LEFT JOIN categories c ON p.category_id = c.id "
        "WHERE p.status = 'published' ORDER BY p.created_at DESC LIMIT ?",
        [limit]
    )


def get_popular_posts(limit=5):
    return query(
        "SELECT p.*, c.name as category_name FROM posts p "
        "LEFT JOIN categories c ON p.category_id = c.id "
        "WHERE p.status = 'published' ORDER BY p.views DESC LIMIT ?",
        [limit]
    )


def get_all_posts_admin(page=1, per_page=15, status=None, category_id=None):
    """Get all posts for admin with optional filters."""
    conditions = ['1=1']
    params = []

    if status:
        conditions.append('p.status = ?')
        params.append(status)
    if category_id:
        conditions.append('p.category_id = ?')
        params.append(category_id)

    where = ' AND '.join(conditions)
    offset = (page - 1) * per_page

    total = query(
        f'SELECT COUNT(*) as count FROM posts p WHERE {where}', params, one=True
    )['count']

    posts = query(
        f'SELECT p.*, c.name as category_name '
        f'FROM posts p LEFT JOIN categories c ON p.category_id = c.id '
        f'WHERE {where} ORDER BY p.created_at DESC LIMIT ? OFFSET ?',
        params + [per_page, offset]
    )
    return posts, total
