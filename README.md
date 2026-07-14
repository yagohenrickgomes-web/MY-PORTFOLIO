# Portfólio — Yago Henrick Alves Gomes

Site em **Python (FastAPI) + PostgreSQL**, com painel administrativo pra
editar conteúdo sem mexer em código.

## Estrutura

```
MY PORTFOLIO/
├── app.py                 -> aplicação FastAPI (rotas públicas + admin)
├── database.py             -> acesso ao banco PostgreSQL
├── requirements.txt
├── Procfile                -> comando de start (usado pelo Railway)
├── .env.example             -> modelo de variáveis de ambiente
├── .gitignore
├── templates/
│   ├── index.html           -> site público (Jinja2)
│   ├── admin_login.html
│   └── admin_dashboard.html
└── static/
    ├── style.css
    └── script.js
```

## Como rodar localmente (Windows / CMD)

1. Você precisa ter o **PostgreSQL instalado e rodando** localmente (você já
   usa isso nos outros projetos, tipo o Contratos SagaCap).

2. Crie um banco vazio pro portfólio, por exemplo `portfolio`:
```bat
psql -U postgres -c "CREATE DATABASE portfolio;"
```

3. Crie o ambiente virtual dentro da pasta do projeto:
```bat
python -m venv .venv
.venv\Scripts\activate
```

4. Instale as dependências:
```bat
pip install -r requirements.txt
```

5. Copie `.env.example` para `.env` e preencha com sua senha real do Postgres:
```bat
copy .env.example .env
notepad .env
```

6. Rode o servidor:
```bat
python -m uvicorn app:app --reload
```

7. Acesse:
- Site público: http://127.0.0.1:8000
- Painel admin: http://127.0.0.1:8000/admin/login

## Login padrão do admin

```
usuário: admin
senha:   admin123
```

**Troque essa senha assim que entrar** — tem um campo "Conta" dentro do
próprio painel admin pra isso.

## O que dá pra editar pelo painel admin

- **Conteúdo**: cargo/subtítulo do Hero, os 3 parágrafos de "Sobre Mim",
  e-mail de contato, LinkedIn e GitHub.
- **Projetos**: adicionar, editar e excluir. Cada projeto tem um campo
  "público" — quando marcado, o card vira link real (abre a URL cadastrada
  em nova aba); quando desmarcado, o card mostra apenas um preview (sem
  link real), pra não expor sistemas internos de empresas/clientes.
- **Conta**: trocar a senha do admin.

As demais seções do site (Serviços, Tecnologias, Experiência, Formação,
Certificações, Processo, Depoimentos, Blog) ainda estão fixas no template
`index.html` — dá pra tornar editáveis também, seção por seção, quando você
quiser.

## Banco de dados

O PostgreSQL é criado/populado automaticamente na primeira vez que você roda
o servidor (a função `init_db()` cria as tabelas e insere os dados padrão se
estiverem vazias). Não precisa rodar nenhum script de migração à parte.

## Segurança

- Senha do admin fica salva com hash PBKDF2 (nunca em texto puro).
- O painel `/admin` é protegido por sessão — sem login, redireciona pro
  login automaticamente.
- Páginas de admin têm `robots: noindex, nofollow`, então não aparecem em
  buscadores.
- O arquivo `.env` (com a senha do banco) nunca é commitado no Git — já
  está no `.gitignore`.

## Deploy no Railway

Veja o guia completo enviado no chat. Resumo rápido:
1. Suba o projeto pro GitHub (sem o `.env`, ele fica de fora automaticamente).
2. No Railway, crie um projeto novo a partir do repositório.
3. Adicione o addon **PostgreSQL** do próprio Railway.
4. Configure as variáveis de ambiente do serviço web: `DATABASE_URL`
   (referenciando o Postgres do Railway) e `SECRET_KEY` (gere uma nova).
5. O Railway detecta o `Procfile` e sobe o site sozinho.

