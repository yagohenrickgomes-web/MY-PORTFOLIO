"""
Portfólio de Yago Henrick Alves Gomes — FastAPI + PostgreSQL.

Como rodar:
    .venv\\Scripts\\python.exe -m uvicorn app:app --reload

Site público:  http://127.0.0.1:8000
Painel admin:  http://127.0.0.1:8000/<ADMIN_PATH>  (login padrão: admin / admin123)

O endereço do painel admin NÃO é fixo em "/admin" por segurança — ele é lido
da variável de ambiente ADMIN_PATH. Configure algo só seu (ex: "painel-yago-9x2")
no .env local e nas variáveis do Railway. Se ADMIN_PATH não estiver definida,
cai no padrão "/admin" (não recomendado em produção).
"""
from fastapi import FastAPI, APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import os
import secrets
import time

import database as db
import cv_generator

app = FastAPI(title="Portfólio - Yago Henrick")

ADMIN_PATH = os.environ.get("ADMIN_PATH", "admin").strip("/")
ADMIN_BASE = f"/{ADMIN_PATH}"

# ---------------------------------------------------------------------------
# Proteção simples contra força bruta no login.
# Guarda tentativas falhas por IP em memória; reseta quando o app reinicia.
# ---------------------------------------------------------------------------
_failed_attempts = {}
MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 15 * 60


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _is_locked_out(ip: str) -> bool:
    record = _failed_attempts.get(ip)
    if not record:
        return False
    count, last_attempt = record
    if count >= MAX_ATTEMPTS and (time.time() - last_attempt) < LOCKOUT_SECONDS:
        return True
    if (time.time() - last_attempt) >= LOCKOUT_SECONDS:
        _failed_attempts.pop(ip, None)
    return False


def _register_failed_attempt(ip: str):
    count, _ = _failed_attempts.get(ip, (0, 0))
    _failed_attempts[ip] = (count + 1, time.time())


def _clear_attempts(ip: str):
    _failed_attempts.pop(ip, None)


# Em produção (Railway), defina a variável de ambiente SECRET_KEY.
SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
IS_PRODUCTION = os.environ.get("RAILWAY_ENVIRONMENT") is not None
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    https_only=IS_PRODUCTION,
    same_site="lax",
    max_age=60 * 60 * 8,  # sessão expira em 8h
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

db.init_db()


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------
def require_login(request: Request):
    if not request.session.get("logged_in"):
        raise HTTPException(status_code=303, headers={"Location": f"{ADMIN_BASE}/login"})
    return True


# ---------------------------------------------------------------------------
# Site público
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    settings = db.get_settings()
    projects = db.get_projects()
    posts = db.get_posts(published_only=True, limit=3)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "settings": settings, "projects": projects, "posts": posts},
    )


@app.get("/blog", response_class=HTMLResponse)
def blog_list(request: Request):
    settings = db.get_settings()
    posts = db.get_posts(published_only=True)
    return templates.TemplateResponse(
        "blog_list.html",
        {"request": request, "settings": settings, "posts": posts},
    )


@app.get("/blog/{slug}", response_class=HTMLResponse)
def blog_post_page(slug: str, request: Request):
    settings = db.get_settings()
    post = db.get_post_by_slug(slug)
    if not post or not post["published"]:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(
        "blog_post.html",
        {"request": request, "settings": settings, "post": post},
    )


@app.get("/cv.pdf")
def download_cv():
    pdf_bytes = cv_generator.generate_cv_pdf()
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="Yago_Henrick_Alves_Gomes_CV.pdf"'},
    )


@app.get("/robots.txt", response_class=HTMLResponse)
def robots_txt(request: Request):
    base_url = str(request.base_url).rstrip("/")
    # Não listamos o caminho do admin aqui de propósito — o robots.txt é público,
    # e um "Disallow" nele acabaria denunciando justamente o endereço que escondemos.
    content = f"""User-agent: *
Allow: /

Sitemap: {base_url}/sitemap.xml
"""
    return HTMLResponse(content=content, media_type="text/plain")


@app.get("/sitemap.xml")
def sitemap_xml(request: Request):
    base_url = str(request.base_url).rstrip("/")
    posts = db.get_posts(published_only=True)

    urls = [
        {"loc": f"{base_url}/", "priority": "1.0"},
        {"loc": f"{base_url}/blog", "priority": "0.8"},
    ]
    for post in posts:
        urls.append({
            "loc": f"{base_url}/blog/{post['slug']}",
            "lastmod": post["created_at"].strftime("%Y-%m-%d"),
            "priority": "0.6",
        })

    xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        xml_parts.append("<url>")
        xml_parts.append(f"<loc>{u['loc']}</loc>")
        if "lastmod" in u:
            xml_parts.append(f"<lastmod>{u['lastmod']}</lastmod>")
        xml_parts.append(f"<priority>{u['priority']}</priority>")
        xml_parts.append("</url>")
    xml_parts.append("</urlset>")

    return HTMLResponse(content="".join(xml_parts), media_type="application/xml")


# ---------------------------------------------------------------------------
# Admin router — montado no caminho secreto definido por ADMIN_PATH
# ---------------------------------------------------------------------------
admin = APIRouter(prefix=ADMIN_BASE)


@admin.get("/login", response_class=HTMLResponse)
def admin_login_form(request: Request):
    if request.session.get("logged_in"):
        return RedirectResponse(ADMIN_BASE, status_code=303)
    return templates.TemplateResponse(
        "admin_login.html", {"request": request, "error": None, "admin_base": ADMIN_BASE}
    )


@admin.post("/login", response_class=HTMLResponse)
def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    ip = _client_ip(request)

    if _is_locked_out(ip):
        return templates.TemplateResponse(
            "admin_login.html",
            {"request": request, "error": "Muitas tentativas. Aguarde 15 minutos antes de tentar de novo.", "admin_base": ADMIN_BASE},
            status_code=429,
        )

    if db.verify_password(username, password):
        _clear_attempts(ip)
        request.session["logged_in"] = True
        request.session["username"] = username
        return RedirectResponse(ADMIN_BASE, status_code=303)

    _register_failed_attempt(ip)
    return templates.TemplateResponse(
        "admin_login.html",
        {"request": request, "error": "Usuário ou senha inválidos.", "admin_base": ADMIN_BASE},
        status_code=401,
    )


@admin.get("/logout")
def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)


@admin.get("", response_class=HTMLResponse)
def admin_dashboard(request: Request, _=Depends(require_login)):
    settings = db.get_settings()
    projects = db.get_projects()
    posts = db.get_posts()
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "settings": settings,
            "projects": projects,
            "posts": posts,
            "username": request.session.get("username"),
            "admin_base": ADMIN_BASE,
        },
    )


@admin.post("/settings/{key}")
async def admin_update_one_setting(
    key: str, request: Request,
    value_pt: str = Form(...), value_en: str = Form(...),
    _=Depends(require_login),
):
    db.update_setting(key, value_pt, value_en)
    return RedirectResponse(f"{ADMIN_BASE}#settings", status_code=303)


# ---- Projetos ----
@admin.post("/projects/new")
def admin_create_project(
    request: Request,
    title_pt: str = Form(...), title_en: str = Form(...),
    desc_pt: str = Form(...), desc_en: str = Form(...),
    tags: str = Form(""), is_public: str = Form(None),
    url: str = Form(""), media_class: str = Form("pm-1"),
    sort_order: int = Form(0),
    _=Depends(require_login),
):
    db.create_project({
        "title_pt": title_pt, "title_en": title_en,
        "desc_pt": desc_pt, "desc_en": desc_en,
        "tags": tags, "is_public": bool(is_public),
        "url": url, "media_class": media_class, "sort_order": sort_order,
    })
    return RedirectResponse(f"{ADMIN_BASE}#projects", status_code=303)


@admin.post("/projects/{project_id}/edit")
def admin_edit_project(
    project_id: int, request: Request,
    title_pt: str = Form(...), title_en: str = Form(...),
    desc_pt: str = Form(...), desc_en: str = Form(...),
    tags: str = Form(""), is_public: str = Form(None),
    url: str = Form(""), media_class: str = Form("pm-1"),
    sort_order: int = Form(0),
    _=Depends(require_login),
):
    db.update_project(project_id, {
        "title_pt": title_pt, "title_en": title_en,
        "desc_pt": desc_pt, "desc_en": desc_en,
        "tags": tags, "is_public": bool(is_public),
        "url": url, "media_class": media_class, "sort_order": sort_order,
    })
    return RedirectResponse(f"{ADMIN_BASE}#projects", status_code=303)


@admin.post("/projects/{project_id}/delete")
def admin_delete_project(project_id: int, request: Request, _=Depends(require_login)):
    db.delete_project(project_id)
    return RedirectResponse(f"{ADMIN_BASE}#projects", status_code=303)


# ---- Blog ----
@admin.post("/posts/new")
def admin_create_post(
    request: Request,
    title_pt: str = Form(...), title_en: str = Form(...),
    excerpt_pt: str = Form(""), excerpt_en: str = Form(""),
    content_pt: str = Form(...), content_en: str = Form(...),
    tag: str = Form("Python"), published: str = Form(None),
    _=Depends(require_login),
):
    db.create_post({
        "title_pt": title_pt, "title_en": title_en,
        "excerpt_pt": excerpt_pt, "excerpt_en": excerpt_en,
        "content_pt": content_pt, "content_en": content_en,
        "tag": tag, "published": bool(published),
    })
    return RedirectResponse(f"{ADMIN_BASE}#blog", status_code=303)


@admin.post("/posts/{post_id}/edit")
def admin_edit_post(
    post_id: int, request: Request,
    title_pt: str = Form(...), title_en: str = Form(...),
    excerpt_pt: str = Form(""), excerpt_en: str = Form(""),
    content_pt: str = Form(...), content_en: str = Form(...),
    tag: str = Form("Python"), published: str = Form(None),
    _=Depends(require_login),
):
    db.update_post(post_id, {
        "title_pt": title_pt, "title_en": title_en,
        "excerpt_pt": excerpt_pt, "excerpt_en": excerpt_en,
        "content_pt": content_pt, "content_en": content_en,
        "tag": tag, "published": bool(published),
    })
    return RedirectResponse(f"{ADMIN_BASE}#blog", status_code=303)


@admin.post("/posts/{post_id}/delete")
def admin_delete_post(post_id: int, request: Request, _=Depends(require_login)):
    db.delete_post(post_id)
    return RedirectResponse(f"{ADMIN_BASE}#blog", status_code=303)


# ---- Conta ----
@admin.post("/password")
def admin_change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    _=Depends(require_login),
):
    username = request.session.get("username")
    if not db.verify_password(username, current_password):
        settings = db.get_settings()
        projects = db.get_projects()
        posts = db.get_posts()
        return templates.TemplateResponse(
            "admin_dashboard.html",
            {
                "request": request, "settings": settings, "projects": projects, "posts": posts,
                "username": username, "password_error": "Senha atual incorreta.",
                "admin_base": ADMIN_BASE,
            },
            status_code=401,
        )
    db.change_admin_password(username, new_password)
    return RedirectResponse(f"{ADMIN_BASE}#account", status_code=303)


app.include_router(admin)
