from config import get_connection, BACKUP_DIR, DB_FILE, BACKUP_PREFIX, MAX_BACKUPS_TO_KEEP, validar_ano, validar_preco, init_db
import shutil
import time
from datetime import datetime
import csv
import io
import sqlite3

# ---------------- Backups ----------------


def backup_db(reason="manual"):
    # Garante que o DB existe antes de copiar
    if not DB_FILE.exists():
        init_db()
        time.sleep(0.05)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    name = f"{BACKUP_PREFIX}{ts}.db"
    path = BACKUP_DIR / name
    shutil.copy2(DB_FILE, path)
    prune_old_backups()
    return str(path)


def prune_old_backups():
    files = sorted(BACKUP_DIR.glob(f"{BACKUP_PREFIX}*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
    for old in files[MAX_BACKUPS_TO_KEEP:]:
        try:
            old.unlink()
        except:
            pass

# ---------------- CSV ----------------


def detect_delimiter(sample_line):
    return "," if sample_line.count(",") >= sample_line.count(";") else ";"


def export_csv_to_memory():
    from crud import listar_livros
    rows = listar_livros()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "book_id", "title", "author", "genre", "publisher", "isbn", "ano_publicacao", "preco", "estoque"])
    for _id, book_id, title, author, genre, publisher, isbn, ano, preco, estoque in rows:
        writer.writerow([_id, book_id or '', title, author, genre or '', publisher or '', isbn or '', ano or '', preco or '', estoque or ''])
    return output.getvalue().encode("utf-8")


def import_csv_file(file_stream, filename):
    # A lógica completa de importação para livros, vendas e clientes permanece aqui,
    # incluindo as chamadas a validar_ano e validar_preco
    # ... (código da função import_csv_file original, adaptado para importar 'backup_db')
    text = file_stream.read().decode("utf-8")
    lines = text.splitlines()
    if not lines:
        return 0

    delim = detect_delimiter(lines[0])

    reader = csv.DictReader(io.StringIO(text), delimiter=delim)
    rows = list(reader)
    if not rows:
        return 0

    fieldnames = [f.lower() for f in reader.fieldnames]

    is_vendas = 'sale_id' in fieldnames and 'total_amount' in fieldnames
    is_livros = 'isbn' in fieldnames and 'title' in fieldnames and 'author' in fieldnames

    if not is_vendas and not is_livros:
        return 0

    backup_db(reason="import_web")
    inserted = 0
    with get_connection() as conn:
        cur = conn.cursor()

        if is_vendas:
             # Lógica de importação VENDAS e CLIENTES
             # ... (código de vendas e clientes) ...
             vendas_cols = [
                 'sale_id', 'timestamp', 'book_id', 'title', 'author', 'genre', 'publisher', 'isbn',
                 'quantity', 'unit_price', 'discount_pct', 'discount_amount', 'total_amount',
                 'customer_id', 'customer_age', 'customer_gender', 'city', 'payment_method',
                 'channel', 'promo_code', 'returned', 'rating', 'stock_before', 'stock_after'
             ]
             insert_vendas_sql = f"INSERT INTO vendas ({', '.join(vendas_cols)}) VALUES ({', '.join('?' * len(vendas_cols))})"

             insert_clientes_sql = """
                 INSERT OR REPLACE INTO clientes (customer_id, customer_age, customer_gender, city)
                 VALUES (?, ?, ?, ?)
             """

             for r in rows:
                 try:
                     row_data = {k.lower(): v for k, v in r.items()}

                     customer_id = row_data.get('customer_id') or None
                     if customer_id:
                         cliente_data = [
                             customer_id,
                             int(row_data.get('customer_age') or 0),
                             row_data.get('customer_gender') or None,
                             row_data.get('city') or None
                         ]
                         cur.execute(insert_clientes_sql, cliente_data)

                     data = [
                         int(row_data.get('sale_id') or 0),
                         row_data.get('timestamp') or None,
                         row_data.get('book_id') or None,
                         row_data.get('title') or None,
                         row_data.get('author') or None,
                         row_data.get('genre') or None,
                         row_data.get('publisher') or None,
                         row_data.get('isbn') or None,
                         int(row_data.get('quantity') or 0),
                         float(row_data.get('unit_price') or 0.0),
                         float(row_data.get('discount_pct') or 0.0),
                         float(row_data.get('discount_amount') or 0.0),
                         float(row_data.get('total_amount') or 0.0),
                         customer_id,
                         int(row_data.get('customer_age') or 0),
                         row_data.get('customer_gender') or None,
                         row_data.get('city') or None,
                         row_data.get('payment_method') or None,
                         row_data.get('channel') or None,
                         row_data.get('promo_code') or None,
                         row_data.get('returned') or 'False',
                         float(row_data.get('rating') or 0.0),
                         int(row_data.get('stock_before') or 0),
                         int(row_data.get('stock_after') or 0)
                     ]

                     if data[1] is None or data[0] == 0:
                         continue

                     cur.execute(insert_vendas_sql, data)
                     inserted += 1
                 except (ValueError, sqlite3.IntegrityError):
                     pass
        elif is_livros:
            # Lógica de importação LIVROS
            for r in rows:
                book_id = r.get("book_id") or ""
                isbn = r.get("isbn") or ""
                title = (r.get("title") or r.get("titulo") or "").strip()
                author = (r.get("author") or r.get("autor") or "").strip()
                genre = r.get("genre") or ""
                publisher = r.get("publisher") or ""
                ano_raw = r.get("ano_publicacao") or r.get("year") or ""
                preco_raw = r.get("preco") or r.get("price") or ""
                estoque_raw = r.get("estoque") or r.get("stock") or ""

                ano = validar_ano(ano_raw) if ano_raw != "" else None
                preco = validar_preco(preco_raw) if preco_raw != "" else None
                estoque = int(estoque_raw) if estoque_raw.isdigit() else None

                if title and author and book_id and isbn:
                    try:
                        cur.execute("""
                            INSERT INTO livros (book_id, isbn, title, author, genre, publisher, ano_publicacao, preco, estoque)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (book_id, isbn, title, author, genre, publisher, ano, preco, estoque))
                        inserted += 1
                    except sqlite3.IntegrityError:
                        pass
        conn.commit()
    return inserted
