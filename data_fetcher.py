"""
Descarga y cachea datos de Yahoo Finance usando yfinance.
"""

import os
import time
import pandas as pd
import yfinance as yf
from config import TICKERS, REFERENCE_TICKER

CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
CACHE_TTL = 4 * 3600  # 4 horas


def _cache_path(period: str) -> str:
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, f"prices_{period}.pkl")


def _cache_is_valid(path: str) -> bool:
    if not os.path.exists(path):
        return False
    age = time.time() - os.path.getmtime(path)
    return age < CACHE_TTL


def fetch_prices(period: str = "2y", force: bool = False) -> pd.DataFrame:
    """
    Descarga precios de cierre ajustado de todos los tickers.
    Cachea localmente durante 4 horas.

    Returns:
        DataFrame con columnas = nombres legibles de cada ticker, index = fecha.
    """
    path = _cache_path(period)

    if not force and _cache_is_valid(path):
        print(f"📦 Usando datos cacheados ({path})")
        return pd.read_pickle(path)

    print(f"🌐 Descargando datos de Yahoo Finance (período: {period})...")
    tickers_list = list(TICKERS.keys())

    try:
        raw = yf.download(
            tickers_list,
            period=period,
            auto_adjust=True,
            progress=False,
            threads=True,
        )

        # yf.download devuelve MultiIndex cuando hay múltiples tickers
        if isinstance(raw.columns, pd.MultiIndex):
            prices = raw["Close"].copy()
        else:
            # Un solo ticker (no debería pasar, pero por seguridad)
            prices = raw[["Close"]].copy()
            prices.columns = [tickers_list[0]]

        # Renombrar columnas de tickers a nombres legibles
        rename_map = {ticker: name for ticker, name in TICKERS.items() if ticker in prices.columns}
        prices.rename(columns=rename_map, inplace=True)

        # Eliminar filas donde todos son NaN, forward-fill gaps menores
        prices.dropna(how="all", inplace=True)
        prices.ffill(inplace=True)

        # Guardar cache
        prices.to_pickle(path)
        print(f"✅ Datos descargados: {len(prices)} días, {len(prices.columns)} tickers")
        return prices

    except Exception as e:
        print(f"❌ Error descargando datos: {e}")
        # Si hay cache viejo, usarlo como fallback
        if os.path.exists(path):
            print("⚠️ Usando cache antiguo como fallback")
            return pd.read_pickle(path)
        raise
