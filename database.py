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

    CREATE TABLE IF NOT EXISTS posts (
        id SERIAL PRIMARY KEY,
        slug TEXT UNIQUE NOT NULL,
        title_pt TEXT NOT NULL,
        title_en TEXT NOT NULL,
        excerpt_pt TEXT NOT NULL DEFAULT '',
        excerpt_en TEXT NOT NULL DEFAULT '',
        content_pt TEXT NOT NULL,
        content_en TEXT NOT NULL,
        tag TEXT NOT NULL DEFAULT 'Python',
        published BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMP NOT NULL DEFAULT NOW()
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
             "Dashboard desktop para gestão de contratos: alertas de vencimento, mapa por estado, relatórios em PDF e sincronização com Google Sheets via Google Apps Script. Única versão desktop do portfólio, com suporte a dois bancos (PostgreSQL para uso em rede e SQLite portátil via USB). Uso interno da equipe de Contratos.",
             "Desktop dashboard for contract management: expiry alerts, state-level map, PDF reports and Google Sheets sync via Google Apps Script. The only desktop project in this portfolio, supporting two databases (PostgreSQL for networked use and a portable SQLite build). Internal use for the Contracts team.",
             "Python, PySide6, PostgreSQL, SQLite, Google Apps Script", False, "", "pm-1", 1),
            ("Sistema Administrativo (Tela Admin)", "Administrative System",
             "Painel administrativo interno com controle de usuários e permissões, usado para gestão de operações de um cliente.",
             "Internal administrative panel with user and permission management, used to run a client's operations.",
             "Python, SQLite, Backend", False, "", "pm-2", 2),
            ("Faturamento por Loja — Dashboard", "Store Revenue Dashboard",
             "Painel de faturamento consolidando 22 lojas: total geral, CMV, ticket médio, faturamento por loja, evolução mensal e ranking de vendedores.",
             "Revenue dashboard consolidating 22 stores: total revenue, CMV, average ticket, revenue by store, monthly trend and sales ranking.",
             "Excel, VBA, Power Query", False, "", "pm-3", 3),
            ("GTM Concessionária — Controle de Frota", "GTM Dealership — Fleet Control",
             "Dashboard de agendamento e manutenção veicular: status de veículos, ordens de serviço, mapa por estado e formas de pagamento.",
             "Vehicle scheduling and maintenance dashboard: vehicle status, service orders, state-level map and payment methods.",
             "Excel, VBA, Macros", False, "", "pm-4", 4),
            ("CEGM — Controle de Consumo", "CEGM — Consumption Control",
             "Painel de consumo por unidade (GTA/GTM/GTR): combustível, peças, serviços e evolução mensal por município.",
             "Per-unit consumption dashboard (GTA/GTM/GTR): fuel, parts, services and monthly trend by municipality.",
             "Excel, VBA, Macros", False, "", "pm-5", 5),
            ("MM Fashion — E-commerce", "MM Fashion — E-commerce",
             "Loja virtual completa de moda feminina: vitrine, categorias, promoções e painel administrativo com KPIs e gestão de pedidos.",
             "Full women's fashion online store: showcase, categories, promotions and an admin panel with KPIs and order management.",
             "HTML, CSS, JavaScript", True, "https://mmfashion.up.railway.app/", "pm-3", 6),
            ("Site Institucional — Advocacia", "Law Firm Website",
             "Site institucional para escritório de advocacia, com identidade visual sóbria, áreas de atuação e formulário de contato.",
             "Institutional website for a law firm, with a sober visual identity, practice areas and a contact form.",
             "HTML, CSS, JavaScript", True, "https://rogervilelaadvocacia.up.railway.app/", "pm-4", 7),
            ("Gomes Contabilidade", "Gomes Contabilidade",
             "Site institucional para escritório de contabilidade, com áreas de atuação, artigos técnicos e formulário de contato.",
             "Institutional website for an accounting firm, with practice areas, technical articles and a contact form.",
             "HTML, CSS, JavaScript", True, "https://yagohenrickgomes-web.github.io/gomescontabilidade/", "pm-5", 8),
            ("Doces Fran — Confeitaria Artesanal", "Doces Fran — Artisan Bakery",
             "Loja virtual de confeitaria artesanal, com vitrine de produtos, categorias, depoimentos e pedidos via WhatsApp.",
             "Artisan bakery online store, with product showcase, categories, testimonials and WhatsApp ordering.",
             "HTML, CSS, JavaScript", True, "https://yagohenrickgomes-web.github.io/docesdafran/", "pm-6", 9),
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


# ---------------------------------------------------------------------------
# Blog
# ---------------------------------------------------------------------------
def _slugify(text: str) -> str:
    import re
    import unicodedata
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9\s-]", "", text).strip().lower()
    text = re.sub(r"[\s-]+", "-", text)
    return text or "post"


def _unique_slug(base_slug: str, cur, exclude_id: int = None) -> str:
    slug = base_slug
    i = 2
    while True:
        if exclude_id:
            cur.execute("SELECT id FROM posts WHERE slug = %s AND id != %s", (slug, exclude_id))
        else:
            cur.execute("SELECT id FROM posts WHERE slug = %s", (slug,))
        if not cur.fetchone():
            return slug
        slug = f"{base_slug}-{i}"
        i += 1


def get_posts(published_only: bool = False, limit: int = None) -> list:
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM posts"
    if published_only:
        query += " WHERE published = TRUE"
    query += " ORDER BY created_at DESC"
    if limit:
        query += f" LIMIT {int(limit)}"
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(row) for row in rows]


def get_post(post_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(row) if row else None


def get_post_by_slug(slug: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM posts WHERE slug = %s", (slug,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(row) if row else None


def create_post(data: dict):
    conn = get_connection()
    cur = conn.cursor()
    base_slug = _slugify(data["title_pt"])
    data["slug"] = _unique_slug(base_slug, cur)
    cur.execute(
        """INSERT INTO posts
           (slug, title_pt, title_en, excerpt_pt, excerpt_en, content_pt, content_en, tag, published)
           VALUES (%(slug)s, %(title_pt)s, %(title_en)s, %(excerpt_pt)s, %(excerpt_en)s,
                   %(content_pt)s, %(content_en)s, %(tag)s, %(published)s)""",
        data,
    )
    conn.commit()
    cur.close()
    conn.close()


def update_post(post_id: int, data: dict):
    conn = get_connection()
    cur = conn.cursor()
    data["id"] = post_id
    cur.execute(
        """UPDATE posts SET
           title_pt=%(title_pt)s, title_en=%(title_en)s, excerpt_pt=%(excerpt_pt)s, excerpt_en=%(excerpt_en)s,
           content_pt=%(content_pt)s, content_en=%(content_en)s, tag=%(tag)s, published=%(published)s
           WHERE id=%(id)s""",
        data,
    )
    conn.commit()
    cur.close()
    conn.close()


def delete_post(post_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM posts WHERE id = %s", (post_id,))
    conn.commit()
    cur.close()
    conn.close()
