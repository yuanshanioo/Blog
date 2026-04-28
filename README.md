# 远山 — 个人博客系统

基于 Flask + SQLite 的个人博客，支持 Markdown 编写、多主题模式、文章管理、访客统计等功能。

## 功能特性

- **Markdown 文章编辑** — 自定义 Markdown 解析器，支持代码块高亮、图片上传
- **封面卡片布局** — 文章以卡片形式展示，封面图为背景，标题与元信息居中覆盖
- **多主题模式** — 支持 白天/夜间/日落/自动 四种主题，可无缝切换
- **字体切换** — 系统默认 / 衬线 / 楷体 / 宋体 四种字体
- **字体缩放** — 滑块调节阅读字号
- **搜索建议** — 输入关键词即时搜索，显示历史搜索与热门文章
- **文章目录 TOC** — 文章页左侧显示锚点目录，随滚动高亮
- **阅读时长** — 自动估算文章阅读时间，记录已读时长
- **RSS 订阅** — 支持 `/feed` 和 `/rss` 输出标准 RSS 2.0
- **访客统计** — 底部显示站点访客总数
- **后台管理** — 文章/分类/友链/系统设置管理
- **登录安全** — 算术验证码 + IP 登录失败锁定（5 次/15 分钟）
- **响应式设计** — 适配桌面与移动端

## 快速开始

### 环境要求

- Python 3.8+
- pip

### 安装

```bash
# 克隆项目
git clone <repo-url> && cd Blog

# 安装依赖
pip install -r requirements.txt

# 初始化数据库并填充示例数据
python seed.py

# 启动
python app.py
```

访问 `http://127.0.0.1:5000/`

默认管理员账号：`admin` / `admin123`

### 项目结构

```
Blog/
├── app.py                 # 应用入口
├── config.py              # 配置（数据库路径、上传目录等）
├── requirements.txt       # Python 依赖
├── seed.py                # 示例数据填充脚本
├── blog/
│   ├── __init__.py        # Flask 应用工厂，注册过滤器、蓝图
│   ├── db.py              # SQLite 数据库连接与查询封装
│   ├── models/            # 数据模型
│   │   ├── post.py        # 文章 CRUD
│   │   ├── category.py    # 分类 CRUD
│   │   ├── link.py        # 友链 CRUD
│   │   ├── user.py        # 用户认证
│   │   └── setting.py     # 系统设置
│   ├── routes/            # 路由
│   │   ├── main.py        # 前台（首页、文章、归档、搜索、RSS）
│   │   ├── admin.py       # 后台（管理、上传、验证码）
│   │   └── api.py         # API（评论等）
│   ├── middleware/
│   │   └── auth.py        # 登录鉴权装饰器
│   └── utils/
│       └── helpers.py     # 工具函数
├── templates/
│   ├── base.html          # 基础布局（页头/导航/页脚）
│   ├── feed.xml           # RSS 模板
│   ├── frontend/          # 前台模板
│   └── admin/             # 后台模板
├── static/
│   ├── css/
│   │   ├── style.css      # 前台样式（含多主题变量）
│   │   └── admin.css      # 后台样式
│   ├── js/
│   │   ├── main.js        # 前台交互
│   │   └── admin.js       # 后台交互
│   └── uploads/           # 上传文件目录
└── database/
    └── schema.sql         # 数据库表结构
```

## 配置说明

编辑 `config.py`：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `SECRET_KEY` | 会话密钥 | `blog-dev-key-...` |
| `DATABASE` | SQLite 数据库路径 | `database/blog.db` |
| `UPLOAD_FOLDER` | 上传文件目录 | `static/uploads` |
| `ALLOWED_EXTENSIONS` | 允许上传的文件类型 | 图片格式 |
| `MAX_CONTENT_LENGTH` | 上传文件大小限制 | 16MB |

## 技术栈

- **后端**: Flask 3.1 + SQLite 3 + Jinja2
- **前端**: 原生 JavaScript + CSS 自定义属性主题系统
- **存储**: SQLite（文件数据库，无需额外部署）

## License

MIT
