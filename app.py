"""
Portfólio de Yago Henrick Alves Gomes — FastAPI + SQLite.

Como rodar:
    .venv\\Scripts\\python.exe -m uvicorn app:app --reload

Site público:  http://127.0.0.1:8000
Painel admin:  http://127.0.0.1:8000/admin  (login padrão: admin / admin123)
"""
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import os
import secrets

import database as db

app = FastAPI(title="Portfólio - Yago Henrick")

# Em produção (Railway), defina a variável de ambiente SECRET_KEY.
# Localmente, se não estiver definida, usa uma gerada na hora (sessões caem a cada restart).
SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

db.init_db()


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------
def require_login(request: Request):
    if not request.session.get("logged_in"):
        raise HTTPException(status_code=303, headers={"Location": "/admin/login"})
    return True


# ---------------------------------------------------------------------------
# Site público
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    settings = db.get_settings()
    projects = db.get_projects()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "settings": settings, "projects": projects},
    )


# ---------------------------------------------------------------------------
# Admin - login / logout
# ---------------------------------------------------------------------------
@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_form(request: Request):
    if request.session.get("logged_in"):
        return RedirectResponse("/admin", status_code=303)
    return templates.TemplateResponse("admin_login.html", {"request": request, "error": None})


@app.post("/admin/login", response_class=HTMLResponse)
def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    if db.verify_password(username, password):
        request.session["logged_in"] = True
        request.session["username"] = username
        return RedirectResponse("/admin", status_code=303)
    return templates.TemplateResponse(
        "admin_login.html",
        {"request": request, "error": "Usuário ou senha inválidos."},
        status_code=401,
    )


@app.get("/admin/logout")
def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)


# ---------------------------------------------------------------------------
# Admin - dashboard
# ---------------------------------------------------------------------------
@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, _=Depends(require_login)):
    settings = db.get_settings()
    projects = db.get_projects()
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "settings": settings,
            "projects": projects,
            "username": request.session.get("username"),
        },
    )


@app.post("/admin/settings")
def admin_update_settings(request: Request, _=Depends(require_login)):
    return RedirectResponse("/admin", status_code=303)


@app.post("/admin/settings/{key}")
async def admin_update_one_setting(
    key: str, request: Request,
    value_pt: str = Form(...), value_en: str = Form(...),
    _=Depends(require_login),
):
    db.update_setting(key, value_pt, value_en)
    return RedirectResponse("/admin#settings", status_code=303)


@app.post("/admin/projects/new")
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
    return RedirectResponse("/admin#projects", status_code=303)


@app.post("/admin/projects/{project_id}/edit")
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
    return RedirectResponse("/admin#projects", status_code=303)


@app.post("/admin/projects/{project_id}/delete")
def admin_delete_project(project_id: int, request: Request, _=Depends(require_login)):
    db.delete_project(project_id)
    return RedirectResponse("/admin#projects", status_code=303)


@app.post("/admin/password")
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
        return templates.TemplateResponse(
            "admin_dashboard.html",
            {
                "request": request, "settings": settings, "projects": projects,
                "username": username, "password_error": "Senha atual incorreta.",
            },
            status_code=401,
        )
    db.change_admin_password(username, new_password)
    return RedirectResponse("/admin#account", status_code=303)
