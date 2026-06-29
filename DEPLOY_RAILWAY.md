# Railway 部署步骤

## 1. 准备工作

### 方式一：通过 GitHub 部署（推荐）

1. 在项目根目录初始化 Git 仓库（如果还没有）：
   ```powershell
   cd E:\admin\Documents\workspace\project_001_基金定投分析
   git init
   git add .
   git commit -m "Initial commit for Railway deployment"
   ```

2. 创建 GitHub 仓库，推送代码

3. 登录 [Railway.app](https://railway.app)

4. 点击 **New Project** → **Deploy from GitHub repo**

5. 选择你的仓库

### 方式二：直接上传文件

1. 登录 [Railway.app](https://railway.app)

2. 点击 **New Project** → **Deploy from git repository**

3. 选择 **Upload files**，将整个项目文件夹上传

## 2. 配置环境变量

在 Railway Dashboard 中，进入 **Variables** 标签页，添加以下环境变量：

| 变量名 | 值 | 说明 |
|--------|------|------|
| `SECRET_KEY` | 强随机字符串 | 从下面生成 |
| `PORT` | `8000` | 服务端口 |
| `DATABASE_PATH` | `/app/data/fund.db` | SQLite 数据库路径 |
| `DATA_CACHE_TTL` | `3600` | 数据缓存时间（秒） |

### 生成 SECRET_KEY

在本地运行：
```powershell
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

将输出的字符串复制到 Railway 的 `SECRET_KEY` 变量中。

## 3. 构建和部署

Railway 会自动检测 `Dockerfile` 并构建镜像。

- **Build Command**: 无需额外设置，Dockerfile 已包含
- **Start Command**: `cd src && uvicorn main:app --host 0.0.0.0 --port $PORT`

## 4. 验证部署

部署完成后，Railway 会给你一个类似 `https://fund-analysisxxx.up.railway.app` 的 URL。

访问该 URL 验证：
- 首页是否正常加载
- 基金搜索功能是否正常
- 用户注册/登录是否正常
- 定投分析页面是否正常

## 5. 自定义域名（可选）

在 Railway Dashboard → **Settings** → **Domains** 中添加自定义域名。

## 常见问题

### Q: 静态文件（CSS/JS）无法加载
A: 检查 Dockerfile 中 `COPY src/ ./` 是否正确包含了 static 目录

### Q: 数据库无法写入
A: 确保 `/app/data` 目录存在且可写。可以在 Dockerfile 中添加 `RUN mkdir -p /app/data`

### Q: AKShare 数据获取失败
A: 可能是网络问题，AKShare 需要从国内源获取数据。Railway 的服务器在海外，可能需要配置代理或改用本地数据

## 免费额度

Railway 提供每月 $5 的免费额度，对于个人项目通常够用。超过后需要绑定信用卡。
