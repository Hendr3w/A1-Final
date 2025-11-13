# app.py (Atualizado)

from flask import Flask, request, jsonify, send_file, render_template, redirect, url_for
from config import init_db
from crud import listar_livros, add_livro, update_preco, delete_livro, search_autor
from data_io import export_csv_to_memory, import_csv_file # Importa I/O de dados
from reporting import generate_html_report, generate_pdf_report # Importa geração de relatórios
import io

app = Flask(__name__, static_folder="static", template_folder="templates")


def validar_preco(preco_str):
    try:
        preco = float(preco_str)
        if preco >= 0:
            return preco
    except:
        pass
    return None




@app.route("/")
def index():
    init_db()
    return render_template("index.html")

@app.route("/api/export/csv", methods=["GET"])
def api_export_csv():
    csv_data = export_csv_to_memory()
    buffer = io.BytesIO(csv_data)
    return send_file(buffer, mimetype="text/csv", as_attachment=True, download_name="livros_exportados.csv")

@app.route("/api/books", methods=["GET"])
def api_list_books():
    from crud import listar_livros
    books = listar_livros()
    books_dict = []
    for b in books:
        books_dict.append({
            "id": b[0],
            "book_id": b[1],
            "isbn": b[2],
            "title": b[3],
            "author": b[4],
            "genre": b[5],
            "publisher": b[6],
            "ano_publicacao": b[7],
            "preco": b[8],
            "estoque": b[9]
        })
    return jsonify(books_dict)

@app.route("/api/report/html", methods=["GET"])
def api_report_html():
    html_data = generate_html_report()
    return html_data, 200, {'Content-Type': 'text/html'}

@app.route("/api/books/<int:book_id>/price", methods=["PUT"])
def api_update(book_id):
    data = request.json or {}
    preco = data.get("preco")
    preco_val = validar_preco(preco)
    if preco_val is None:
        return jsonify({"error":"Preço inválido."}), 400
    ok = update_preco(book_id, preco_val)
    if not ok:
        return jsonify({"error":"Livro não encontrado."}), 404
    return jsonify({"ok": True})


@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def api_delete(book_id):
    ok = delete_livro(book_id)
    if not ok:
        return jsonify({"error":"Livro não encontrado."}), 404
    return jsonify({"ok": True})


@app.route("/api/search", methods=["GET"])
def api_search():
    q = request.args.get("q","").strip()
    rows = search_autor(q) if q else []
    books = [{"id":r[0],"book_id":r[1],"title":r[2],"author":r[3],"genre":r[4],"publisher":r[5],"isbn":r[6],"ano_publicacao":r[7],"preco":r[8],"estoque":r[9]} for r in rows]
    return jsonify(books)

@app.route("/api/export", methods=["GET"])
def api_export():
    data = export_csv_to_memory()
    return send_file(io.BytesIO(data), as_attachment=True, download_name="livros_exportados.csv", mimetype="text/csv")

@app.route("/api/import", methods=["POST"])
def api_import():
    if "file" not in request.files:
        return jsonify({"error":"Nenhum arquivo enviado."}), 400
    f = request.files["file"]
    # Esta função agora trata a importação de 'livros', 'vendas' e 'clientes'
    inserted = import_csv_file(f.stream, f.filename)
    return jsonify({"inserted": inserted})



@app.route("/api/report/pdf", methods=["GET"])
def api_report_pdf():
    try:
        pdf_data = generate_pdf_report()
        buffer = io.BytesIO(pdf_data)
        return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name="relatorio_livros.pdf")
    except ImportError as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)