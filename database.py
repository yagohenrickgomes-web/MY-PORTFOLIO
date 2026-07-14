"""
Camada de banco de dados do portfólio — PostgreSQL.

Lê a conexão de DATABASE_URL (variável de ambiente):
- Localmente: coloque num arquivo .env na raiz do projeto (veja .env.example)
- No Railway: injetado automaticamente quando você conecta o addon PostgreSQL
"""
import hashlib
import hmac
import os

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL não configurada. Crie um arquivo .env na raiz do "
            "projeto com: DATABASE_URL=postgresql://usuario:senha@localhost:5432/nome_do_banco"
        )
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value_pt TEXT NOT NULL DEFAULT '',
        value_en TEXT NOT NULL DEFAULT ''
    );

    CREATE TABLE IF NOT EXISTS projects (
        id SERIAL PRIMARY KEY,
        title_pt TEXT NOT NULL,
        title_en TEXT NOT NULL,
        desc_pt TEXT NOT NULL,
        desc_en TEXT NOT NULL,
        tags TEXT NOT NULL DEFAULT '',
        is_public BOOLEAN NOT NULL DEFAULT FALSE,
        url TEXT DEFAULT '',
        media_class TEXT NOT NULL DEFAULT 'pm-1',
        sort_order INTEGER NOT NULL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS admin_user (
        username TEXT PRIMARY KEY,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL
    );
    """)
    conn.commit()

    # Seed default settings only if empty
    cur.execute("SELECT COUNT(*) AS c FROM settings")
    if cur.fetchone()["c"] == 0:
        defaults = [
            ("hero_role", "Business Process & AI Automation Specialist",
             "Business Process & AI Automation Specialist"),
            ("hero_sub",
             "Transformando processos empresariais em soluções inteligentes utilizando Inteligência Artificial, Python e Análise de Dados.",
             "Turning business processes into intelligent solutions using Artificial Intelligence, Python and Data Analysis."),
            ("about_p1",
             "Minha trajetória começou na administração e contabilidade, mas foi na tecnologia que encontrei a ferramenta certa para resolver problemas reais de negócio.",
             "My path started in administration and accounting, but it was in technology that I found the right tool to solve real business problems."),
            ("about_p2",
             "Trabalho com Inteligência Artificial, Python e Business Intelligence para automatizar rotinas, eliminar retrabalho e transformar dados dispersos em decisões claras.",
             "I work with Artificial Intelligence, Python and Business Intelligence to automate routines, eliminate rework and turn scattered data into clear decisions."),
            ("about_p3",
             "Minha visão é simples: tecnologia só tem valor quando resolve um problema de negócio de verdade.",
             "My view is simple: technology only has value when it solves a real business problem."),
            ("contact_email", "yago.contato@email.com", "yago.contato@email.com"),
            ("linkedin_url", "https://linkedin.com", "https://linkedin.com"),
            ("github_url", "https://github.com", "https://github.com"),
        ]
        cur.executemany(
            "INSERT INTO settings (key, value_pt, value_en) VALUES (%s, %s, %s)", defaults
        )

    # Seed default projects only if empty
    cur.execute("SELECT COUNT(*) AS c FROM projects")
    if cur.fetchone()["c"] == 0:
        projects = [
            ("SagaCap Contratos — BI Dashboard", "SagaCap Contratos — BI Dashboard",
             "Dashboard desktop para gestão de contratos: alertas de vencimento, mapa por estado, relatórios em PDF e sincronização com Google Sheets. Uso interno da equipe de Contratos.",
             "Desktop dashboard for contract management: expiry alerts, state-level map, PDF reports and Google Sheets sync. Internal use for the Contracts team.",
             "Python, PySide6, PostgreSQL", False, "", "pm-1", 1),
            ("Sistema Administrativo (Tela Admin)", "Administrative System",
             "Painel administrativo interno com controle de usuários e permissões, usado para gestão de operações de um cliente.",
             "Internal administrative panel with user and permission management, used to run a client's operations.",
             "Python, SQLite, Backend", False, "", "pm-2", 2),
            ("MM Fashion — E-commerce", "MM Fashion — E-commerce",
             "Loja virtual completa de moda feminina: vitrine, categorias, promoções e painel administrativo com KPIs e gestão de pedidos.",
             "Full women's fashion online store: showcase, categories, promotions and an admin panel with KPIs and order management.",
             "HTML, CSS, JavaScript", True, "https://github.com/", "pm-3", 3),
            ("Site Institucional — Advocacia", "Law Firm Website",
             "Site institucional para escritório de advocacia, com identidade visual sóbria, áreas de atuação e formulário de contato.",
             "Institutional website for a law firm, with a sober visual identity, practice areas and a contact form.",
             "HTML, CSS, JavaScript", True, "https://github.com/", "pm-4", 4),
            ("Site Institucional — Contabilidade", "Accounting Firm Website",
             "Site institucional para escritório de contabilidade, com apresentação de serviços e captação de clientes.",
             "Institutional website for an accounting firm, showcasing services and capturing new client leads.",
             "HTML, CSS, JavaScript", True, "https://github.com/", "pm-5", 5),
            ("Site Institucional — Confeitaria", "Bakery Website",
             "Site institucional para confeitaria, com catálogo de produtos e pedidos via WhatsApp. Em desenvolvimento.",
             "Institutional website for a bakery, with a product catalog and WhatsApp ordering. In development.",
             "HTML, CSS, JavaScript", True, "https://github.com/", "pm-6", 6),
        ]
        cur.executemany(
            """INSERT INTO projects
               (title_pt, title_en, desc_pt, desc_en, tags, is_public, url, media_class, sort_order)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            projects,
        )

    # Seed default admin user (username: admin / password: admin123) only if empty
    cur.execute("SELECT COUNT(*) AS c FROM admin_user")
    if cur.fetchone()["c"] == 0:
        salt = os.urandom(16).hex()
        password_hash = hash_password("admin123", salt)
        cur.execute(
            "INSERT INTO admin_user (username, password_hash, salt) VALUES (%s, %s, %s)",
            ("admin", password_hash, salt),
        )

    conn.commit()
    cur.close()
    conn.close()


def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), 200_000
    ).hex()


def verify_password(username: str, password: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM admin_user WHERE username = %s", (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return False
    computed = hash_password(password, row["salt"])
    return hmac.compare_digest(computed, row["password_hash"])


def change_admin_password(username: str, new_password: str):
    salt = os.urandom(16).hex()
    password_hash = hash_password(new_password, salt)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE admin_user SET password_hash = %s, salt = %s WHERE username = %s",
        (password_hash, salt, username),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_settings() -> dict:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM settings")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {row["key"]: {"pt": row["value_pt"], "en": row["value_en"]} for row in rows}


def update_setting(key: str, value_pt: str, value_en: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE settings SET value_pt = %s, value_en = %s WHERE key = %s",
        (value_pt, value_en, key),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_projects(public_only: bool = False) -> list:
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM projects"
    if public_only:
        query += " WHERE is_public = TRUE"
    query += " ORDER BY sort_order ASC, id ASC"
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(row) for row in rows]


def get_project(project_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(row) if row else None


def create_project(data: dict):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO projects
           (title_pt, title_en, desc_pt, desc_en, tags, is_public, url, media_class, sort_order)
           VALUES (%(title_pt)s, %(title_en)s, %(desc_pt)s, %(desc_en)s, %(tags)s,
                   %(is_public)s, %(url)s, %(media_class)s, %(sort_order)s)""",
        data,
    )
    conn.commit()
    cur.close()
    conn.close()


def update_project(project_id: int, data: dict):
    data["id"] = project_id
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """UPDATE projects SET
           title_pt=%(title_pt)s, title_en=%(title_en)s, desc_pt=%(desc_pt)s, desc_en=%(desc_en)s,
           tags=%(tags)s, is_public=%(is_public)s, url=%(url)s, media_class=%(media_class)s,
           sort_order=%(sort_order)s
           WHERE id=%(id)s""",
        data,
    )
    conn.commit()
    cur.close()
    conn.close()


def delete_project(project_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM projects WHERE id = %s", (project_id,))
    conn.commit()
    cur.close()
    conn.close()
