# reporting.py (Novo Módulo, focado em Relatórios)
from config import REPORTLAB_AVAILABLE
import os
import io

# Imports condicionais do ReportLab para PDF
if REPORTLAB_AVAILABLE:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    # ... (outros imports do ReportLab, se necessário)

# ---------------- HTML Report (Exemplo) ----------------

def generate_html_report():
    from crud import listar_livros
    """Gera um relatório HTML simples de todos os livros."""
    books = listar_livros() # Obtém os dados
    
    html_content = "<html><head><title>Relatório de Livros</title>"
    html_content += "<style>table, th, td {border: 1px solid black; border-collapse: collapse;}</style>"
    html_content += "</head><body><h1>Relatório de Livros Cadastrados</h1>"
    
    html_content += "<table style='width:100%'><tr>"
    # Cabeçalho da tabela (adaptado ao novo esquema)
    headers = ["ID", "Book ID", "Título", "Autor", "ISBN", "Preço", "Estoque"]
    for h in headers:
        html_content += f"<th>{h}</th>"
    html_content += "</tr>"
    
    for r in books:
        # r é uma tupla: id, book_id, title, author, genre, publisher, isbn, ano_publicacao, preco, estoque
        html_content += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[6]}</td><td>R$ {r[8]:.2f}</td><td>{r[9]}</td></tr>"
    
    html_content += "</table></body></html>"
    return html_content.encode("utf-8")


# ---------------- PDF Report (Exemplo) ----------------

def generate_pdf_report():
    from crud import listar_livros
    """Gera um relatório PDF formatado usando ReportLab."""
    if not REPORTLAB_AVAILABLE:
        raise ImportError("ReportLab não está instalado. Não é possível gerar PDF.")
        
    books = listar_livros()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=10 * mm, bottomMargin=10 * mm)
    styles = getSampleStyleSheet()
    elements = []
    
    # Título
    elements.append(Paragraph("Relatório Detalhado de Livros", styles['h1']))
    elements.append(Spacer(1, 6 * mm))
    
    # Dados da Tabela
    data = [["ID", "Book ID", "Título", "Autor", "ISBN", "Preço", "Estoque"]]
    for r in books:
        data.append([
            str(r[0]), str(r[1]), r[2], r[3], r[6] or '', f"R$ {r[8]:.2f}" if r[8] else 'N/A', str(r[9]) if r[9] is not None else 'N/A'
        ])

    table = Table(data, colWidths=[15*mm, 20*mm, 60*mm, 40*mm, 30*mm, 15*mm, 15*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (3, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    return buffer.getvalue()