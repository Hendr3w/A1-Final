import os
import sqlite3
from pathlib import Path

# Caminhos e constantes
DB_FILE = Path("livros.db")
BACKUP_DIR = Path("backups")
BACKUP_PREFIX = "backup_"
MAX_BACKUPS_TO_KEEP = 5

# ReportLab
try:
    import reportlab
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Conexão com o banco
def get_connection():
    return sqlite3.connect(DB_FILE)

# Inicializa o banco
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela de livros
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS livros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id TEXT UNIQUE,
        isbn TEXT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        genre TEXT,
        publisher TEXT,
        ano_publicacao INTEGER,
        preco REAL,
        estoque INTEGER
    )
    """)

    # Tabela de clientes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        customer_id TEXT PRIMARY KEY,
        customer_age INTEGER,
        customer_gender TEXT,
        city TEXT
    )
    """)

    # Tabela de vendas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vendas (
        sale_id INTEGER PRIMARY KEY,
        timestamp TEXT,
        book_id TEXT,
        title TEXT,
        author TEXT,
        genre TEXT,
        publisher TEXT,
        isbn TEXT,
        quantity INTEGER,
        unit_price REAL,
        discount_pct REAL,
        discount_amount REAL,
        total_amount REAL,
        customer_id TEXT,
        customer_age INTEGER,
        customer_gender TEXT,
        city TEXT,
        payment_method TEXT,
        channel TEXT,
        promo_code TEXT,
        returned TEXT,
        rating REAL,
        stock_before INTEGER,
        stock_after INTEGER
    )
    """)

    conn.commit()
    conn.close()

# Validação de dados
def validar_ano(ano):
    try:
        ano = int(ano)
        return 0 < ano <= 2100
    except ValueError:
        return False

def validar_preco(preco):
    try:
        preco = float(preco)
        return preco >= 0
    except ValueError:
        return False
