from config import get_connection, validar_ano, validar_preco
from reporting import backup_db # Importa a função de backup do módulo de relatórios

def listar_livros():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, book_id, title, author, genre, publisher, isbn, ano_publicacao, preco, estoque FROM livros ORDER BY id")
        # Retorna uma lista de tuplas para facilitar o uso na serialização/exportação
        return [tuple(row) for row in cur.fetchall()]

def add_livro(title, author, isbn, book_id, genre, publisher, ano=None, preco=None, estoque=None):
    backup_db(reason="add_web")
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO livros (book_id, isbn, title, author, genre, publisher, ano_publicacao, preco, estoque)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (book_id.strip(), isbn.strip(), title.strip(), author.strip(), genre.strip(), publisher.strip(), ano, preco, estoque))
        conn.commit()
        return cur.lastrowid

def update_preco(livro_id, novo_preco):
    # ... (código da função update_preco, usando get_connection e backup_db)
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM livros WHERE id = ?", (livro_id,))
        if cur.fetchone() is None:
            return False
    backup_db(reason="update_web")
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE livros SET preco = ? WHERE id = ?", (novo_preco, livro_id))
        conn.commit()
        return True

def delete_livro(livro_id):
    # ... (código da função delete_livro, usando get_connection e backup_db)
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM livros WHERE id = ?", (livro_id,))
        if cur.fetchone() is None:
            return False
    backup_db(reason="delete_web")
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM livros WHERE id = ?", (livro_id,))
        conn.commit()
        return True

def search_autor(q):
    with get_connection() as conn:
        cur = conn.cursor()
        like = f"%{q}%"
        cur.execute("SELECT id, book_id, title, author, genre, publisher, isbn, ano_publicacao, preco, estoque FROM livros WHERE author LIKE ? ORDER BY id", (like,))
        return [tuple(row) for row in cur.fetchall()]