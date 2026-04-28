from blog.db import query, execute


def get_all_links(visible_only=True):
    if visible_only:
        return query('SELECT * FROM links WHERE is_visible = 1 ORDER BY sort_order')
    return query('SELECT * FROM links ORDER BY sort_order')


def get_link_by_id(link_id):
    return query('SELECT * FROM links WHERE id = ?', [link_id], one=True)


def create_link(name, url, description='', avatar='', sort_order=0, is_visible=1):
    return execute(
        'INSERT INTO links (name, url, description, avatar, sort_order, is_visible) VALUES (?, ?, ?, ?, ?, ?)',
        [name, url, description, avatar, sort_order, is_visible]
    )


def update_link(link_id, name, url, description='', avatar='', sort_order=0, is_visible=1):
    execute(
        'UPDATE links SET name=?, url=?, description=?, avatar=?, sort_order=?, is_visible=? WHERE id=?',
        [name, url, description, avatar, sort_order, is_visible, link_id]
    )


def delete_link(link_id):
    execute('DELETE FROM links WHERE id = ?', [link_id])
