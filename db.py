import os
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd() / "meu_sistema_livraria"
DATA_DIR = ROOT / "data"
BACKUP_DIR = ROOT / "backups"
EXPORT_DIR = ROOT / "exports"
DB_FILE = DATA_DIR / "livraria.db"
BACKUP_PREFIX = "backup_livraria_"
MAX_BACKUPS_TO_KEEP = 5


def ensure_directories():
    for p in (ROOT, DATA_DIR, BACKUP_DIR, EXPORT_DIR):
        os.makedirs(p, exist_ok=True)


def init_db():
    ensure_directories()
    with sqlite3.connect(str(DB_FILE)) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS livros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                autor TEXT NOT NULL,
                ano_publicacao INTEGER,
                preco REAL
            )
        """)
        conn.commit()


def get_connection():
    if not DB_FILE.exists():
        init_db()
    return sqlite3.connect(str(DB_FILE))


def backup_db():
    ensure_directories()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_name = f"{BACKUP_PREFIX}{timestamp}.db"
    backup_path = BACKUP_DIR / backup_name

    try:
        shutil.copy2(DB_FILE, backup_path)
    except FileNotFoundError:
        pass

    prune_old_backups()
    return backup_path


def prune_old_backups():
    backups = sorted(BACKUP_DIR.glob(
        f"{BACKUP_PREFIX}*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
    for old in backups[MAX_BACKUPS_TO_KEEP:]:
        try:
            old.unlink()
        except Exception:
            pass


def listar_livros():
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT id, titulo, autor, ano_publicacao, preco FROM livros ORDER BY id")
        return [dict(row) for row in cur.fetchall()]


def buscar_por_autor(autor_query):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        like = f"%{autor_query.strip()}%"
        cur.execute(
            "SELECT id, titulo, autor, ano_publicacao, preco FROM livros WHERE autor LIKE ? ORDER BY id", (like,))
        return [dict(row) for row in cur.fetchall()]


def adicionar_livro(titulo, autor, ano_publicacao, preco):
    backup_db()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO livros (titulo, autor, ano_publicacao, preco) VALUES (?, ?, ?, ?)",
                    (titulo.strip(), autor.strip(), ano_publicacao, preco))
        conn.commit()
        return cur.lastrowid


def remover_livro(livro_id):
    backup_db()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM livros WHERE id = ?", (livro_id,))
        conn.commit()
        return cur.rowcount > 0


def atualizar_preco_livro(livro_id, novo_preco):
    backup_db()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE livros SET preco = ? WHERE id = ?",
                    (novo_preco, livro_id))
        conn.commit()


def remover_todos_livros():
    backup_db()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM livros")
        conn.commit()
        return cur.rowcount > 0
