"""
Cálculos de correlación rodante, clasificación de zonas y diagnóstico automático.
"""

import pandas as pd
import numpy as np
from config import ZONES, BLOCKS, REFERENCE_TICKER, TICKERS

REFERENCE_NAME = TICKERS[REFERENCE_TICKER]


def compute_rolling_correlation(prices: pd.DataFrame, window: int = 30) -> pd.DataFrame:
    """
    Calcula la correlación rodante de cada región contra el S&P 500.

    Args:
        prices: DataFrame con precios de cierre (columnas = nombres de regiones).
        window: Ventana en días hábiles.

    Returns:
        DataFrame con correlaciones rodantes (sin la columna de referencia).
    """
    returns = prices.pct_change().dropna()

    if REFERENCE_NAME not in returns.columns:
        raise ValueError(f"Columna de referencia '{REFERENCE_NAME}' no encontrada en los datos.")

    ref = returns[REFERENCE_NAME]
    regions = [c for c in returns.columns if c != REFERENCE_NAME]

    correlations = pd.DataFrame(index=returns.index)
    for col in regions:
        correlations[col] = returns[col].rolling(window=window).corr(ref)

    return correlations.dropna(how="all")


def classify_zone(value: float) -> dict:
    """
    Clasifica un valor de correlación en su zona correspondiente.
    """
    for z in ZONES:
        if z["min"] <= value <= z["max"]:
            return z
    # Fallback para valores exactamente en el borde
    if value >= 0.70:
        return ZONES[0]
    if value < 0:
        return ZONES[3]
    return ZONES[2]


def get_current_snapshot(correlations: pd.DataFrame) -> list[dict]:
    """
    Genera el snapshot actual: último valor de correlación por región,
    delta vs 30 días antes, y clasificación de zona.
    """
    latest = correlations.iloc[-1]
    prev = correlations.iloc[-30] if len(correlations) >= 30 else correlations.iloc[0]

    snapshot = []
    for col in correlations.columns:
        current = latest[col]
        delta = current - prev[col]
        zone = classify_zone(current)
        snapshot.append({
            "region": col,
            "correlation": current,
            "delta": delta,
            "zone": zone,
        })

    # Ordenar de mayor a menor correlación
    snapshot.sort(key=lambda x: x["correlation"], reverse=True)
    return snapshot


def generate_diagnosis(correlations: pd.DataFrame) -> dict:
    """
    Genera un diagnóstico automático en español.

    Returns:
        dict con keys: 'date', 'groups', 'asia_trend', 'latam_trend'
    """
    latest = correlations.iloc[-1]
    prev = correlations.iloc[-30] if len(correlations) >= 30 else correlations.iloc[0]

    # Agrupar por zona
    groups = {}
    for col in correlations.columns:
        val = latest[col]
        zone = classify_zone(val)
        key = zone["css"]
        if key not in groups:
            groups[key] = {"zone": zone, "regions": []}
        groups[key]["regions"].append({"name": col, "value": val})

    # Tendencias por bloque
    def block_trend(region_names):
        cols = [c for c in correlations.columns if c in region_names]
        if not cols:
            return 0.0, 0.0, 0.0
        avg_now = latest[cols].mean()
        avg_prev = prev[cols].mean()
        pct = ((avg_now - avg_prev) / abs(avg_prev)) * 100 if avg_prev != 0 else 0
        return avg_now, avg_prev, pct

    asia_now, asia_prev, asia_pct = block_trend(BLOCKS.get("Asia-Pacífico 🌏", []))
    americas_now, americas_prev, americas_pct = block_trend(BLOCKS.get("Américas 🌎", []))

    return {
        "date": correlations.index[-1].strftime("%d de %B de %Y") if hasattr(correlations.index[-1], "strftime") else str(correlations.index[-1]),
        "groups": groups,
        "asia_trend": {"avg_now": asia_now, "pct_change": asia_pct},
        "americas_trend": {"avg_now": americas_now, "pct_change": americas_pct},
    }
