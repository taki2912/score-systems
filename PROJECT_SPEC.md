# 计分系统项目说明书

> 最后更新: 2026-04-20

## 项目概述

基于 Flask 的俱乐部计分管理系统。管理员可创建俱乐部、管理成员和分数，游客可查看俱乐部和分数排行并点击成员进入详情页，用户可自行注册账号，登录后可申请查看成员历史变动（需确认本人 + 管理员审批），审批通过后可查看完整历史记录含趋势图。

## 在线访问

- **生产环境**: https://web-production-8483d5.up.railway.app/
- **GitHub 仓库**: https://github.com/taki2912/score-systems
- **部署平台**: Railway (免费托管)

## 默认账号

- **超级管理员**: `admin` / `admin123` (首次登录强制改密)

## 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | Flask 3.1 |
| ORM | Flask-SQLAlchemy 3.1 |
| 数据库 | SQLite (单文件 score.db) |
| 前端 | Jinja2 模板 + Bootstrap 5.3 + Chart.js 4.4 |
| 密码 | Werkzeug generate_password_hash/check_password_hash |
| 头像 | 本地文件上传 (static/avatars/) |
| 图表 | Chart.js (CDN) |

## 项目结构

```
F:\Program Files\score-system\
├── app.py                  # 主应用: 路由 + 业务逻辑
├── config.py               # 配置: DB路径/密钥/上传设置
├── models.py               # 数据模型: Club/Member/ScoreChange/ViewRequest/User
├── auth.py                 # 认证: 登录/登出/权限装饰器
├── requirements.txt        # 依赖: flask, flask-sqlalchemy, werkzeug
├── score.db                # SQLite 数据库 (运行时自动创建)
├── PROJECT_SPEC.md         # 本文件
├── static/
│   ├── avatars/            # 成员头像图片存放目录
│   └── css/style.css       # 自定义样式 + 首页英雄区 + 领奖台 + 手机适配
└── templates/
    ├── base.html           # 基础布局 (导航栏/消息提示/用户状态)
    ├── index.html          # 首页: 英雄区域 + 俱乐部卡片 (游客可访问)
    ├── club_detail.html    # 俱乐部详情: 前三名领奖台 + 成员卡片网格 (游客可访问)
    ├── member_detail.html  # 成员详情: 统计卡+趋势图+历史表格 (需审批后查看)
    ├── request_view.html   # 申请查看: 确认本人+非本人填原因
    ├── login.html          # 登录页 (含注册链接)
    ├── register.html       # 注册页
    ├── change_password.html# 修改密码页
    └── admin/
        ├── clubs.html           # 俱乐部管理
        ├── create_club.html     # 创建俱乐部
        ├── club_members.html    # 成员管理 (大卡片布局)
        ├── create_member.html   # 添加成员 (含头像上传, 分数以万为单位)
        ├── edit_member.html     # 编辑成员 (含头像更换+分数修改)
        ├── users.html           # 用户账号管理
        ├── create_user.html     # 创建登录账号
        ├── review_list.html     # 查看申请审核列表 (卡片布局)
        ├── review_detail.html   # 审核详情
        └── score_changes.html   # 全局分数变动记录
```

## 数据库模型

### Club (俱乐部)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| name | TEXT UNIQUE | 俱乐部名称 (如 "86硬上山") |
| description | TEXT | 简介 (可空) |
| created_at | DATETIME | 创建时间 |

### Member (成员)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| club_id | INTEGER FK → clubs.id | 所属俱乐部 |
| display_id | TEXT | 成员ID (俱乐部内唯一, 如 "001") |
| name | TEXT | 成员名称 |
| avatar | TEXT | 头像文件名 (如 "abc123.jpg", 可空) |
| score | REAL | 当前分数 (千/万级别, 如 85000) |
| is_active | BOOLEAN | 是否启用 |
| created_at | DATETIME | 创建时间 |

约束: (club_id, display_id) 联合唯一

### ScoreChange (分数变动记录)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| member_id | INTEGER FK → members.id | 关联成员 |
| old_score | REAL | 变动前分数 |
| new_score | REAL | 变动后分数 |
| change_type | TEXT | admin_edit (管理员直接改) |
| reason | TEXT | 变动原因 (必填) |
| is_self_confirmed | BOOLEAN | 是否确认本人操作 |
| status | TEXT | approved (管理员改分直接生效) |
| applicant_id | INTEGER FK → users.id | 操作人 |
| reviewed_by | INTEGER FK → users.id | 审核人 |
| created_at | DATETIME | 时间 |
| reviewed_at | DATETIME | 审核时间 |

### ViewRequest (查看历史申请)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| member_id | INTEGER FK → members.id | 目标成员 |
| applicant_id | INTEGER FK → users.id | 申请人 |
| is_self_confirmed | BOOLEAN | 是否确认本人 |
| not_self_reason | TEXT | 非本人原因说明 (可空) |
| status | TEXT | pending / approved / rejected |
| reviewed_by | INTEGER FK → users.id | 审核人 (可空) |
| created_at | DATETIME | 申请时间 |
| reviewed_at | DATETIME | 审核时间 (可空) |

约束: (member_id, applicant_id) 联合唯一 — 每人对每个成员只能申请一次

### User (登录账号)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| username | TEXT UNIQUE | 登录用户名 |
| password_hash | TEXT | 密码哈希 |
| role | TEXT | super_admin / admin / user |
| is_active | BOOLEAN | 是否启用 |
| must_change_password | BOOLEAN | 是否需要强制改密 |
| created_at | DATETIME | 创建时间 |

**重要区分**: User 是登录账号(谁可以操作), Member 是计分对象(谁的分数)。两者独立。

### 角色权限

| 权限 | super_admin | admin | user |
|------|:-----------:|:-----:|:----:|
| 俱乐部增删 | YES | - | - |
| 添加成员 | YES | YES | - |
| 成员启禁/删除 | YES | - | - |
| 成员信息编辑(头像,ID,名称) | YES | - | - |
| 修改分数(必填原因) | YES | YES | - |
| 审核查看申请 | YES | YES | - |
| 查看分数变动记录 | YES | YES | - |
| 用户与权限管理 | YES | - | - |
| 查看成员历史 | YES | YES(需审批) | 需审批 |
| 查看俱乐部/排行 | YES | YES | YES |
| 注册账号 | YES | YES | YES |

## 路由一览

### 公开路由 (游客可访问)
| 路由 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 首页 - 英雄区域 + 俱乐部卡片 |
| `/club/<club_id>` | GET | 俱乐部详情 - 领奖台 + 成员排行 |
| `/member/<member_id>` | GET | 成员详情页 (无权限则显示申请/登录引导) |
| `/login` | GET/POST | 登录 |
| `/register` | GET/POST | 注册 |

### 需登录路由
| 路由 | 方法 | 说明 |
|------|------|------|
| `/member/<member_id>/request_view` | GET/POST | 申请查看历史 (确认本人) |
| `/logout` | GET | 登出 |
| `/change_password` | GET/POST | 修改密码 |

### 管理员路由 (admin + super_admin)
| 路由 | 方法 | 说明 |
|------|------|------|
| `/admin/club/<club_id>/members` | GET | 成员管理 (大卡片) |
| `/admin/club/<club_id>/member/create` | GET/POST | 添加成员(含头像) |
| `/admin/member/<member_id>/edit` | GET/POST | 编辑成员(管理员仅改分+必填原因,超管可改所有) |
| `/admin/reviews` | GET | 查看申请审核列表 (?status=) |
| `/admin/review/<request_id>` | GET/POST | 审核查看申请 |
| `/admin/score_changes` | GET | 全局分数变动记录 |

### 超级管理员专属路由
| 路由 | 方法 | 说明 |
|------|------|------|
| `/admin/clubs` | GET | 俱乐部管理 |
| `/admin/club/create` | GET/POST | 创建俱乐部 |
| `/admin/club/<club_id>/delete` | POST | 删除俱乐部 |
| `/admin/member/<member_id>/toggle_active` | POST | 启用/禁用成员 |
| `/admin/member/<member_id>/delete` | POST | 删除成员 |
| `/admin/users` | GET | 用户与权限管理 |
| `/admin/user/create` | GET/POST | 创建登录账号 |
| `/admin/user/<user_id>/toggle_active` | POST | 启用/禁用用户 |
| `/admin/user/<user_id>/reset_password` | POST | 重置用户密码 |
| `/admin/user/<user_id>/change_role` | POST | 修改用户角色 |

### API 路由
| 路由 | 方法 | 说明 |
|------|------|------|
| `/api/member/<member_id>/chart_data` | GET | 成员分数趋势图数据 (JSON) |

## 权限模型

```
游客: 首页俱乐部列表 → 俱乐部成员排行(领奖台+卡片)
      └─ 点击成员 → 进入详情页 → 看到"需登录"提示 → 引导登录

登录用户: 游客权限 + 成员详情页
          └─ 无权限时: "申请查看"按钮 → 确认本人 → 等待管理员审批
          └─ 已审批: 看到统计卡 + 趋势图 + 历史表格

管理员: 全部权限 + 俱乐部CRUD + 成员CRUD + 用户CRUD + 审批查看申请 + 分数变动记录
        └─ 直接查看任何成员历史，无需申请
        └─ 改分直接生效，自动记录原因
```

## 查看历史审批流程

```
用户点击成员 → 详情页显示"申请查看"
  → 填写是否本人
     ├─ 是本人 → 提交申请 → 管理员审核 → 通过(可看历史) / 驳回
     └─ 非本人 → 必须填写原因(代为查看原因) → 提交 → 管理员审核 → 通过 / 驳回
```

每人对每个成员只能申请一次 (联合唯一约束)。

## 分数修改规则

- 管理员和超级管理员修改分数时，**必须填写修改原因**
- 原因输入框始终显示，不论分数是否改变
- 修改记录自动保存到 `score_changes` 表，状态为 `approved`

## 分数显示格式 (score_fmt 过滤器)

```python
# app.py 中的 format_score 函数, 注册为 Jinja2 过滤器 score_fmt
85000  → "85,000"
120000 → "120,000"
5000   → "5,000"
300    → "300"
```

分数直接显示原始数字，带千分位逗号分隔。

## 首页设计

- **英雄区域**: 深色渐变背景 + 浮动光效动画 + 统计数据
- **俱乐部卡片**: 渐变图标 + 悬浮动态效果 + 点击跳转

## 俱乐部详情页设计

- **领奖台**: 前三名突出展示 (金/银/铜边框头像 + 名次徽章)
- **全部成员**: 卡片网格, 响应式布局

## 成员详情页设计

- **信息头部**: 头像 + 名称 + ID + 俱乐部 + 当前分数(大字)
- **统计卡片**: 总变动次数 / 最高分 / 最低分 / 最近变动
- **趋势图**: Chart.js 折线图 (从 /api/member/<id>/chart_data 获取数据)
- **历史表格**: 时间 / 变动前 / 变动后 / 差值(+绿色 -红色) / 类型 / 原因 / 本人

## 管理员成员管理

- 大卡片布局 (非表格), 每个成员独立卡片展示头像+信息+操作按钮
- 分数以 score_fmt 格式显示
- 所有管理员(admin + super_admin)可添加成员和修改分数
- 导航栏"管理"下拉菜单显示所有俱乐部的成员管理入口

## 头像上传

- 存放: `static/avatars/`
- 命名: `{uuid}.{ext}` (避免重名冲突)
- 格式: PNG/JPG/JPEG/GIF/WebP
- 限制: 最大 2MB (MAX_CONTENT_LENGTH)
- 编辑成员更换头像时自动删除旧文件

## 手机适配

- viewport: `width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no`
- 移动端 meta: apple-mobile-web-app-capable / mobile-web-app-capable
- 成员卡片: col-6(手机) / col-sm-4(平板) / col-md-3(桌面) / col-lg-2(大屏)
- 管理卡片: col-12 / col-sm-6 / col-md-4 / col-lg-3
- 表格: table-responsive 横向滚动
- 小屏下缩小字号/边距/头像尺寸 (CSS @media max-width: 576px)

## 初始化数据

首次运行 `python app.py` 自动创建:
1. 超级管理员账号: `admin` / `admin123` (首次登录强制改密, role=super_admin)
2. 默认俱乐部: "86硬上山"

用户也可通过 `/register` 页面自行注册普通账号。
超级管理员可在"用户与权限"页面修改任何用户的角色(admin/user/super_admin)。

## 项目文件说明

### 核心文件
- `app.py` - 主应用，包含所有路由和业务逻辑
- `models.py` - 数据库模型定义
- `auth.py` - 认证和权限装饰器
- `config.py` - 配置文件

### 部署配置
- `requirements.txt` - Python 依赖
- `railway.json` - Railway 部署配置
- `Procfile` - 进程启动配置
- `render.yaml` - Render 部署配置（备用）

### 运维工具
- `keep_alive.py` - 定时访问脚本，防止服务休眠
- `start_keep_alive.bat` - Windows 快捷启动脚本

### 文档
- `PROJECT_SPEC.md` - 项目完整说明书（本文件）
- `README.md` - 项目简介

## 运行方式

### 本地运行
```bash
cd "F:\Program Files\score-system"
pip install -r requirements.txt
python app.py
# 访问 http://localhost:5000
```

### 部署到 Railway
1. 推送代码到 GitHub
2. 访问 https://railway.app 并用 GitHub 登录
3. 创建新项目，选择 GitHub 仓库
4. Railway 自动检测配置并部署
5. 在 Settings → Domains 生成固定域名

### 保持在线（防止休眠）
Railway 免费套餐无活动时会休眠，使用定时访问脚本保持在线：

**Windows:**
```bash
双击运行 start_keep_alive.bat
```

**命令行:**
```bash
python keep_alive.py
```

脚本每 10 分钟自动访问一次网站，保持服务在线。

## 外网访问

### 方式1: Railway 部署（推荐）
- 固定域名，永久有效
- 免费额度充足（每月 $5）
- 自动 HTTPS
- 当前部署: https://web-production-8483d5.up.railway.app/

### 方式2: Cloudflare Tunnel（临时）
```bash
cloudflared tunnel --url http://localhost:5000
# 分配临时域名 xxx.trycloudflare.com，重启后域名会变
```

### 方式3: Cloudflare Tunnel（固定域名）
需要 Cloudflare 账号和自己的域名：
```bash
cloudflared tunnel login
cloudflared tunnel create score-system
cloudflared tunnel route dns score-system score.yourdomain.com
cloudflared tunnel run score-system
```

## 前端交互细节

- `club_detail.html`: 前三名领奖台布局 (2nd-1st-3rd排列)
- `member_detail.html`: Chart.js 异步加载趋势图数据；统计卡显示 max/min/最近变动
- `request_view.html`: "是否本人"单选切换时动态显示/隐藏"非本人原因"框
- `edit_member.html`: 修改分数时动态显示/隐藏"修改原因"输入框
- 分数格式化: 所有显示通过 `|score_fmt` 过滤器 (万/千/原始)
- 所有页面消息通过 Flask flash + Bootstrap alert 展示

## 配置项 (config.py)

| 配置 | 默认值 | 说明 |
|------|--------|------|
| SQLALCHEMY_DATABASE_URI | sqlite:///score.db | 数据库路径 |
| SECRET_KEY | change-this-in-production-2024 | Session 密钥 |
| UPLOAD_FOLDER | static/avatars/ | 头像存储目录 |
| MAX_CONTENT_LENGTH | 2MB | 上传文件大小限制 |
