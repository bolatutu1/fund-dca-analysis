import os
import sys

# Determine project root from this file's location
_current_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_current_dir)

# Add both to path for imports
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from starlette.middleware.sessions import SessionMiddleware
from jinja2 import Environment, FileSystemLoader
from database import engine, Base, get_db, SessionLocal
from models import User
from routes import fund, analysis, auth, watchlist
import config

app = FastAPI(title="基金定投分析", version="1.0.0")

# Session middleware — 从 config 读取 SECRET_KEY
app.add_middleware(SessionMiddleware, secret_key=config.SECRET_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(_current_dir, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
TEMPLATES_DIR = os.path.join(_current_dir, "templates")
app.include_router(fund.router, prefix="/api/fund")
app.include_router(analysis.router, prefix="/api/analysis")
app.include_router(auth.router, prefix="/api/auth")
app.include_router(watchlist.router, prefix="/api/watchlist")

# Custom Jinja2 environment with cache disabled (Python 3.14 compatibility fix)
_jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    cache_size=0,
    autoescape=True,
)


def render_template(filename: str, context: dict) -> Response:
    """Render a Jinja2 template to HTML, bypassing Starlette's broken TemplateResponse."""
    template = _jinja_env.get_template(filename)
    html = template.render(**context)
    return Response(content=html, media_type="text/html; charset=utf-8")


def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        return user
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    user = get_current_user(request)
    return render_template("index.html", {
        "request": request,
        "user": user,
        "page_title": "首页 - 基金定投分析",
    })


@app.get("/analysis", response_class=HTMLResponse)
async def analysis_page(request: Request):
    user = get_current_user(request)
    fund_code = request.query_params.get("fund", "")
    return render_template("analysis.html", {
        "request": request,
        "user": user,
        "page_title": "定投分析 - 基金定投分析",
        "fund_code": fund_code,
    })


@app.get("/watchlist", response_class=HTMLResponse)
async def watchlist_page(request: Request):
    user = get_current_user(request)
    return render_template("watchlist.html", {
        "request": request,
        "user": user,
        "page_title": "自选基金 - 基金定投分析",
    })


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return render_template("login.html", {
        "request": request,
        "page_title": "登录 - 基金定投分析",
    })


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return render_template("register.html", {
        "request": request,
        "page_title": "注册 - 基金定投分析",
    })


@app.on_event("startup")
async def startup():
    # 确保 data 目录存在
    db_dir = os.path.dirname(config.DATABASE_URL.replace("sqlite:///", ""))
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)
