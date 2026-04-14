import os
import logging
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from requests import Session
from requests.exceptions import RequestException
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s')

def load_config():
    """Carrega as configurações do arquivo .env para o ambiente do sistema."""
    base_path = Path(__file__).resolve().parent.parent
    load_dotenv(base_path / ".env")

def get_api_key() -> str:
    """Busca a chave da API de forma segura."""
    api_key = os.getenv('COINMARKETCAP_API_KEY')
    if not api_key:
        raise ValueError("ERRO: Chave 'COINMARKETCAP_API_KEY' não encontrada no ambiente.")
    return api_key

def fetch_crypto_data(api_key: str) -> list:
    """Faz a requisição na API do CoinMarketCap e retorna o JSON bruto."""
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parametros = {'start': '1', 'limit': '10', 'convert': 'USD'}
    cabecalhos = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': api_key}

    logging.info("Conectando à API do CoinMarketCap...")
    
    with Session() as session:
        session.headers.update(cabecalhos)
        try:
            resposta = session.get(url, params=parametros)
            resposta.raise_for_status() 
            return resposta.json()["data"]
        except RequestException as e:
            logging.error(f"Falha na requisição: {e}")
            raise

def process_and_save_data(raw_data: list):
    """Achata o JSON, adiciona metadados e salva no formato Parquet na camada Bronze."""
    logging.info("Iniciando processamento dos dados...")

    df = pd.json_normalize(raw_data)
    
    colunas_uteis = [
        'id', 'name', 'symbol', 'quote.USD.price', 
        'quote.USD.volume_24h', 'quote.USD.market_cap', 'quote.USD.last_updated'
    ]
    df = df[[c for c in colunas_uteis if c in df.columns]]
    
    timestamp_agora = datetime.now(timezone.utc)
    df['ingestion_timestamp'] = timestamp_agora

    env_path = os.getenv('BRONZE_DATA_DIR')
    
    bronze_dir = Path(env_path) if env_path else Path(__file__).resolve().parent / "01-bronze-raw"
    
    bronze_dir.mkdir(parents=True, exist_ok=True)

    nome_arquivo = f"crypto_listings_{timestamp_agora.strftime('%Y%m%d_%H%M%S')}.parquet"
    caminho_final = bronze_dir / nome_arquivo
    
    df.to_parquet(caminho_final, index=False)
    logging.info(f"Sucesso! Arquivo salvo: {caminho_final}")

def extract_and_save():
    """Maestro do pipeline: Coordena as fases de extração e carga."""
    load_config() 
    
    chave_api = get_api_key()
    dados_brutos = fetch_crypto_data(chave_api)
    process_and_save_data(dados_brutos)

if __name__ == "__main__":
    extract_and_save()