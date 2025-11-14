import csv
from datetime import datetime
from io import StringIO, BytesIO
from flask import Flask, request, jsonify, send_file, render_template

# Importações para ReportLab (Geração de PDF)
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

import db


def validar_ano(ano_str):
    try:
        if not ano_str:
            return None
        ano = int(ano_str)
        if 1000 <= ano <= datetime.now().year + 1:
            return ano
    except:
        pass
    return None


def validar_preco(preco_str):
    """Valida e converte a string de preço para float, aceitando , ou ."""
    try:
        if not preco_str:
            return None
        # Substitui a vírgula por ponto para o float() funcionar
        preco = float(str(preco_str).strip().replace(',', '.'))
        if preco >= 0:
            return preco
    except:
        pass
    return None


def exportar_para_csv():
    """Exporta os dados da tabela para CSV em memória e retorna um stream binário (BytesIO)."""
    livros = db.listar_livros()
    si = StringIO()  # Usamos StringIO para escrever o CSV como texto
    writer = csv.writer(si)
    writer.writerow(["id", "titulo", "autor", "ano_publicacao", "preco"])
    for livro in livros:
        # Garante que o preço saia com ponto decimal para importação universal
        preco_csv = f"{livro['preco']:.2f}" if (
            livro['preco'] is not None) else ""
        writer.writerow([livro['id'], livro['titulo'], livro['autor'],
                        livro['ano_publicacao'] or "", preco_csv])
    si.seek(0)

    # CONVERSÃO ESSENCIAL: Converte o conteúdo de texto (StringIO) para binário (BytesIO)
    csv_data_bytes = si.getvalue().encode('utf-8')
    buffer = BytesIO(csv_data_bytes)
    buffer.seek(0)

    return buffer  # Retorna o objeto BytesIO (BINÁRIO)


def importar_de_csv_from_memory(file_storage):
    inserted = 0
    stream = file_storage.stream.read().decode("utf-8")
    reader = csv.DictReader(StringIO(stream))
    rows = list(reader)
    if not rows:
        return 0
    db.backup_db()
    with db.get_connection() as conn:
        cur = conn.cursor()
        for r in rows:
            titulo = r.get("titulo") or r.get("title") or ""
            autor = r.get("autor") or r.get("author") or ""
            ano_raw = r.get("ano_publicacao") or r.get(
                "Ano") or r.get("year") or ""
            preco_raw = r.get("preco") or r.get(
                "Preço") or r.get("price") or ""

            # Validação usa a função que aceita vírgula ou ponto
            ano = validar_ano(ano_raw.strip())
            preco = validar_preco(preco_raw.strip())

            db.adicionar_livro(titulo.strip(), autor.strip(), ano, preco)
            inserted += 1
        conn.commit()
    return inserted


def gerar_relatorio_html():
    """
    Gera o relatório HTML em memória e converte o conteúdo de texto para BytesIO.
    """
    livros = db.listar_livros()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_content = [
        "<!doctype html>",
        "<html><head><meta charset='utf-8'><title>Relatório de Livros</title>",
        "<style>body{font-family:Arial,sans-serif;}table{border-collapse:collapse;width:80%;margin:20px auto;}th,td{border:1px solid #ccc;padding:10px;text-align:left;}thead{background-color:#003366;color:white;}</style>",
        "</head><body>",
        f"<h1>Relatório de Livros - Livraria Aoros</h1><p style='text-align:center;'>Gerado em {
            now}</p>",
        "<table><thead><tr><th style='width:5%; text-align:center;'>ID</th><th style='width:35%'>Título</th><th style='width:30%'>Autor</th><th style='width:10%; text-align:center;'>Ano</th><th style='width:20%; text-align:right;'>Preço</th></tr></thead><tbody>"
    ]
    total_livros = len(livros)

    for livro in livros:
        # Formata o preço no padrão BRL para o relatório HTML
        preco_str = f"R$ {livro['preco']:,.2f}".replace(",", "X").replace(
            ".", ",").replace("X", ".") if (livro['preco'] is not None) else 'N/A'
        html_content.append(f"<tr><td style='text-align:center;'>{livro['id']}</td><td>{livro['titulo']}</td><td>{
                            livro['autor']}</td><td style='text-align:center;'>{livro['ano_publicacao'] or ''}</td><td style='text-align:right;'>{preco_str}</td></tr>")

    html_content.append("</tbody></table>")
    html_content.append(
        f"<p style='text-align:center; margin-top: 20px;'>Total de Registros: {total_livros}</p>")
    html_content.append("</body></html>")

    final_html = "\n".join(html_content)

    # CONVERSÃO PARA BINÁRIO:
    html_data_bytes = final_html.encode('utf-8')
    buffer = BytesIO(html_data_bytes)
    buffer.seek(0)
    return buffer  # Retorna o objeto BytesIO (BINÁRIO)


def gerar_relatorio_pdf():
    livros = db.listar_livros()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Função para formatar o preço em BRL para o PDF
    def formatar_preco_brl(preco):
        if preco is not None:
            # Garante a formatação BRL correta no PDF
            return "R$ " + f"{preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return 'N/A'

    # 1. Título
    elements.append(
        Paragraph("Relatório de Livros da Livraria Aoros", styles['h1']))
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime(
        '%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 0.4 * inch))

    # 2. Tabela de Dados
    data = [["ID", "Título", "Autor", "Ano", "Preço"]]

    for livro in livros:
        preco_str = formatar_preco_brl(livro['preco'])

        data.append([
            str(livro['id']),
            str(livro['titulo']),
            str(livro['autor']),
            str(livro['ano_publicacao'] or ''),
            preco_str
        ])

    table = Table(data, colWidths=[
                  0.5*inch, 2.5*inch, 2*inch, 0.7*inch, 1*inch])

    # 3. Estilo da Tabela
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Alinha coluna ID ao centro
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Alinha coluna Ano ao centro
        ('ALIGN', (4, 1), (4, -1), 'RIGHT'),  # Alinha coluna Preço à direita
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
    ])

    table.setStyle(style)
    elements.append(table)

    # 4. Total de Registros
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(f"Total de Livros Cadastrados: {
                    len(livros)}", styles['h3']))

    doc.build(elements)
    buffer.seek(0)
    return buffer


db.init_db()

app = Flask(__name__, static_folder='static', template_folder='templates')


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/api/books", methods=["GET", "POST"])
def api_books():
    if request.method == "GET":
        livros = db.listar_livros()
        return jsonify(livros)

    elif request.method == "POST":
        data = request.json
        titulo = data.get("titulo")
        autor = data.get("autor")
        ano_raw = data.get("ano_publicacao", "")
        preco_raw = data.get("preco", "")

        if not titulo or not autor:
            return jsonify({"error": "Título e Autor são obrigatórios"}), 400

        ano = validar_ano(ano_raw)
        if ano_raw and ano is None:
            return jsonify({"error": "Ano de publicação inválido"}), 400

        preco = validar_preco(preco_raw)
        if preco_raw and preco is None:
            return jsonify({"error": "Preço inválido (deve ser um número não negativo)"}), 400

        try:
            livro_id = db.adicionar_livro(titulo, autor, ano, preco)
            return jsonify({"success": True, "id": livro_id}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def api_delete_book(book_id):
    if db.remover_livro(book_id):
        return jsonify({"success": True})
    return jsonify({"error": "Livro não encontrado"}), 404


@app.route("/api/books/<int:book_id>/price", methods=["PUT"])
def api_update_price(book_id):
    data = request.json
    preco_raw = data.get("preco")
    novo_preco = validar_preco(preco_raw)

    if novo_preco is None:
        return jsonify({"error": "Preço inválido"}), 400

    if db.atualizar_preco_livro(book_id, novo_preco):
        return jsonify({"success": True})
    return jsonify({"error": "Livro não encontrado"}), 404


@app.route("/api/search")
def api_search():
    query = request.args.get("q", "")
    if not query:
        return jsonify(db.listar_livros())

    resultados = db.buscar_por_autor(query)
    return jsonify(resultados)


@app.route("/api/export")
def api_export():
    csv_in_memory = exportar_para_csv()
    return send_file(
        csv_in_memory,
        mimetype='text/csv',
        download_name='livros_exportados.csv',
        as_attachment=True
    )


@app.route("/api/import", methods=["POST"])
def api_import():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nome do arquivo inválido"}), 400

    try:
        inserted = importar_de_csv_from_memory(file)
        return jsonify({"success": True, "inserted": inserted})
    except Exception as e:
        return jsonify({"error": f"Erro ao importar CSV: {e}"}), 500


@app.route("/api/backup")
def api_backup():
    try:
        backup_path = db.backup_db()
        return jsonify({"success": True, "backup": backup_path.name})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/report/html")
def api_report_html():
    html_in_memory = gerar_relatorio_html()

    return send_file(
        html_in_memory,
        mimetype='text/html',
        download_name='relatorio_livros.html',
        as_attachment=True
    )


@app.route("/api/report/pdf")
def api_report_pdf():
    pdf_buffer = gerar_relatorio_pdf()

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        download_name='relatorio_livros.pdf',
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)
