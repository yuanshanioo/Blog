# 远山

> 个人博客系统 · 基于 Flask + MySQL

**[English](README_EN.md)**

远山是一个功能完整的个人博客，采用 Python Flask 框架开发，支持 Markdown 写作、多主题切换、后台管理、RSS 订阅等特性，适合个人搭建轻量级博客站点。

## 功能

**写作与展示**
- Markdown 文章编辑，支持代码块、图片、引用等语法
- 文章封面图展示，响应式卡片布局
- 文章目录（TOC）锚点导航，自动高亮当前章节
- 自动估算阅读时长，记录已读进度
- RSS 订阅输出（/feed、/rss）

**阅读体验**
- 四套主题：白天、夜间、日落、自动跟随系统
- 四种字体：系统默认、衬线、楷体、宋体
- 字号滑块调节，实时生效

**搜索与导航**
- 搜索关键词即时建议
- 历史搜索记录（localStorage）
- 热门文章推荐
- 文章按分类、归档时间浏览

**后台管理**
- 控制台仪表盘：文章数、阅读量、访客统计
- 文章发布与管理（增删改）
- 分类管理（支持二级分类）
- 友链管理
- 系统设置（站点标题、描述、SEO 关键词、ICP 备案号等）
- 个人资料编辑

**安全与防护**
- 算术验证码登录
- IP 登录失败锁定（连续 5 次失败后封禁 15 分钟）

## 快速开始

### 环境要求

- Python 3.8+
- pip
- MySQL 5.7+ / 8.0+

### 安装

```bash
# 克隆项目
git clone <repo-url> && cd Blog

# 安装依赖
pip install -r requirements.txt

# 创建 MySQL 数据库
mysql -u root -p -e "CREATE DATABASE blog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 配置数据库连接
export MYSQL_HOST=127.0.0.1
export MYSQL_PORT=3306
export MYSQL_USER=blog
export MYSQL_PASSWORD=your_password
export MYSQL_DATABASE=blog

# 初始化数据库并填充示例数据
python seed.py

# 启动（开发模式）
python app.py
```

访问 http://127.0.0.1:5000

默认管理员账号：`admin` / `admin123`

### 局域网访问

```bash
# app.py 中使用 0.0.0.0 监听所有网卡
app.run(host='0.0.0.0', port=5000, debug=True)
```

其他设备通过 `http://<本机局域网IP>:5000` 访问。

> 注意：Flask 开发服务器仅建议在可信网络中使用。生产环境请使用 Gunicorn / Waitress 等 WSGI 服务器。

## 项目结构

```
Blog/
├── app.py                   # 应用入口
├── config.py                # 配置文件
├── requirements.txt         # Python 依赖
├── seed.py                  # 示例数据填充
├── DEVELOPMENT.md           # 开发文档与变更日志
├── blog/
│   ├── __init__.py          # Flask 应用工厂
│   ├── db.py                # MySQL 封装
│   ├── models/              # 数据模型层
│   │   ├── post.py          #   文章
│   │   ├── category.py      #   分类
│   │   ├── link.py          #   友链
│   │   ├── user.py          #   用户
│   │   └── setting.py       #   设置（带缓存）
│   ├── routes/              # 路由层
│   │   ├── main.py          #   前台页面 + SEO 端点
│   │   ├── admin.py         #   后台管理
│   │   └── api.py           #   JSON 接口
│   ├── middleware/
│   │   └── auth.py          # 登录鉴权装饰器
│   └── utils/
│       └── helpers.py       # 工具函数
├── templates/               # Jinja2 模板
│   ├── base.html            #   基础布局
│   ├── macros/              #   可复用组件
│   │   ├── post_card.html   #     文章卡片
│   │   └── pagination.html  #     分页
│   ├── frontend/            #   前台页面
│   ├── admin/               #   后台页面
│   ├── feed.xml             #   RSS 模板
│   ├── robots.txt           #   爬虫规则
│   └── sitemap.xml          #   站点地图
├── static/                  # 静态资源
│   ├── css/
│   │   ├── style.css        #   前台样式（CSS 自定义属性）
│   │   └── admin.css        #   后台样式
│   ├── js/
│   │   ├── main.js          #   前台脚本
│   │   └── admin.js         #   后台脚本
│   └── uploads/             #   上传文件
└── database/
    └── schema.sql           # 数据库建表语句（MySQL）
```

## 配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `SECRET_KEY` | 会话加密密钥 | `blog-dev-key-...` |
| `MYSQL_HOST` | MySQL 主机 | `127.0.0.1` |
| `MYSQL_PORT` | MySQL 端口 | `3306` |
| `MYSQL_USER` | MySQL 用户 | `blog` |
| `MYSQL_PASSWORD` | MySQL 密码 | 空 |
| `MYSQL_DATABASE` | MySQL 数据库名 | `blog` |
| `MYSQL_CHARSET` | MySQL 字符集 | `utf8mb4` |
| `UPLOAD_FOLDER` | 文件上传目录 | `static/uploads` |
| `ALLOWED_EXTENSIONS` | 允许上传的后缀 | 图片格式 |
| `MAX_CONTENT_LENGTH` | 上传大小上限 | 16MB |
| `ITEMS_PER_PAGE` | 每页文章数 | 5 |

生产环境应将 `SECRET_KEY` 改为随机字符串，并通过环境变量 `SECRET_KEY` 传入。

## 技术栈

| 层面 | 技术 |
|------|------|
| 后端框架 | Flask 3.1 |
| 模板引擎 | Jinja2 3.1 |
| 数据库 | MySQL + PyMySQL |
| 前端 | 原生 JavaScript |
| 样式 | CSS 自定义属性（主题变量） |
| 认证 | PBKDF2-SHA256 + Session |
| 部署 | Gunicorn / Waitress |

## 截图

首页卡片列表 — 文章封面图配标题、分类、日期居中覆盖展示，支持响应式布局。

## License

MIT
