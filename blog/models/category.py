from blog.db import query, execute


def get_all_categories():
    """Get all categories ordered hierarchically."""
    return query(
        'SELECT c1.*, c2.name as parent_name '
        'FROM categories c1 '
        'LEFT JOIN categories c2 ON c1.parent_id = c2.id '
        'ORDER BY c1.parent_id IS NULL, c1.parent_id, c1.sort_order'
    )


def get_category_by_slug(slug):
    return query('SELECT * FROM categories WHERE slug = %s', [slug], one=True)


def get_category_by_id(cat_id):
    return query('SELECT * FROM categories WHERE id = %s', [cat_id], one=True)


def get_child_categories(parent_id):
    return query('SELECT * FROM categories WHERE parent_id = %s ORDER BY sort_order', [parent_id])


def create_category(name, slug, description='', parent_id=None, sort_order=0):
    return execute(
        'INSERT INTO categories (name, slug, description, parent_id, sort_order) VALUES (%s, %s, %s, %s, %s)',
        [name, slug, description, parent_id, sort_order]
    )


def update_category(cat_id, name, slug, description='', parent_id=None, sort_order=0):
    execute(
        'UPDATE categories SET name=%s, slug=%s, description=%s, parent_id=%s, sort_order=%s WHERE id=%s',
        [name, slug, description, parent_id, sort_order, cat_id]
    )


def delete_category(cat_id):
    execute('DELETE FROM categories WHERE id = %s', [cat_id])


def get_category_post_count(cat_id=None):
    """Get post count per category, optionally for a specific category."""
    if cat_id:
        return query(
            "SELECT COUNT(*) as count FROM posts WHERE category_id = %s AND status = 'published'",
            [cat_id], one=True
        )['count']
    categories = query(
        "SELECT c.id, c.name, c.slug, COUNT(p.id) as post_count "
        "FROM categories c LEFT JOIN posts p ON c.id = p.category_id AND p.status = 'published' "
        "GROUP BY c.id ORDER BY c.sort_order"
    )
    return categories
