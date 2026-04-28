#!/usr/bin/env python3
"""
Database seeder - populates the database with initial data.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from blog import create_app
from blog.db import get_db, query, execute


def seed():
    app = create_app('development')
    with app.app_context():
        db = get_db()

        # Check if already seeded
        existing = query('SELECT COUNT(*) as c FROM users', one=True)
        if existing and existing['c'] > 0:
            print('Database already seeded, skipping.')
            return

        print('Seeding database...')

        # Create admin user (password: admin123)
        from blog.models.user import create_user
        create_user('admin', 'admin123', '管理员', 'admin@dbkuaizi.com', 'admin')
        create_user('editor', 'editor123', '编辑', 'editor@dbkuaizi.com', 'editor')
        print('  Created users: admin/admin123, editor/editor123')

        # Categories
        from blog.models.category import create_category
        coding = create_category('编码', 'coding', '技术文章、编程笔记', None, 1)
        reading = create_category('阅读', 'reading', '读书笔记、书评与感悟', None, 2)
        life = create_category('杂谈', 'life', '生活随笔与思考', None, 3)

        # Sub-categories
        create_category('Go', 'go', 'Go 语言相关', coding, 1)
        create_category('PHP', 'php', 'PHP 相关', coding, 2)
        create_category('Linux', 'linux', 'Linux 系统与运维', coding, 3)
        create_category('数据库', 'database', '数据库相关', coding, 4)
        create_category('前端', 'frontend', '前端技术', coding, 5)
        create_category('算法', 'algorithm', '算法与数据结构', coding, 6)
        create_category('容器', 'container', 'Docker/K8s 相关', coding, 7)
        print('  Created categories with sub-categories')

        # Posts
        from blog.models.post import create_post
        posts_data = [
            {
                'title': 'Go 语言并发编程模式详解',
                'slug': 'go-concurrency-patterns',
                'content': '''## Goroutine 基础

Go 语言诞生于 2009 年，由 Robert Griesemer、Rob Pike 和 Ken Thompson 设计。它的并发模型基于 CSP（Communicating Sequential Processes）理论，通过 Goroutine 和 Channel 提供了简洁而强大的并发编程能力。

不同于传统的线程加锁模型，Go 倡导"不通过共享内存来通信，而通过通信来共享内存"。

```go
go func() {
    fmt.Println("Hello from goroutine")
}()
```

## 模式一：扇出/扇入（Fan-Out/Fan-In）

扇出模式是指将同一个任务分发到多个 Goroutine 并行处理，扇入模式则是将多个 Goroutine 的结果合并到一个 Channel 中。

```go
func fanOut(input <-chan int, workers int) []<-chan int {
    channels := make([]<-chan int, workers)
    for i := 0; i < workers; i++ {
        channels[i] = worker(input, i)
    }
    return channels
}
```

## 模式二：Pipeline（流水线）

Pipeline 模式将数据处理流程划分为多个阶段，每个阶段由一组 Goroutine 处理，通过 Channel 连接：

```go
func generate(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for _, n := range nums {
            out <- n
        }
    }()
    return out
}
```

## 总结

Go 的并发模型在处理现代分布式系统和网络服务时展现了极大的优势。熟练掌握这些并发模式，能帮助我们写出更高效、更健壮的 Go 程序。''',
                'excerpt': 'Go 语言以其简洁优雅的并发模型闻名。本文深入探讨 Goroutine 与 Channel 的常见使用模式。',
                'category_id': 4,  # Go
                'tags': 'Go,并发,Goroutine',
                'status': 'published',
                'cover_image': ''
            },
            {
                'title': '读《百年孤独》—— 家族的第一人被困在树上',
                'slug': 'reading-hundred-years-solitude',
                'content': '''"多年以后，面对行刑队，奥雷里亚诺·布恩迪亚上校将会回想起父亲带他去见识冰块的那个遥远的下午。"

这是《百年孤独》的开篇，也是文学史上最著名的开头之一。

## 循环的宿命

布恩迪亚家族的命运早已写在梅尔基亚德斯的羊皮卷上："家族的第一个人被困在树上，最后一个人正在被蚂蚁吃掉。"

## 孤独的多种形态

书中的每个角色都以自己的方式承受着孤独：

- **何塞·阿尔卡蒂奥·布恩迪亚** —— 探索者的孤独
- **奥雷里亚诺上校** —— 权力的孤独
- **阿玛兰塔** —— 爱与恨的孤独
- **蕾梅黛丝** —— 美丽的孤独

## 重读的感悟

第一次读时，我被魔幻的情节吸引。第二次读时，我看到了孤独背后的东西——布恩迪亚家族的百年孤独，某种程度上是现代人的孤独。''',
                'excerpt': '马尔克斯用魔幻现实主义编织的马孔多小镇，是一个关于命运与轮回的寓言。',
                'category_id': 2,  # 阅读
                'tags': '读书笔记,马尔克斯,魔幻现实主义',
                'status': 'published',
                'cover_image': ''
            },
            {
                'title': 'Linux 内核学习笔记：进程调度',
                'slug': 'linux-kernel-notes',
                'content': '''进程调度是操作系统最核心的功能之一。Linux 内核的调度器经历了数次重写，从最初的 O(n) 调度器，到 O(1) 调度器，再到 2.6.23 版本引入的 CFS（Completely Fair Scheduler，完全公平调度器）。

## 调度器演进简史

- **O(n) 调度器（Linux 2.4 及之前）**：每次调度时遍历所有进程
- **O(1) 调度器（Linux 2.6.0-2.6.22）**：引入优先级数组
- **CFS 调度器（Linux 2.6.23 至今）**：基于红黑树实现完全公平调度

## CFS 的核心思想

CFS 的设计理念非常朴素：如果系统中有 N 个可运行进程，理想情况下每个进程应该获得 1/N 的 CPU 时间。

```c
struct cfs_rq {
    struct rb_root tasks_timeline;
    struct rb_node *rb_leftmost;
    struct sched_entity *curr;
    u64 min_vruntime;
    unsigned int nr_running;
};
```

## 总结

CFS 的设计哲学是通过简单的数据结构和清晰的算法来达到公平调度的目标。''',
                'excerpt': 'Linux 内核的进程调度器演进历程与 CFS 完全公平调度器的核心原理。',
                'category_id': 5,  # Linux
                'tags': 'Linux,内核,进程调度',
                'status': 'published',
                'cover_image': ''
            },
            {
                'title': '当我谈跑步时，我谈些什么',
                'slug': 'when-i-talk-about-running',
                'content': '''村上春树说："Pain is inevitable. Suffering is optional."

## 跑步与写作

村上春树从 1982 年开始跑步，那年他 33 岁，刚刚决定成为一名职业小说家。

> "持之以恒，不乱节奏。这对长期作业至为重要。一旦节奏得以设定，其余的问题便可以迎刃而解。"

## 跑者的孤独

跑步是一项不需要同伴的运动。村上春树在书中承认，他并不享受团队运动。

## 关于坚持

> "今天不想跑，所以才去跑。这才是长距离跑者的思维方式。"

看完这本书后，我开始了自己的跑步计划。从最初的一公里就气喘吁吁，到三个月后能连续跑五公里。最大的收获不是体能变好了——而是每天有了一段完全属于自己的时间。''',
                'excerpt': '村上春树用跑步来类比写作。我想，跑步也可以类比编程——两者都需要耐力、专注和持续学习的心态。',
                'category_id': 2,  # 阅读
                'tags': '村上春树,跑步,读书笔记',
                'status': 'published',
                'cover_image': ''
            },
            {
                'title': 'SQLite 与 PostgreSQL：选型指南',
                'slug': 'sqlite-vs-postgresql',
                'content': '''最近在做一个新项目，需要选择数据库。在 SQLite 和 PostgreSQL 之间做选择时，我花了一些时间仔细对比了两者的异同。

**SQLite 和 PostgreSQL 没有绝对的优劣，只有是否适合你的场景。**

## SQLite 的优势

### 零配置
SQLite 不需要安装、配置或管理。你只需要一个数据库文件，就可以开始使用。

### 轻量级
SQLite 库本身只有几百 KB，运行时内存占用极低。

## PostgreSQL 的优势

### 功能全面
PostgreSQL 常被称为"开源界的 Oracle"。它拥有极其丰富的功能集。

### 并发处理
PostgreSQL 使用 MVCC（多版本并发控制）来处理并发访问。

## 选型建议

选择 SQLite 的场景：嵌入式应用、开发和测试、小规模网站。
选择 PostgreSQL 的场景：Web 应用、复杂查询、高可用需求。''',
                'excerpt': 'SQLite 和 PostgreSQL 分别代表了两种不同的设计哲学。本文从实际场景出发，分析如何选择合适的数据库。',
                'category_id': 6,  # 数据库
                'tags': 'SQLite,PostgreSQL,数据库',
                'status': 'published',
                'cover_image': ''
            },
            {
                'title': '正则语法速查',
                'slug': 'regular-expression-cheatsheet',
                'content': '''正则表达式是每个程序员必备的技能之一。本文整理了一份常用的正则语法速查表。

## 基础匹配

```
模式          | 描述                        | 示例
.             | 匹配任意单个字符            | a.c → "abc"
^             | 匹配字符串开头              | ^hello
$             | 匹配字符串结尾              | world$
*             | 匹配 0 次或多次             | ab*c
+             | 匹配 1 次或多次             | ab+c
?             | 匹配 0 次或 1 次            | ab?c
```

## 字符类

```
\d            | 匹配数字
\D            | 匹配非数字
\w            | 匹配单词字符
\W            | 匹配非单词字符
\s            | 匹配空白字符
\S            | 匹配非空白字符
```

## 常用正则示例

### 邮箱验证
```
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
```

### IP 地址（IPv4）
```
^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$
```''',
                'excerpt': '常用正则表达式语法速查表，包含字符匹配、量词、分组、零宽断言等核心概念。',
                'category_id': 1,  # 编码
                'tags': '正则,速查表,工具',
                'status': 'published',
                'cover_image': ''
            },
            {
                'title': '博客五年',
                'slug': 'blog-five-years',
                'content': '''转眼这个博客已经运行五年了。

五年前，我在 Typecho 上搭建了这个小站，初衷很简单——记录自己的技术学习和生活思考。

## 为什么要写博客

写博客的好处，这些年体会越来越深：

1. **加深理解** —— 把知识写出来，才是真正的掌握
2. **建立连接** —— 通过博客认识了很多志同道合的朋友
3. **记录成长** —— 回头看以前的文章，能清晰看到自己的进步

## 一些数据

这五年，博客共发布了 **60+** 篇文章，收到了 **200+** 条评论，总访问量超过 **10万**。

## 未来的计划

接下来，我希望能保持每月至少一篇的更新频率，同时计划写一些系列文章，更系统地分享知识。''',
                'excerpt': '转眼这个博客已经运行五年了。五年前，我在 Typecho 上搭建了这个小站。',
                'category_id': 3,  # 杂谈
                'tags': '博客,五年,总结',
                'status': 'published',
                'cover_image': ''
            },
            {
                'title': '多用户 PassKey 认证插件开发记录',
                'slug': 'passkey-auth-plugin',
                'content': '''最近为 Typecho 开发了一款多用户 PassKey 认证插件，记录一下开发过程中的一些思考和遇到的坑。

## 什么是 PassKey

PassKey 是一种基于 WebAuthn 标准的无密码认证方式。用户可以使用生物识别（指纹、面部识别）或设备 PIN 码来登录，无需记忆密码。

## 技术实现

插件的前端使用 WebAuthn API，后端验证签名。

```php
// 注册 PassKey
$credentials = $webauthn->createRegisterCredential($user->id, $challenge);
```

## 遇到的坑

1. **跨域问题** —— WebAuthn 要求使用 HTTPS，本地开发时需要注意
2. **用户关联** —— 多用户场景下，需要为每个用户管理多个 PassKey

插件已发布到 Typecho 插件市场，欢迎试用。''',
                'excerpt': '为 Typecho 开发的 PassKey 无密码认证插件，记录开发过程与技术细节。',
                'category_id': 5,  # PHP
                'tags': 'Typecho,PHP,PassKey,WebAuthn',
                'status': 'published',
                'cover_image': ''
            },
        ]

        for p in posts_data:
            create_post(**p)
        print(f'  Created {len(posts_data)} posts')

        # Links
        from blog.models.link import create_link
        links = [
            ('Perass', 'https://www.perass.com/', '一个技术博客', 1),
            ('Typecho', 'https://typecho.org/', '简洁的博客系统', 2),
            ('Go 语言中文网', 'https://studygolang.com/', 'Go 语言学习社区', 3),
            ('阮一峰的网络日志', 'https://www.ruanyifeng.com/blog/', '科技爱好者周刊', 4),
        ]
        for name, url, desc, sort in links:
            create_link(name, url, desc, '', sort, 1)
        print(f'  Created {len(links)} links')

        print('Done! Database seeded successfully.')


if __name__ == '__main__':
    seed()
