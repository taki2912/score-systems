# 计分系统

基于 Flask 的俱乐部计分管理系统

## 🌐 在线访问

**生产环境**: https://web-production-8483d5.up.railway.app/

**默认管理员账号**: `admin` / `admin123` (首次登录需修改密码)

## ✨ 功能特性

- 🏢 俱乐部管理：创建、编辑、删除俱乐部
- 👥 成员管理：添加成员、上传头像、管理分数
- 📊 分数追踪：完整的分数变动历史和趋势图
- 🔐 权限系统：超级管理员、管理员、普通用户三级权限
- 📝 审批流程：用户申请查看历史需管理员审批
- 📱 响应式设计：支持手机、平板、桌面访问

## 🚀 本地运行

```bash
# 克隆仓库
git clone https://github.com/taki2912/score-systems.git
cd score-systems

# 安装依赖
pip install -r requirements.txt

# 运行应用
python app.py

# 访问 http://localhost:5000
```

## 📦 部署到 Railway

1. Fork 本仓库到你的 GitHub
2. 访问 https://railway.app 并用 GitHub 登录
3. 创建新项目，选择你的仓库
4. Railway 自动部署
5. 在 Settings → Domains 生成域名

## 🔄 保持在线

Railway 免费套餐无活动时会休眠，使用定时访问脚本：

```bash
# Windows: 双击运行
start_keep_alive.bat

# 或命令行
python keep_alive.py
```

## 📖 完整文档

详见 [PROJECT_SPEC.md](PROJECT_SPEC.md)

## 🛠️ 技术栈

- **后端**: Flask 3.1
- **数据库**: SQLite + Flask-SQLAlchemy
- **前端**: Bootstrap 5.3 + Chart.js
- **部署**: Railway
- **版本控制**: Git + GitHub

## 📄 许可

MIT License
