import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from prophet import Prophet
import seaborn as sns
import sqlite3

#---------- 1 - Carregar Dados ----------

import pandas as pd
import sqlite3

# Caminho para o banco
DB_FILE = "livros.db"

# Conexão com o banco
conn = sqlite3.connect(DB_FILE)

# Query para pegar todos os dados da tabela vendas
query = "SELECT * FROM vendas"

# Carrega os dados em um DataFrame
df = pd.read_sql_query(query, conn)

# Fecha a conexão
conn.close()

# Exibe os primeiros registros
print(df.head())

# Info do DataFrame
print("Info")
print(df.info())

#---------- Tratamentos ----------

df['timestamp'] = pd.to_datetime(df['timestamp'])
df['total_amount'] = pd.to_numeric(df['total_amount'])

#---------- Período ----------
#print("\nPeríodo de vendas:", df['timestamp'].min(), "->", df['timestamp'].max())
#Período de vendas: 2023-11-14 01:49:12 -> 2025-11-12 23:38:08

#---------- 2 - Análise ----------

#---------- Agregar vendas por ano/mês ----------
df['year_month'] = df['timestamp'].dt.to_period("M")

monthly_sales = df.groupby('year_month')['total_amount'].sum().reset_index()

monthly_sales['year_month'] = monthly_sales['year_month'].dt.to_timestamp()

primeiro_mes = monthly_sales['year_month'].min()
ultimo_mes = monthly_sales['year_month'].max()

primeiro_mes_total = monthly_sales.loc[monthly_sales['year_month'] == primeiro_mes, 'total_amount'].values[0]
ultimo_mes_total = monthly_sales.loc[monthly_sales['year_month'] == ultimo_mes, 'total_amount'].values[0]

monthly_sales = monthly_sales[
    (monthly_sales['year_month'] > primeiro_mes) &
    (monthly_sales['year_month'] < ultimo_mes)
]

print(monthly_sales.head())
print(monthly_sales.tail())


#Plot
plt.figure(figsize=(10, 5))
plt.plot(monthly_sales['year_month'], monthly_sales['total_amount'], marker='o')
plt.title("Evolução das Vendas Mensais")
plt.xlabel("Mês")
plt.ylabel("Total de Vendas (R$)")
plt.grid(True)
plt.tight_layout()
plt.show()


#---------- 3 - Modelo de Previsão (Regressão simples) ----------

monthly_sales = monthly_sales.sort_values('year_month')
monthly_sales['month_number'] = np.arange(len(monthly_sales))

# Variáveis de Treino
X = monthly_sales[['month_number']]
y = monthly_sales['total_amount']

# Treinar modelo e fazer previsões
model = LinearRegression()
model.fit(X, y)

monthly_sales['predicted'] = model.predict(X)

future_months = 6 # Seis mêses de previsão. 
last_month_num = monthly_sales['month_number'].max()
future_X = np.arange(last_month_num + 1, last_month_num + future_months + 1).reshape(-1, 1)
future_preds = model.predict(future_X)

last_date = monthly_sales['year_month'].max()
future_dates = pd.date_range(last_date + pd.offsets.MonthBegin(1), periods=future_months, freq='MS')

# Dataframe de previsões
future_df = pd.DataFrame({
    'year_month': future_dates,
    'predicted': future_preds
})

combined = pd.concat([monthly_sales[['year_month', 'total_amount', 'predicted']], future_df], ignore_index=True)

#Plot
plt.figure(figsize=(10, 5))
plt.plot(monthly_sales['year_month'], monthly_sales['total_amount'], label="Vendas reais", marker='o')
plt.plot(combined['year_month'], combined['predicted'], label="Previsão", linestyle='--', color='orange')
plt.title("Previsão de Vendas Mensais (Regressão Linear)")
plt.xlabel("Mês")
plt.ylabel("Total de Vendas (R$)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

print("\n📈 Previsões para os próximos meses:")
print(future_df)



#---------- 4 - Modelo de Previsão utilizando Prophet ----------

# Converter para formato compatível com Prophet
prophet_df = monthly_sales[['year_month', 'total_amount']].rename(
    columns={'year_month': 'ds', 'total_amount': 'y'}
)

# Criar e treinar o modelo Prophet
model_prophet = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=False,
    daily_seasonality=False,
    seasonality_mode='additive'
)

model_prophet.fit(prophet_df)

future = model_prophet.make_future_dataframe(periods=6, freq='MS')
forecast = model_prophet.predict(future)

#Plot
model_prophet.plot(forecast)
plt.title("📈 Previsão Sazonal de Vendas com Prophet")
plt.xlabel("Mês")
plt.ylabel("Total de Vendas (R$)")
plt.show()


print("\n📅 Previsões futuras com sazonalidade:")
print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(6))


# EXTRA

#---------- 5 - Análises extras de comportamento de clientes ----------

#Por Gênero
sns.countplot(data=df, x ='customer_gender')
plt.title("Distribuição por Sexo")
plt.show()

#Faixa Etária
bins = [0, 18, 25, 35, 45, 60, 80]
labels = ['<18', '18–25', '26–35', '36–45', '46–60', '60+']
df['faixa_etaria'] = pd.cut(df['customer_age'], bins=bins, labels=labels, right=False)

sns.countplot(data=df, x='faixa_etaria', order=labels)
plt.title('Distribuição de clientes por faixa etária')
plt.show()


#---------- Comportamento ----------
# Ticket médio por gênero
df.groupby('customer_gender')['total_amount'].mean().plot(kind='bar')
plt.title('Ticket médio por gênero')
plt.ylabel('R$ médio por compra')
plt.show()

# Ticket médio por faixa etária
df.groupby('faixa_etaria')['total_amount'].mean().plot(kind='bar')
plt.title('Ticket médio por faixa etária')
plt.ylabel('R$ médio por compra')
plt.show()

# Quantidade média de livros por canal
df.groupby('channel')['quantity'].mean().sort_values().plot(kind='barh')
plt.title('Quantidade média de livros por compra (por canal)')
plt.xlabel('Quantidade média')
plt.show()



#---------- Segmentação ----------

ultima_data = df['timestamp'].max()

rfm = df.groupby('customer_id').agg({
    'timestamp': lambda x: (ultima_data - x.max()).days,  
    'sale_id': 'count',                                 
    'total_amount': 'sum'                              
}).reset_index()

rfm.columns = ['customer_id', 'Recency', 'Frequency', 'Monetary']

print(rfm.describe())


# Normalização necessária para usar o K-means
scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm[['Recency', 'Frequency', 'Monetary']])



# Para descobrir o K ideal será usado o método de cotovelo
wcss = []  # Within-Cluster Sum of Squares

for k in range(1, 11):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(rfm_scaled)
    wcss.append(kmeans.inertia_)

plt.plot(range(1, 11), wcss, marker='o')
plt.title('Método do Cotovelo')
plt.xlabel('Número de clusters (K)')
plt.ylabel('WCSS')
plt.show()



# Rodar o K-means com o K ideal descoberto.
kmeans = KMeans(n_clusters=4, random_state=42)
rfm['Cluster'] = kmeans.fit_predict(rfm_scaled)

# Print dos clusters 
rfm_summary = rfm.groupby('Cluster').agg({
    'Recency': 'mean',
    'Frequency': 'mean',
    'Monetary': 'mean',
    'customer_id': 'count'
}).rename(columns={'customer_id': 'NumClientes'})

print(rfm_summary)


#Plot dos Cluesters 
sns.pairplot(rfm, hue='Cluster', vars=['Recency', 'Frequency', 'Monetary'])
plt.suptitle('Clusters de Clientes (K-Means RFM)')
plt.show()

