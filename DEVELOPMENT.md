# 远山 开发文档

> 本文档面向开发者，涵盖架构说明、开发环境搭建、编码规范、部署指南和变更日志。

---

## 1. 架构概览

### 1.1 应用工厂

`app.py` 是入口文件，调用 `create_app(config_name)` 创建 Flask 应用。工厂函数位于 `blog/__init__.py`，职责包括：

- 加载配置（`DevelopmentConfig` / `ProductionConfig`）
- 初始化数据库连接（`blog/db.py`）
- 注册三个 Blueprint
- 注册模板过滤器（`rssdate`、`datecn`、`slugify`）
- 设置错误处理器（404、500）
- 注入全局上下文（站点设置、导航分类、访客数）

### 1.2 Blueprint 路由

| Blueprint | 模块 | URL 前缀 | 用途 |
|-----------|------|---------|------|
| `main_bp` | `blog/routes/main.py` | `/` | 前台页面、RSS、robots.txt、sitemap |
| `admin_bp` | `blog/routes/admin.py` | `/admin` | 后台管理面板 |
| `api_bp` | `blog/routes/api.py` | `/api` | JSON 接口（文章、分类、设置、统计） |

### 1.3 数据库层 (`blog/db.py`)

使用 PyMySQL + DictCursor，所有查询结果返回字典。

核心函数：
- `init_db(app)` — 启动时读取并执行 `database/schema.sql`
- `query(sql, params, one=False)` — 查询，`one=True` 返回单条
- `execute(sql, params)` — 执行写操作，返回 `lastrowid`
- `get_db()` — 从 Flask `g` 获取连接，`teardown_appcontext` 自动关闭
- `format_row_dates()` — 将 `datetime`/`date` 对象转为字符串
- `split_sql_statements()` — 分割多条 SQL 语句

### 1.4 模型层 (`blog/models/`)

无状态函数模块，不使用 ORM，直接调用 `query()`/`execute()`：

| 模块 | 功能 |
|------|------|
| `post.py` | 文章 CRUD、搜索、分页、归档、热门/最新/相关/上下篇查询 |
| `category.py` | 分类管理（支持二级分类 `parent_id`）、文章计数 |
| `link.py` | 友情链接，支持可见性切换 |
| `user.py` | 用户管理，PBKDF2-SHA256 密码哈希 |
| `setting.py` | 键值对设置，带内存缓存（60 秒 TTL，写入时自动失效） |

### 1.5 中间件 (`blog/middleware/auth.py`)

- `login_required` — 检查 session 中的 `user_id`，未登录则重定向
- `admin_required` — 额外检查 `role == 'admin'`

### 1.6 模板层 (`templates/`)

```
templates/
  base.html              # 基础布局（header、nav、footer、主题/设置 JS）
  macros/
    post_card.html        # 可复用文章卡片宏
    pagination.html       # 可复用分页宏
  frontend/               # 前台页面
    index.html            #   首页（文章列表）
    post.html             #   文章详情（TOC、阅读进度、上下篇、相关推荐）
    category.html         #   分类列表
    search.html           #   搜索（建议、历史、热门）
    archive.html          #   归档
    about.html            #   关于
    links.html            #   友情链接
    404.html / 500.html   #   错误页
  admin/                  # 后台页面（login、dashboard、posts、categories 等）
  feed.xml                # RSS 模板
  robots.txt              # 搜索引擎爬虫规则
  sitemap.xml             # 站点地图
```

模板 Block 命名约定：
- `title` / `description` / `keywords` — SEO meta
- `canonical` — 规范链接
- `og_meta` / `twitter_title` / `twitter_description` — 社交分享
- `nav_home` / `nav_archive` / `nav_about` / `nav_links` — 导航高亮
- `content` — 主内容区
- `extra_head` / `extra_scripts` — 页面级扩展

### 1.7 静态资源

- `static/css/style.css` — CSS 自定义属性主题系统
- `static/js/main.js` — 原生 JS（主题、设置、搜索、移动端菜单、图片懒加载）
- `static/uploads/` — 用户上传文件

### 1.8 Markdown 渲染

在 `templates/frontend/post.html` 中通过 Jinja2 内联解析，支持：
- `##` / `###` 标题（自动生成 slugify ID 用于 TOC 锚点）
- 围栏代码块（带语言标识）
- 引用块、列表、加粗文本
- 图片（自动添加 `loading="lazy"`）
- 不依赖外部 Markdown 库

### 1.9 模板过滤器

在 `blog/__init__.py` 中注册：
- `rssdate` — RSS 日期格式（RFC 822）
- `datecn` — 中文日期格式（YYYY年MM月DD日）
- `slugify` — URL 安全别名生成

---

## 2. 开发环境搭建

### 2.1 前置条件

- Python 3.8+
- pip
- MySQL 5.7+ / 8.0+

### 2.2 安装

```bash
git clone <repo-url> && cd Blog
pip install -r requirements.txt
```

### 2.3 数据库

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE blog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 设置环境变量
export MYSQL_HOST=127.0.0.1
export MYSQL_PORT=3306
export MYSQL_USER=blog
export MYSQL_PASSWORD=your_password
export MYSQL_DATABASE=blog

# 初始化数据（管理员、分类、示例文章、友链）
python seed.py
```

### 2.4 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `FLASK_ENV` | 运行环境 | `development` |
| `SECRET_KEY` | 会话密钥 | `blog-dev-key-change-in-production` |
| `MYSQL_HOST` | MySQL 主机 | `127.0.0.1` |
| `MYSQL_PORT` | MySQL 端口 | `3306` |
| `MYSQL_USER` | MySQL 用户 | `blog` |
| `MYSQL_PASSWORD` | MySQL 密码 | 空 |
| `MYSQL_DATABASE` | 数据库名 | `blog` |
| `MYSQL_CHARSET` | 字符集 | `utf8mb4` |

### 2.5 启动

```bash
python app.py
# 访问 http://127.0.0.1:5000
# 默认管理员：admin / admin123
```

局域网访问：`app.py` 默认监听 `0.0.0.0:5000`，其他设备通过 `http://<局域网IP>:5000` 访问。

---

## 3. 编码规范

### 3.1 Python

- **无 ORM**：使用原始 SQL + 参数化查询，占位符统一使用 `%s`
- **模型为函数模块**：不使用类，每个模块导出独立函数
- **DictCursor**：所有查询结果为字典，便于模板直接访问属性
- **日期格式化**：`format_row_dates()` 在 `db.py` 中统一处理

### 3.2 模板

- **宏复用**：可复用组件抽取到 `templates/macros/`（如 `post_card.html`、`pagination.html`）
- **继承链**：`base.html` → `frontend/*.html`，通过 block 覆盖
- **上下文注入**：`inject_globals()` 提供 `settings`、`nav_categories`、`current_year`、`visitor_count`

### 3.3 CSS

- **主题系统**：通过 `[data-theme]` 属性 + CSS 自定义属性实现（light / dark / sunset / auto）
- **字体模式**：`[data-font]` 属性切换 sans / serif / kai / song
- **字号缩放**：`[data-size]` 属性 + `--font-scale` 变量
- **响应式断点**：1024px（TOC 隐藏）、820px（间距调整）、640px（移动端导航）、380px（单列）

### 3.4 JavaScript

- **原生 JS**，无框架或构建工具
- **IIFE + strict mode**，避免全局污染
- **localStorage** 持久化主题、字号、字体、搜索历史
- **防抖搜索建议**（300ms 延迟）

---

## 4. 部署指南

### 4.1 生产配置

```bash
export FLASK_ENV=production
export SECRET_KEY=$(openssl rand -hex 32)
export MYSQL_HOST=your-db-host
export MYSQL_USER=blog
export MYSQL_PASSWORD=your-password
export MYSQL_DATABASE=blog
```

### 4.2 WSGI 服务器

**Linux / macOS — Gunicorn：**

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app('production')"
```

**Windows — Waitress：**

```bash
pip install waitress
waitress-serve --port=8000 "app:create_app('production')"
```

### 4.3 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /path/to/Blog/static/;
        expires 30d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4.4 数据库

- `schema.sql` 在应用启动时自动执行（`init_db()`），无需手动建表
- 首次部署运行 `python seed.py` 填充初始数据
- 生产环境建议创建专用 MySQL 用户并限制权限

### 4.5 文件上传

- 确保 `static/uploads/` 目录可写
- 上传大小限制 16MB（`MAX_CONTENT_LENGTH`）
- 允许格式：png、jpg、jpeg、gif、webp、svg、ico

---

## 5. 变更日志

### v0.4 — 系统性改进（2026-05-12）

#### 5.1 宏提取
- 新建 `templates/macros/post_card.html` — 可复用文章卡片（封面图、叠加层、元信息）
- 新建 `templates/macros/pagination.html` — 可复用分页（省略号、ARIA 标签）
- 重构 `index.html`、`category.html`、`search.html` 使用宏，消除 3 处重复代码

#### 5.2 SEO 改进
- 新建 `templates/robots.txt` — 允许公开页面，禁止 /admin/ 和 /api/
- 新建 `templates/sitemap.xml` — 动态站点地图（文章、分类、静态页）
- 所有前台页面添加 `<link rel="canonical">`
- 添加 Open Graph meta 标签（og:type、og:title、og:description、og:image、og:url）
- 添加 Twitter Card meta 标签
- 文章页添加 `article:published_time`、`article:modified_time`、`article:section`、`article:tag`
- `base.html` head 中添加 RSS 订阅链接

#### 5.3 文章导航
- `post.py` 新增 `get_prev_next_posts()` — 按 ID 获取上下篇
- `post.py` 新增 `get_related_posts()` — 按分类获取相关文章，不足时用热门文章补充
- `post.html` 新增上下篇导航栏
- `post.html` 新增相关文章网格

#### 5.4 阅读体验
- 文章页 TOC 侧边栏（从 Markdown h2/h3 提取）
- Scroll-spy JS 自动高亮当前章节
- 阅读进度条
- 阅读时间估算（中文 ~300 字/分钟）
- 已读时间追踪器

#### 5.5 性能优化
- `setting.py` 新增内存缓存（60 秒 TTL，写入时自动失效）
- `__init__.py` 中 `current_year` 从硬编码 `2026` 改为 `datetime.now().year`

#### 5.6 可访问性
- 所有导航、搜索、设置、分页、TOC 添加 `aria-label`
- 主题/字体按钮添加 `role="radiogroup"` + `role="radio"` + `aria-checked`
- 分页当前页添加 `aria-current="page"`
- 下拉触发器添加 `aria-haspopup` + `aria-expanded`
- 添加 `:focus-visible` 键盘导航轮廓样式
- 移动端菜单过渡动画从 `max-height` 改为 `opacity + transform`

#### 5.7 死代码清理
- 删除 `helpers.py` 中未使用的 `save_upload()`、`truncate_html()`、`strip_html()`、`format_date()`
- 删除未使用的 `hashlib`、`uuid` 导入
- 移除 `admin.py` 中未使用的 `admin_required` 导入

#### 5.8 搜索体验
- 搜索建议支持键盘方向键导航（上/下/Enter）
- localStorage 保存最近 5 条搜索历史
- 输入为空时显示热门文章
- 搜索 API 防抖（300ms）

#### 5.9 数据库迁移（SQLite → MySQL）
- `db.py` 从 sqlite3 重写为 pymysql
- 所有模型 SQL 占位符从 `?` 改为 `%s`
- SQLite `strftime()` 改为 MySQL `DATE_FORMAT()`
- 新增 `split_sql_statements()` 处理多语句执行
- 新增 `format_row_dates()` 统一日期格式化
- `schema.sql` 更新为 MySQL 语法（ENGINE=InnoDB、utf8mb4、AUTO_INCREMENT）

#### 5.10 模板重构
- `category.html`、`index.html`、`search.html` 简化为使用宏
- 移除列表页中的内联文章卡片 HTML
- 添加空状态组件

---

### v0.3 — 代码重构（2026-05-10）

- 删除无用代码，重构项目结构

### v0.2 — Bug 修复

- 修复已知问题

### v0.1 — 项目介绍

- 初始项目介绍文档

### v0.0 — 首次提交

- 项目初始化
