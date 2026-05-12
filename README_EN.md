# Distant Mountain (远山)

> Personal Blog System — Built with Flask + MySQL

**[中文](README.md)**

远山 is a full-featured personal blog built with Python Flask, supporting Markdown writing, multi-theme switching, admin management, RSS feeds, and more. Designed for running a lightweight blog on your own server.

## Features

**Writing & Display**
- Markdown article editing with code blocks, images, blockquotes
- Article cover images with responsive card layout
- Table of Contents (TOC) with scroll-spy highlighting
- Estimated reading time and reading progress tracking
- RSS feed output (`/feed`, `/rss`)

**Reading Experience**
- Four themes: Light, Dark, Sunset, Auto (follows system)
- Four fonts: System Default, Serif, Kai, Song
- Font size slider with real-time preview

**Search & Navigation**
- Real-time search suggestions
- Search history (localStorage)
- Popular posts recommendations
- Browse by category and archive date

**Admin Panel**
- Dashboard with post count, views, visitor stats
- Post management (CRUD)
- Category management (with sub-categories)
- Friend links management
- System settings (title, description, SEO keywords, ICP, etc.)
- Profile editing

**Security**
- Arithmetic CAPTCHA on login
- IP-based login lockout (5 failures in 15 minutes)

## Quick Start

### Requirements

- Python 3.8+
- pip
- MySQL 5.7+ / 8.0+

### Installation

```bash
# Clone the project
git clone <repo-url> && cd Blog

# Install dependencies
pip install -r requirements.txt

# Create MySQL database
mysql -u root -p -e "CREATE DATABASE blog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Configure database connection
export MYSQL_HOST=127.0.0.1
export MYSQL_PORT=3306
export MYSQL_USER=blog
export MYSQL_PASSWORD=your_password
export MYSQL_DATABASE=blog

# Initialize database and seed sample data
python seed.py

# Start (development mode)
python app.py
```

Visit http://127.0.0.1:5000

Default admin: `admin` / `admin123`

### LAN Access

```bash
# app.py listens on 0.0.0.0 by default
app.run(host='0.0.0.0', port=5000, debug=True)
```

Other devices access via `http://<your-LAN-IP>:5000`.

> Note: Flask dev server is for trusted networks only. Use Gunicorn / Waitress for production.

## Project Structure

```
Blog/
├── app.py                   # Entry point
├── config.py                # Configuration
├── requirements.txt         # Python dependencies
├── seed.py                  # Database seeder
├── DEVELOPMENT.md           # Development guide & changelog
├── blog/
│   ├── __init__.py          # Flask app factory
│   ├── db.py                # MySQL wrapper (PyMySQL)
│   ├── models/              # Data models
│   │   ├── post.py          #   Posts
│   │   ├── category.py      #   Categories
│   │   ├── link.py          #   Friend links
│   │   ├── user.py          #   Users
│   │   └── setting.py       #   Settings (with cache)
│   ├── routes/              # Route handlers
│   │   ├── main.py          #   Frontend pages + SEO endpoints
│   │   ├── admin.py         #   Admin management
│   │   └── api.py           #   JSON API
│   ├── middleware/
│   │   └── auth.py          # Login/admin decorators
│   └── utils/
│       └── helpers.py       # Utility functions
├── templates/               # Jinja2 templates
│   ├── base.html            #   Master layout
│   ├── macros/              #   Reusable components
│   │   ├── post_card.html   #     Post card
│   │   └── pagination.html  #     Pagination
│   ├── frontend/            #   Frontend pages
│   ├── admin/               #   Admin pages
│   ├── feed.xml             #   RSS template
│   ├── robots.txt           #   Robots template
│   └── sitemap.xml          #   Sitemap template
├── static/                  # Static assets
│   ├── css/
│   │   ├── style.css        #   Frontend styles (CSS custom properties)
│   │   └── admin.css        #   Admin styles
│   ├── js/
│   │   ├── main.js          #   Frontend JavaScript
│   │   └── admin.js         #   Admin JavaScript
│   └── uploads/             #   User uploads
└── database/
    └── schema.sql           # Database schema (MySQL)
```

## Configuration

| Setting | Description | Default |
|---------|-------------|---------|
| `SECRET_KEY` | Session encryption key | `blog-dev-key-...` |
| `MYSQL_HOST` | MySQL host | `127.0.0.1` |
| `MYSQL_PORT` | MySQL port | `3306` |
| `MYSQL_USER` | MySQL user | `blog` |
| `MYSQL_PASSWORD` | MySQL password | (empty) |
| `MYSQL_DATABASE` | MySQL database name | `blog` |
| `MYSQL_CHARSET` | MySQL charset | `utf8mb4` |
| `UPLOAD_FOLDER` | Upload directory | `static/uploads` |
| `ALLOWED_EXTENSIONS` | Allowed upload types | Image formats |
| `MAX_CONTENT_LENGTH` | Upload size limit | 16MB |
| `ITEMS_PER_PAGE` | Posts per page | 5 |

Production: set `SECRET_KEY` via environment variable with a strong random string.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask 3.1 |
| Template | Jinja2 3.1 |
| Database | MySQL + PyMySQL |
| Frontend | Vanilla JavaScript |
| Styling | CSS Custom Properties (theming) |
| Auth | PBKDF2-SHA256 + Session |
| Deployment | Gunicorn / Waitress |

## Screenshots

Homepage card layout — article cover images with title, category, and date centered overlay, responsive design.

## License

MIT
