import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.impute import SimpleImputer

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

def train_price_model(df: pd.DataFrame, model_type="rf"):
    """
    Treina um modelo para prever preço.
    model_type: 'rf' = RandomForest, 'lr' = LinearRegression
    """
    df = df.copy()
    df = df[df["final_price"].notna()]

    # Features
    features = ["rating_clean", "reviews_count", "answered_questions",
                "images_count", "discount", "main_category", "brand"]
    X = df[features]
    y = df["final_price"]

    # Separar colunas numéricas e categóricas
    numeric_features = ["rating_clean", "reviews_count", "answered_questions",
                        "images_count", "discount"]
    categorical_features = ["main_category", "brand"]

    # Transformadores
    numeric_transformer = SimpleImputer(strategy="median")
    categorical_transformer = OneHotEncoder(handle_unknown="ignore")

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features)
        ]
    )

    # Modelo
    if model_type == "rf":
        model = RandomForestRegressor(n_estimators=300, random_state=42)
    else:
        model = LinearRegression()

    pipeline = Pipeline(steps=[("preprocessor", preprocessor),
                               ("regressor", model)])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipeline.fit(X_train, y_train)
    score = pipeline.score(X_test, y_test)

    # Salvar modelo
    joblib.dump(pipeline, f"{MODEL_DIR}/price_model_{model_type}.pkl")

    return score

def load_price_model(model_type="rf"):
    path = f"{MODEL_DIR}/price_model_{model_type}.pkl"
    return joblib.load(path)

def predict_price(model, input_dict):
    """
    input_dict: dict com keys iguais às features usadas no treino
    """
    df = pd.DataFrame([input_dict])
    pred = model.predict(df)[0]
    return pred
