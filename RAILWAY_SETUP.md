# Railway 环境变量配置说明

## 问题：数据库表结构未创建

Railway 的 Web Service 需要连接到 PostgreSQL 数据库。

## 解决方案：

### 1. 在 Railway Dashboard 配置环境变量

1. 访问 https://railway.app
2. 进入项目
3. 点击 **Web Service**（你的 Flask 应用）
4. 点击 **"Variables"** 标签
5. 点击 **"+ New Variable"**
6. 选择 **"Add Reference"**
7. 选择 **PostgreSQL** → **DATABASE_URL**
8. 保存

这样 Web Service 就能自动获取 PostgreSQL 的连接地址。

### 2. 重新部署

配置完成后，点击 **"Deployments"** → 最新部署右侧的三个点 → **"Redeploy"**

### 3. 验证

部署完成后，再次检查 PostgreSQL 的 Data 标签，应该能看到表结构了。
