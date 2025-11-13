import csv
import sqlite3
from config import get_connection, validar_ano, validar_preco, init_db

def import_csv_to_db(livros_path=None, clientes_path=None, vendas_path=None):
    init_db()  # garante que as tabelas existam

    conn = get_connection()
    cur = conn.cursor()
    inserted_counts = {"livros": 0, "clientes": 0, "vendas": 0}

    # ---------------- Livros ----------------
    if livros_path:
        with open(livros_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                try:
                    ano = int(r.get("ano_publicacao") or 0) if validar_ano(r.get("ano_publicacao")) else None
                    preco = float(r.get("preco") or 0) if validar_preco(r.get("preco")) else None
                    estoque = int(r.get("estoque") or 0)
                    cur.execute("""
                        INSERT OR IGNORE INTO livros 
                        (book_id, isbn, title, author, genre, publisher, ano_publicacao, preco, estoque)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        r.get("book_id"), r.get("isbn"), r.get("title"), r.get("author"),
                        r.get("genre"), r.get("publisher"), ano, preco, estoque
                    ))
                    inserted_counts["livros"] += 1
                except Exception as e:
                    print(f"Erro ao inserir livro {r.get('title')}: {e}")

    # ---------------- Clientes ----------------
    if clientes_path:
        with open(clientes_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                try:
                    cur.execute("""
                        INSERT OR REPLACE INTO clientes 
                        (customer_id, customer_age, customer_gender, city)
                        VALUES (?, ?, ?, ?)
                    """, (
                        r.get("customer_id"), int(r.get("customer_age") or 0),
                        r.get("customer_gender"), r.get("city")
                    ))
                    inserted_counts["clientes"] += 1
                except Exception as e:
                    print(f"Erro ao inserir cliente {r.get('customer_id')}: {e}")

    # ---------------- Vendas ----------------
    if vendas_path:
        with open(vendas_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                try:
                    cur.execute("""
                        INSERT OR IGNORE INTO vendas
                        (sale_id, timestamp, book_id, title, author, genre, publisher, isbn, quantity,
                         unit_price, discount_pct, discount_amount, total_amount, customer_id, customer_age,
                         customer_gender, city, payment_method, channel, promo_code, returned, rating,
                         stock_before, stock_after)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        int(r.get("sale_id") or 0), r.get("timestamp"), r.get("book_id"), r.get("title"),
                        r.get("author"), r.get("genre"), r.get("publisher"), r.get("isbn"),
                        int(r.get("quantity") or 0), float(r.get("unit_price") or 0),
                        float(r.get("discount_pct") or 0), float(r.get("discount_amount") or 0),
                        float(r.get("total_amount") or 0), r.get("customer_id"),
                        int(r.get("customer_age") or 0), r.get("customer_gender"), r.get("city"),
                        r.get("payment_method"), r.get("channel"), r.get("promo_code"),
                        r.get("returned"), float(r.get("rating") or 0),
                        int(r.get("stock_before") or 0), int(r.get("stock_after") or 0)
                    ))
                    inserted_counts["vendas"] += 1
                except Exception as e:
                    print(f"Erro ao inserir venda {r.get('sale_id')}: {e}")

    conn.commit()
    conn.close()
    return inserted_counts


counts = import_csv_to_db(
    livros_path="livros.csv",
    clientes_path="clientes.csv",
    vendas_path="data.csv"
)

print("Registros inseridos:", counts)
