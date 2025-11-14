import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt


from src.preprocessing import clean_dataset

matplotlib.use("Agg")

PLOT_DIR = "static/plots/"


def save_plot(fig, name):
    """Salva gráfico no diretório de plots."""
    os.makedirs(PLOT_DIR, exist_ok=True)
    path = os.path.join(PLOT_DIR, name)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def visualize_dataset(df, filename):
    
    df = clean_dataset(df)

    plots = []

    # --------------------
    # 1. Distribuição de Preços
    # --------------------
    if "final_price" in df.columns:
        fig = plt.figure(figsize=(6, 4))
        plt.hist(df["final_price"], bins=20)
        plt.title("Distribuição de Preços")
        plt.xlabel("Preço")
        plt.ylabel("Quantidade")
        plots.append(save_plot(fig, f"{filename}_price_dist.png"))

    # --------------------
    # 2. Distribuição de Ratings
    # --------------------
    if "rating_clean" in df.columns:
        fig = plt.figure(figsize=(6, 4))
        plt.hist(df["rating_clean"], bins=20)
        plt.title("Distribuição de Ratings")
        plt.xlabel("Nota")
        plt.ylabel("Quantidade")
        plots.append(save_plot(fig, f"{filename}_rating_dist.png"))

    # --------------------
    # 3. Top livros por reviews
    # --------------------
    if "reviews_count" in df.columns and "title" in df.columns:
        fig = plt.figure(figsize=(8, 5))
        top10 = df.sort_values("reviews_count", ascending=False).head(10)
        plt.barh(top10["title"], top10["reviews_count"])
        plt.title("Top 10 Livros por Reviews")
        plt.xlabel("Reviews")
        plt.ylabel("Livro")
        plt.gca().invert_yaxis()
        plots.append(save_plot(fig, f"{filename}_top_reviews.png"))

    # --------------------
    # 4. Contagem de Categorias
    # --------------------
    if "main_category" in df.columns:
        fig = plt.figure(figsize=(7, 4))
        df["main_category"].value_counts().head(10).plot(kind="bar")
        plt.title("Categorias Mais Frequentes")
        plt.xlabel("Categoria")
        plt.ylabel("Quantidade")
        plots.append(save_plot(fig, f"{filename}_categories.png"))

    # --------------------
    # 5. Relação Preço x Reviews
    # --------------------
    if "final_price" in df.columns and "reviews_count" in df.columns:
        fig = plt.figure(figsize=(6, 4))
        plt.scatter(df["final_price"], df["reviews_count"])
        plt.title("Preço x Reviews")
        plt.xlabel("Preço")
        plt.ylabel("Reviews")
        plots.append(save_plot(fig, f"{filename}_price_reviews.png"))

    # --------------------
    # 6. Relação Rating x Reviews
    # --------------------
    if "rating_clean" in df.columns and "reviews_count" in df.columns:
        fig = plt.figure(figsize=(6, 4))
        plt.scatter(df["rating_clean"], df["reviews_count"])
        plt.title("Rating x Reviews")
        plt.xlabel("Rating")
        plt.ylabel("Reviews")
        plots.append(save_plot(fig, f"{filename}_rating_reviews.png"))

    return plots
