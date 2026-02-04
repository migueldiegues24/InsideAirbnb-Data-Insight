import os
import sys
import json
import re
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# --- CONFIGURAÇÃO DE COLUNAS ---

LISTING_COLUMNS = [
    'id',
    # Dados Financeiros e Disponibilidade (KPIs)
    'price', 
    'room_type',              # Adicionado para gráficos de distribuição
    'availability_30',        # CRUCIAL para o KPI de Ocupação
    'availability_365', 
    'estimated_revenue_l365d', # CRUCIAL para o KPI de Receita
    
    # Dados Legais e Temporais (KPIs e Gráficos)
    'license',                # CRUCIAL para distinguir Regularizados/Irregulares
    'first_review',           # CRUCIAL para o Gráfico de Novos Registos
    'last_review',
    'number_of_reviews',
    'review_scores_rating',
    'neighbourhood_group_cleansed',
    'neighbourhood_cleansed',
    
    # Localização (Para o Mapa)
    'latitude',
    'longitude'
]

USER_COLUMNS = [
    'id', 'username', 'password', 'name', 'role'
]

def extract_file_metadata(file_path):
    """
    Tenta extrair cidade e data do nome do ficheiro (ex: Porto_2023-05-20.csv).
    Se falhar, usa a data de modificação do ficheiro.
    Retorna (cidade, data_string).
    """
    filename = file_path.name
    # Regex procura padrões como Cidade_YYYY-MM-DD
    match = re.search(r'^(.+)_(\d{4}[-_]?\d{2}[-_]?\d{2})', filename)
    
    if match:
        city = match.group(1).replace('_', ' ').strip()
        date_str = match.group(2).replace('_', '-').replace('/', '-')
        # Se estiver colado (20230101), tenta formatar
        if len(date_str) == 8 and '-' not in date_str:
            date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
        return city, date_str
    else:
        # Fallback: Data de modificação do ficheiro
        timestamp = os.path.getmtime(file_path)
        return "Unknown", datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

def load_csv(path, columns_to_keep, city=None, date_label=None):
    """Carrega CSV, filtra colunas e adiciona a data de referência."""
    try:
        df = pd.read_csv(path)
    except Exception as e:
        print(f"Erro ao ler {path}: {e}", file=sys.stderr)
        return []

    # Se 'id' não estiver nas colunas desejadas, forçamos a leitura se existir no csv
    # (Útil para juntar dados históricos do mesmo item)
    if 'id' not in columns_to_keep and 'id' in df.columns:
        columns_to_keep = columns_to_keep + ['id']

    # Filtrar colunas existentes
    existing_cols = [col for col in columns_to_keep if col in df.columns]
    df = df[existing_cols]

    # --- LIMPEZA ESPECÍFICA ---
    if 'price' in df.columns:
        df['price'] = df['price'].astype(str).str.replace(r'[$,]', '', regex=True)
        df['price'] = pd.to_numeric(df['price'], errors='coerce')

    # Converter numéricos
    cols_to_numeric = ['availability_30', 'availability_365', 'estimated_revenue_l365d', 'id', 'number_of_reviews']
    for col in cols_to_numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # --- ADICIONAR DATA DE REFERÊNCIA (CRUCIAL PARA COMPARAÇÃO) ---
    if date_label:
        df['scrape_date'] = date_label
    if city:
        df['city'] = city

    # Limpar nulos
    df = df.replace([pd.NA, pd.NaT, np.nan, np.inf, -np.inf], None)
    
    return df.where(pd.notnull(df), None).to_dict(orient="records")

def collect_data(base_dir):
    """Separa ficheiros em 'listings' e 'users'."""
    database = {
        "listings": {},
        "users": []
    }
    
    base_dir = Path(base_dir).resolve()

    if not base_dir.exists():
        print(f"Erro: A diretoria '{base_dir}' não existe.", file=sys.stderr)
        return database

    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".csv"):
                path = Path(root) / file
                filename_lower = file.lower()
                
                # Obter data deste ficheiro específico
                city, file_date = extract_file_metadata(path)

                if "user" in filename_lower or "utilizador" in filename_lower:
                    print(f"Processando UTILIZADORES: {file}...")
                    # Users normalmente não precisam de histórico, carregamos sem data
                    content = load_csv(path, USER_COLUMNS)
                    database["users"].extend(content)
                else:
                    print(f"Processando ALOJAMENTOS ({city} - {file_date}): {file}...")
                    # Passamos a data para ser injetada em cada linha
                    content = load_csv(path, LISTING_COLUMNS, city=city, date_label=file_date)
                    
                    if city not in database["listings"]:
                        database["listings"][city] = []
                    database["listings"][city].extend(content)

    return database

def main():
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} <pasta_com_csvs>", file=sys.stderr)
        sys.exit(1)

    base_dir = sys.argv[1].strip()
    script_dir = Path(__file__).parent
    output_path = script_dir.parent / "db.json"

    print("Iniciando processamento com suporte a datas...")
    final_data = collect_data(base_dir)

    # --- PÓS-PROCESSAMENTO ---
    
    # 1. Deduplicar Users (ficando com o último encontrado pelo ID)
    if final_data["users"]:
        users_map = {str(u.get("id")): u for u in final_data["users"] if u.get("id")}
        final_data["users"] = list(users_map.values())
    
    # Se não encontrou users, adiciona admin
    if not final_data["users"]:
        print("Aviso: Nenhum utilizador encontrado. Adicionando admin padrão.")
        final_data["users"] = [
            {"id": 1, "username": "admin", "password": "admin", "name": "Admin", "role": "admin"}
        ]

    # Ordenar Listings por data (opcional, mas ajuda na leitura)
    for city in final_data["listings"]:
        final_data["listings"][city].sort(key=lambda x: x.get('scrape_date', ''))

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    count_listings = sum(len(l) for l in final_data["listings"].values())
    print(f"\nSucesso! '{output_path}' gerado.")
    print(f"Listings Total (Histórico): {count_listings}")
    print(f"Users Únicos: {len(final_data['users'])}")

if __name__ == "__main__":
    main()