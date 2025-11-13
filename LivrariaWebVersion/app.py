# app.py (Atualizado)

from flask import Flask, request, jsonify, send_file, render_template, redirect, url_for
from config import init_db
from crud import listar_livros, add_livro, update_preco, delete_livro, search_autor
from data_io import export_csv_to_memory, import_csv_file # Importa I/O de dados
from reporting import generate_html_report, generate_pdf_report # Importa geração de relatórios
import io

app = Flask(__name__, static_folder="static", template_folder="templates")

# ... (Rotas CRUD permanecem as mesmas)

# --- Rotas de I/O de Dados (do data_io.py) ---

@app.route("/api/export/csv", methods=["GET"])
def api_export_csv():
    csv_data = export_csv_to_memory()
    buffer = io.BytesIO(csv_data)
    return send_file(buffer, mimetype="text/csv", as_attachment=True, download_name="livros_exportados.csv")

@app.route("/api/import", methods=["POST"])
def api_import():
    if "file" not in request.files:
        return jsonify({"error":"Nenhum arquivo enviado."}), 400
    f = request.files["file"]
    inserted = import_csv_file(f.stream, f.filename)
    return jsonify({"inserted": inserted})


# --- Novas Rotas de Relatórios (do reporting.py) ---

@app.route("/api/report/html", methods=["GET"])
def api_report_html():
    html_data = generate_html_report()
    return html_data, 200, {'Content-Type': 'text/html'}

@app.route("/api/report/pdf", methods=["GET"])
def api_report_pdf():
    try:
        pdf_data = generate_pdf_report()
        buffer = io.BytesIO(pdf_data)
        return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name="relatorio_livros.pdf")
    except ImportError as e:
        return jsonify({"error": str(e)}), 500

# Run
if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)