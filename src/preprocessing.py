import ast
import pandas as pd


def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def clean_rating(rating_str: str):
    if not isinstance(rating_str, str):
        return None
    try:
        return float(rating_str.split(" ")[0])
    except:
        return None


def clean_categories(categories_str: str):
    try:
        parsed = ast.literal_eval(categories_str)
        if isinstance(parsed, list):
            return parsed
    except:
        pass
    return []


def clean_best_sellers(best_str: str):
    try:
        parsed = ast.literal_eval(best_str)
        if isinstance(parsed, list):
            return parsed
    except:
        pass
    return []

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()

    # 1. Limpeza do Rating
    cleaned["rating_clean"] = cleaned["rating"].apply(clean_rating)

    # 2. Limpeza de Categorias
    cleaned["categories_list"] = cleaned["categories"].apply(clean_categories)

    # Remove "Books" (já que todos têm)
    def remove_books_category(categories):
        if not isinstance(categories, list):
            return []
        return [c for c in categories if c != "Books"]

    cleaned["categories_clean"] = cleaned["categories_list"].apply(remove_books_category)

    # Categoria principal útil (primeira depois de remover "Books")
    cleaned["main_category"] = cleaned["categories_clean"].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
    )

    # 3. Limpeza de Best Sellers
    cleaned["best_sellers_list"] = cleaned["best_sellers_rank"].apply(clean_best_sellers)

    return cleaned
