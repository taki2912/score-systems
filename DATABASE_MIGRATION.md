# 数据库迁移操作指南

## 📝 以后修改数据库字段的步骤

### 1. 修改 models.py
例如添加新字段：
```python
class Member(db.Model):
    # 原有字段...
    nickname = db.Column(db.String(50), default='')  # 新增
```

### 2. 生成迁移脚本
```bash
cd "F:\Program Files\score-system"
flask db migrate -m "添加 nickname 字段"
```

### 3. 应用到本地（如果本地也用 PostgreSQL）
```bash
flask db upgrade
```

### 4. 推送到 GitHub
```bash
git add .
git commit -m "添加 nickname 字段"
git push
```

### 5. Railway 自动部署
Railway 会自动运行迁移，更新线上数据库

---

## 🚀 首次初始化（只需执行一次）

```bash
cd "F:\Program Files\score-system"
pip install Flask-Migrate
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

---

## 📋 常用命令

```bash
# 查看当前迁移状态
flask db current

# 查看迁移历史
flask db history

# 回滚到上一个版本
flask db downgrade

# 升级到最新版本
flask db upgrade
```

---

## ⚠️ 注意事项

- 每次修改 models.py 后都要运行 `flask db migrate`
- 迁移文件会保存在 `migrations/` 目录
- 推送时要包含 `migrations/` 目录
- Railway 部署时会自动执行 `flask db upgrade`
