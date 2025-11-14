from flask import Flask, render_template, request, redirect
import os
import pandas as pd

from src.preprocessing import load_data, clean_dataset
from src.visualization import visualize_dataset
from src.modeling import train_rating_model
from src.preprocessing import clean_dataset
from src.ml.price_model import train_price_model, load_price_model, predict_price


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "data/uploaded/"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]
    if file.filename == "":
        return redirect("/")

    path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(path)

    return redirect(f"/preview?file={file.filename}")


@app.route("/analyze")
def analyze():
    filename = request.args.get("file")
    if not filename:
        return "Arquivo não informado", 400

    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    df = pd.read_csv(path)

    from src.visualization import visualize_dataset
    plots = visualize_dataset(df, filename)

    return render_template("analysis.html", plots=plots, filename=filename)


@app.route("/preview")
def preview():
    filename = request.args.get("file")
    if not filename:
        return "Arquivo não informado", 400

    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    df = pd.read_csv(path)

    columns_to_show = [
        "title",
        "final_price",
        "rating",
        "reviews_count",
        "timestamp",
        "categories",
        "best_sellers_rank"
    ]

    df_filtered = df[[col for col in columns_to_show if col in df.columns]]

    html_table = df_filtered.to_html(classes="table table-striped table-bordered", index=False)

    return render_template("preview.html", 
                           table=html_table,
                           filename=filename)

@app.route("/ml")
def ml_home():
    filename = request.args.get("file")

    return render_template("ml_home.html", filename=filename)

from src.ml.price_model import train_price_model, load_price_model, predict_price

@app.route("/train_price")
def train_price():
    filename = request.args.get("file")
    if not filename:
        return "Arquivo não informado", 400

    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    df = pd.read_csv(path)
    df = clean_dataset(df)

    model_type = request.args.get("model", "rf") 
    score = train_price_model(df, model_type=model_type)
    return f"Modelo de preço ({model_type}) treinado! R² score: {score:.3f}"


@app.route("/predict_price", methods=["GET"])
def predict_price_form():
    filename = request.args.get("file")
    categories = []
    brands = []
    if filename:
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        if os.path.exists(path):
            df = pd.read_csv(path)
            df = clean_dataset(df)
            if "main_category" in df.columns:
                categories = sorted(df["main_category"].dropna().unique().tolist())
            if "brand" in df.columns:
                brands = sorted(df["brand"].dropna().unique().tolist())

    return render_template("predict_price_form.html",
                           filename=filename,
                           categories=categories,
                           brands=brands)


@app.route("/predict_price", methods=["POST"])
def predict_price_submit():
    model_type = request.form.get("model_choice", "rf")
    try:
        model = load_price_model(model_type)
    except Exception as e:
        return f"Erro carregando modelo: {e}", 500

    input_dict = {
        "rating_clean": float(request.form.get("rating_clean", 0)),
        "reviews_count": float(request.form.get("reviews_count", 0)),
        "answered_questions": float(request.form.get("answered_questions", 0)),
        "images_count": float(request.form.get("images_count", 0)),
        "discount": float(request.form.get("discount", 0)),
        "main_category": request.form.get("main_category", "UNKNOWN"),
        "brand": request.form.get("brand", "UNKNOWN")
    }

    pred = predict_price(model, input_dict)
    return render_template("predict_price_result.html",
                           input=input_dict, price=pred)



if __name__ == "__main__":
    app.run(debug=True)
