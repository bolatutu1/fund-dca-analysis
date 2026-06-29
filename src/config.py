import os

# 基础配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

# 数据库
_db_path = os.environ.get("DATABASE_PATH", os.path.join(PROJECT_DIR, "data", "fund.db"))
DATABASE_URL = f"sqlite:///{_db_path}"

# 服务器
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))

# 认证
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

# AKShare 数据缓存（秒）
DATA_CACHE_TTL = int(os.environ.get("DATA_CACHE_TTL", "3600"))
