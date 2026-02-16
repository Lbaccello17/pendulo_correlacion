# 🌍⚖️ El Péndulo de Correlación Global

Widget interactivo que mide la sincronía o desacoplamiento entre mercados emergentes (Asia y Latinoamérica) y el S&P 500 usando correlación rodante con datos reales de Yahoo Finance.

## ⚡ Inicio Rápido

```bash
# 1. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar
python app.py
```

**Abrir en navegador:** [http://127.0.0.1:8050](http://127.0.0.1:8050)

## 📁 Estructura

```
pendulo_correlacion/
├── app.py              ← App principal (Dash + Plotly)
├── config.py           ← Tickers, colores, umbrales
├── data_fetcher.py     ← Descarga datos de Yahoo Finance (con cache)
├── calculations.py     ← Correlación rodante + diagnóstico
├── requirements.txt    ← Dependencias
└── README.md
```

## 🎛️ Controles

| Control | Función |
|---|---|
| **Período** | 6 meses, 1 año, 2 años, 5 años |
| **Ventana** | Días de correlación rodante (10–90) |
| **Actualizar** | Fuerza re-descarga desde Yahoo Finance |

## 🔴🟡🟢🔵 Zonas

| Correlación | Zona | Significado |
|---|---|---|
| 0.70 – 1.00 | 🔴 Sincronía Alta | Riesgo sistémico, sin diversificación |
| 0.40 – 0.69 | 🟡 Sincronía Moderada | Diversificación limitada |
| 0.00 – 0.39 | 🟢 Desacoplamiento | Oportunidad de diversificación real |
| -1.00 – -0.01 | 🔵 Inversión/Cobertura | Hedge natural contra USA |

## 📊 Mercados Monitoreados

**Asia:** China (FXI), India (INDA), Japón (EWJ), Corea del Sur (EWY)
**LatAm:** Brasil (EWZ), México (EWW), Chile (ECH), Colombia (GXG)
**Referencia:** S&P 500 (^GSPC)
