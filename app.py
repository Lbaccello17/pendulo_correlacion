"""
🌍⚖️ El Péndulo de Correlación Global
App principal — Dash + Plotly con datos reales de Yahoo Finance.

Ejecutar:
    pip install -r requirements.txt
    python app.py

Abrir en navegador: http://127.0.0.1:8050
"""

import locale
import dash
from dash import html, dcc, Input, Output, State, callback
from io import StringIO
import traceback
import plotly.graph_objects as go
import numpy as np

from config import (
    BLOCKS, LINE_COLORS, ZONES, PERIOD_OPTIONS,
    DEFAULT_WINDOW, DEFAULT_PERIOD, WINDOW_MARKS, REFERENCE_NAME,
    TICKERS,
)
from data_fetcher import fetch_prices
from calculations import (
    compute_rolling_correlation,
    classify_zone,
    get_current_snapshot,
    generate_diagnosis,
)

# ── Intentar locale español para fechas ──
try:
    locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
except Exception:
    try:
        locale.setlocale(locale.LC_TIME, "es_ES")
    except Exception:
        pass

# ══════════════════════════════════════════════════════════
# ESTILOS CSS
# ══════════════════════════════════════════════════════════

THEME = {
    "bg_deep": "#0B0E1A",
    "bg_primary": "#111427",
    "bg_card": "#171B30",
    "border": "#252A45",
    "text_primary": "#E8ECF4",
    "text_secondary": "#6B7394",
    "text_muted": "#454B6B",
    "accent": "#2A9D8F",
    "red": "#E63946",
    "yellow": "#F4A261",
    "green": "#2A9D8F",
    "blue": "#4895EF",
}

ZONE_COLOR_MAP = {"red": THEME["red"], "yellow": THEME["yellow"], "green": THEME["green"], "blue": THEME["blue"]}

def hex_to_rgba(hex_code, alpha):
    """Convert hex color to rgba string."""
    hex_code = hex_code.lstrip('#')
    return f"rgba({int(hex_code[0:2], 16)}, {int(hex_code[2:4], 16)}, {int(hex_code[4:6], 16)}, {alpha})"

# ══════════════════════════════════════════════════════════
# APP SETUP
# ══════════════════════════════════════════════════════════

app = dash.Dash(
    __name__,
    title="Péndulo de Correlación Global 🌍⚖️",
    update_title=None,
    suppress_callback_exceptions=True,
)

# ══════════════════════════════════════════════════════════
# LAYOUT
# ══════════════════════════════════════════════════════════

app.index_string = '''<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    {%css%}
    <link href="https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: ''' + THEME["bg_deep"] + ''';
            color: ''' + THEME["text_primary"] + ''';
            font-family: 'Sora', sans-serif;
            min-height: 100vh;
        }
        /* Dash component overrides */
    </style>
</head>
<body>
    {%app_entry%}
    <footer>{%config%}{%scripts%}{%renderer%}</footer>
</body>
</html>'''


def make_section_label(text, badge_text=None, badge_color=None):
    children = [html.H2(text, style={"fontSize": "13px", "fontWeight": 600, "textTransform": "uppercase",
                                      "letterSpacing": "1.5px", "color": THEME["text_secondary"]})]
    if badge_text:
        children.append(html.Span(badge_text, style={
            "fontFamily": "'JetBrains Mono'", "fontSize": "10px", "padding": "3px 8px",
            "borderRadius": "4px", "fontWeight": 600,
            "background": hex_to_rgba(badge_color, 0.13), "color": badge_color, "border": f"1px solid {hex_to_rgba(badge_color, 0.2)}",
        }))
    children.append(html.Div(style={"flex": 1, "height": "1px", "background": THEME["border"]}))
    return html.Div(children, style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "16px", "marginTop": "8px"})


app.layout = html.Div([
    # Stored data
    dcc.Store(id="store-prices"),
    dcc.Store(id="store-correlations"),

    # ── HEADER ──
    html.Div([
        html.Div([
            html.Div("⚖️", style={
                "width": "52px", "height": "52px", "borderRadius": "14px",
                "background": f"linear-gradient(135deg, {THEME['accent']}, {THEME['blue']})",
                "display": "flex", "alignItems": "center", "justifyContent": "center",
                "fontSize": "26px", "boxShadow": f"0 4px 24px {hex_to_rgba(THEME['accent'], 0.27)}",
            }),
            html.Div([
                html.H1("Mercados Internacionales VS S&P 500", style={
                    "fontSize": "22px", "fontWeight": 700, "letterSpacing": "-0.5px"}),
                html.Span("Sincronía vs Desacoplamiento · Mercados Emergentes vs S&P 500", style={
                    "fontSize": "12px", "color": THEME["text_secondary"],
                    "letterSpacing": "1px", "textTransform": "uppercase"}),
            ]),
        ], style={"display": "flex", "alignItems": "center", "gap": "16px"}),

        # Controls
        html.Div([
            html.Div([
                html.Label("Período", style={"fontSize": "11px", "color": THEME["text_secondary"],
                                               "fontWeight": 500, "textTransform": "uppercase", "letterSpacing": "0.5px"}),
                dcc.Dropdown(
                    id="period-dropdown",
                    options=PERIOD_OPTIONS,
                    value=DEFAULT_PERIOD,
                    clearable=False,
                    style={"width": "120px", "fontSize": "12px", "fontFamily": "'JetBrains Mono'"},
                ),
            ], style={"display": "flex", "alignItems": "center", "gap": "8px",
                       "background": THEME["bg_card"], "border": f"1px solid {THEME['border']}",
                       "borderRadius": "10px", "padding": "6px 12px"}),

            html.Div([
                html.Label("Ventana", style={"fontSize": "11px", "color": THEME["text_secondary"],
                                               "fontWeight": 500, "textTransform": "uppercase", "letterSpacing": "0.5px", "whiteSpace": "nowrap"}),
                html.Div([
                    dcc.Slider(
                        id="window-slider",
                        min=10, max=90, step=5, value=DEFAULT_WINDOW,
                        marks=WINDOW_MARKS,
                        tooltip={"placement": "top", "always_visible": False},
                    ),
                ], style={"width": "180px"}),
            ], style={"display": "flex", "alignItems": "center", "gap": "8px",
                       "background": THEME["bg_card"], "border": f"1px solid {THEME['border']}",
                       "borderRadius": "10px", "padding": "6px 12px"}),

            html.Button("⟳ Actualizar", id="btn-refresh", n_clicks=0, style={
                "background": f"linear-gradient(135deg, {THEME['accent']}, #238b80)",
                "color": "white", "border": "none", "borderRadius": "10px",
                "padding": "10px 20px", "fontFamily": "'Sora'", "fontSize": "12px",
                "fontWeight": 600, "cursor": "pointer", "letterSpacing": "0.3px",
            }),
        ], style={"display": "flex", "gap": "12px", "alignItems": "center", "flexWrap": "wrap"}),
    ], style={
        "display": "flex", "alignItems": "center", "justifyContent": "space-between",
        "padding": "20px 0 28px", "borderBottom": f"1px solid {THEME['border']}",
        "marginBottom": "24px", "flexWrap": "wrap", "gap": "16px",
    }),

    # ── FILTERS ──
    html.Div([
        html.Label("Seleccionar Mercados:", style={"fontSize": "12px", "fontWeight": 600, "marginBottom": "8px", "display": "block", "color": THEME["text_secondary"]}),
        dcc.Dropdown(
            id="ticker-selector",
            options=[{"label": name, "value": name} for name in TICKERS.values() if name != "S&P 500"],
            value=[name for name in TICKERS.values() if name != "S&P 500"],  # Default all
            multi=True,
            clearable=False,
            style={"fontSize": "12px", "fontFamily": "'JetBrains Mono'"},
        ),
    ], style={"marginBottom": "32px", "maxWidth": "100%"}),

    # ── LEGEND ──
    html.Div([
        html.Div([
            html.Div(style={"width": "10px", "height": "10px", "borderRadius": "3px", "background": z["color"]}),
            html.Span(f"{z['name']} ({z['min']:.2f} a {z['max']:.2f})", style={"fontSize": "11px", "color": THEME["text_secondary"]}),
        ], style={"display": "flex", "alignItems": "center", "gap": "6px"})
        for z in ZONES
    ], style={"display": "flex", "gap": "20px", "justifyContent": "center", "margin": "16px 0", "flexWrap": "wrap"}),

    # ── STATUS ──
    html.Div(id="status-msg", style={
        "textAlign": "center", "fontSize": "12px", "color": THEME["accent"],
        "fontFamily": "'JetBrains Mono'", "marginBottom": "16px",
    }),

    # ── AMÉRICAS GAUGES ──
    make_section_label("Américas", "Norte y Sur", THEME["green"]),
    html.Div(id="americas-gauges", style={
        "display": "grid", "gridTemplateColumns": "repeat(auto-fill, minmax(240px, 1fr))",
        "gap": "14px", "marginBottom": "24px",
    }),

    # ── EUROPA GAUGES ──
    make_section_label("Europa", "Mercados Desarrollados", THEME["red"]),
    html.Div(id="europa-gauges", style={
        "display": "grid", "gridTemplateColumns": "repeat(auto-fill, minmax(240px, 1fr))",
        "gap": "14px", "marginBottom": "24px",
    }),

    # ── ASIA-PACÍFICO GAUGES ──
    make_section_label("Asia - Pacífico", "Mercados Asiáticos y Oceanía", THEME["blue"]),
    html.Div(id="asia-gauges", style={
        "display": "grid", "gridTemplateColumns": "repeat(auto-fill, minmax(240px, 1fr))",
        "gap": "14px", "marginBottom": "24px",
    }),

    # ── MEA GAUGES ──
    make_section_label("Medio Oriente & África", "Mercados Emergentes", "#FFFF00"),
    html.Div(id="mea-gauges", style={
        "display": "grid", "gridTemplateColumns": "repeat(auto-fill, minmax(240px, 1fr))",
        "gap": "14px", "marginBottom": "24px",
    }),

    # ── ROLLING CHART ──
    html.Div([
        html.Div([
            html.Div(style={"width": "8px", "height": "8px", "borderRadius": "50%", "background": THEME["accent"]}),
            html.Span("Correlación Rodante vs S&P 500", style={"fontSize": "14px", "fontWeight": 600}),
        ], style={"display": "flex", "alignItems": "center", "gap": "8px", "marginBottom": "12px"}),
        dcc.Graph(id="rolling-chart", config={"displayModeBar": False}, style={"height": "400px"}),
    ], style={
        "background": THEME["bg_card"], "border": f"1px solid {THEME['border']}",
        "borderRadius": "14px", "padding": "20px", "marginBottom": "24px",
    }),

    # ── BOTTOM ROW ──
    html.Div([
        # Heatmap
        html.Div([
            html.Div("🗺️ Snapshot Actual", style={"fontSize": "14px", "fontWeight": 600, "marginBottom": "14px"}),
            html.Div(id="heatmap-table"),
        ], style={
            "background": THEME["bg_card"], "border": f"1px solid {THEME['border']}",
            "borderRadius": "14px", "padding": "20px",
        }),
        # Diagnosis
        html.Div([
            html.Div("📊 Diagnóstico Automático", style={"fontSize": "14px", "fontWeight": 600, "marginBottom": "14px"}),
            html.Div(id="diagnosis-content"),
        ], style={
            "background": THEME["bg_card"], "border": f"1px solid {THEME['border']}",
            "borderRadius": "14px", "padding": "20px",
        }),
    ], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"}),

    # Footer
    html.Div("Datos: Yahoo Finance vía yfinance · Actualización cada 4h · Correlación rodante Pearson",
             style={"textAlign": "center", "fontSize": "11px", "color": THEME["text_muted"],
                     "marginTop": "32px", "paddingBottom": "24px"}),

], style={"maxWidth": "1440px", "margin": "0 auto", "padding": "24px"})


# ══════════════════════════════════════════════════════════
# CALLBACKS
# ══════════════════════════════════════════════════════════

@callback(
    Output("store-prices", "data"),
    Output("status-msg", "children"),
    Input("btn-refresh", "n_clicks"),
    Input("period-dropdown", "value"),
)
def load_data(n_clicks, period):
    """Descarga / cachea datos de yfinance."""
    try:
        prices = fetch_prices(period=period, force=(n_clicks or 0) > 0 and dash.ctx.triggered_id == "btn-refresh")
        n_days = len(prices)
        n_tickers = len(prices.columns) - 1  # Exclude reference
        msg = f"✅ {n_tickers} mercados · {n_days} días · Último dato: {prices.index[-1].strftime('%d/%m/%Y')}"
        return prices.to_json(date_format="iso"), msg
    except Exception as e:
        return None, f"❌ Error cargando datos: {str(e)}"


@callback(
    Output("americas-gauges", "children"),
    Output("europa-gauges", "children"),
    Output("asia-gauges", "children"),
    Output("mea-gauges", "children"),
    Output("rolling-chart", "figure"),
    Output("heatmap-table", "children"),
    Output("diagnosis-content", "children"),
    Input("store-prices", "data"),
    Input("window-slider", "value"),
    Input("ticker-selector", "value"),
)
def update_all(prices_json, window, selected_tickers):
    """Actualiza todos los componentes cuando cambian datos o ventana."""
    if not prices_json:
        empty = html.Div("Esperando datos...", style={"color": THEME["text_muted"], "fontSize": "13px"})
        return empty, empty, empty, empty, go.Figure(), empty, empty

    import pandas as pd
    # Fix read_json warning
    prices = pd.read_json(StringIO(prices_json))
    
    correlations = compute_rolling_correlation(prices, window=window)

    # Filter by selection
    if selected_tickers:
        valid_cols = [c for c in correlations.columns if c in selected_tickers]
        correlations = correlations[valid_cols]

    if correlations.empty:
        print("DEBUG: Correlations is empty! Returning empty components.")
        empty = html.Div("Sin datos de correlación suficientes.", style={"color": THEME["text_muted"], "fontSize": "13px"})
        return [], [], [], [], go.Figure(), empty, empty

    americas_cards = build_gauge_cards(correlations, BLOCKS.get("Américas 🌎", []))
    europa_cards = build_gauge_cards(correlations, BLOCKS.get("Europa 🌍", []))
    asia_cards = build_gauge_cards(correlations, BLOCKS.get("Asia-Pacífico 🌏", []))
    mea_cards = build_gauge_cards(correlations, BLOCKS.get("Medio Oriente & África 🐪", []))
    
    chart = build_rolling_chart(correlations)
    heatmap = build_heatmap(correlations)
    diagnosis = build_diagnosis(correlations)

    return americas_cards, europa_cards, asia_cards, mea_cards, chart, heatmap, diagnosis


# ══════════════════════════════════════════════════════════
# COMPONENT BUILDERS
# ══════════════════════════════════════════════════════════

def build_gauge_cards(correlations, region_names):
    """Crea los gauge cards para un bloque de regiones."""
    cards = []
    available = [r for r in region_names if r in correlations.columns]

    for region in available:
        series = correlations[region].dropna()
        if series.empty:
            continue

        value = series.iloc[-1]
        # Round to 2 decimals for display consistency
        value = round(value, 2)
        zone = classify_zone(value)
        color = ZONE_COLOR_MAP[zone["css"]]

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            number={"font": {"size": 28, "family": "JetBrains Mono", "color": color}, "valueformat": "+.2f"},
            gauge={
                "axis": {"range": [-1, 1], "tickwidth": 0, "tickfont": {"size": 9, "color": THEME["text_muted"]},
                         "dtick": 0.5},
                "bar": {"color": color, "thickness": 0.3},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [-1, -0.01], "color": hex_to_rgba(THEME["blue"], 0.1)},
                    {"range": [0, 0.39],   "color": hex_to_rgba(THEME["green"], 0.1)},
                    {"range": [0.40, 0.69], "color": hex_to_rgba(THEME["yellow"], 0.1)},
                    {"range": [0.70, 1.0], "color": hex_to_rgba(THEME["red"], 0.1)},
                ],
                "threshold": {
                    "line": {"color": THEME["text_primary"], "width": 3},
                    "thickness": 0.8,
                    "value": value,
                },
            },
        ))

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"family": "Sora", "color": THEME["text_primary"]},
            margin={"t": 24, "b": 0, "l": 16, "r": 16},
            height=140,
        )

        card = html.Div([
            html.Div(region, style={"fontSize": "13px", "fontWeight": 600, "textAlign": "center", "marginBottom": "2px"}),
            dcc.Graph(figure=fig, config={"displayModeBar": False}, style={"height": "140px"}),
            html.Div(
                f"{zone['emoji']} {zone['name']}",
                style={
                    "textAlign": "center", "fontSize": "10px", "fontWeight": 600,
                    "textTransform": "uppercase", "letterSpacing": "0.5px",
                    "padding": "3px 8px", "borderRadius": "4px", "display": "inline-block",
                    "background": hex_to_rgba(color, 0.13), "color": color,
                },
            ),
        ], style={
            "background": THEME["bg_card"], "border": f"1px solid {THEME['border']}",
            "borderRadius": "14px", "padding": "14px 10px 10px", "textAlign": "center",
            "borderTop": f"3px solid {color}",
        })

        cards.append(card)

    return cards


def build_rolling_chart(correlations):
    """Construye el gráfico de series de correlación rodante."""
    fig = go.Figure()

    for col in correlations.columns:
        color = LINE_COLORS.get(col, "#FFFFFF")
        fig.add_trace(go.Scatter(
            x=correlations.index, y=correlations[col],
            mode="lines", name=col,
            line={"width": 2, "color": color},
            hovertemplate=f"<b>{col}</b><br>Fecha: %{{x|%d %b %Y}}<br>Correlación: %{{y:.3f}}<extra></extra>",
        ))

    # Zone background bands
    for z in ZONES:
        fig.add_hrect(
            y0=z["min"], y1=z["max"],
            fillcolor=hex_to_rgba(z["color"], 0.05),
            line_width=0, layer="below",
        )

    # Zero line
    fig.add_hline(y=0, line_dash="dot", line_color=THEME["text_muted"], line_width=1)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Sora", "color": THEME["text_secondary"], "size": 11},
        margin={"t": 10, "r": 20, "b": 40, "l": 50},
        xaxis={"gridcolor": hex_to_rgba(THEME["border"], 0.2), "tickfont": {"size": 10}},
        yaxis={
            "range": [-1, 1], "gridcolor": hex_to_rgba(THEME["border"], 0.2),
            "zeroline": False, "dtick": 0.2,
            "tickfont": {"family": "JetBrains Mono", "size": 10},
        },
        legend={
            "orientation": "h", "y": -0.15, "x": 0.5, "xanchor": "center",
            "font": {"size": 11}, "bgcolor": "rgba(0,0,0,0)",
        },
        hovermode="x unified",
    )

    return fig


def build_heatmap(correlations):
    """Construye la tabla heatmap con snapshot actual."""
    snapshot = get_current_snapshot(correlations)

    # Group by blocks
    americas_names = set(BLOCKS.get("Américas 🌎", []))
    europa_names = set(BLOCKS.get("Europa 🌍", []))
    asia_names = set(BLOCKS.get("Asia-Pacífico 🌏", []))
    mea_names = set(BLOCKS.get("Medio Oriente & África 🐪", []))

    americas_items = [s for s in snapshot if s["region"] in americas_names]
    europa_items = [s for s in snapshot if s["region"] in europa_names]
    asia_items = [s for s in snapshot if s["region"] in asia_names]
    mea_items = [s for s in snapshot if s["region"] in mea_names]

    def make_rows(items, block_label):
        rows = [html.Tr([
            html.Td(block_label, colSpan=4, style={
                "fontSize": "11px", "fontWeight": 700, "textTransform": "uppercase",
                "letterSpacing": "1.5px", "color": THEME["text_secondary"],
                "padding": "14px 10px 6px", "background": "transparent",
            })
        ])]

        for item in items:
            color = ZONE_COLOR_MAP[item["zone"]["css"]]
            delta = item["delta"]
            delta_str = f"↑ +{delta:.2f}" if delta >= 0 else f"↓ {delta:.2f}"
            delta_color = THEME["red"] if delta >= 0 else THEME["green"]

            rows.append(html.Tr([
                html.Td(item["region"], style={"padding": "8px 10px", "background": THEME["bg_primary"], "borderRadius": "8px 0 0 8px", "fontWeight": 500}),
                html.Td(
                    f"{'+' if item['correlation'] >= 0 else ''}{item['correlation']:.3f}",
                    style={"padding": "8px 10px", "background": THEME["bg_primary"],
                           "fontFamily": "'JetBrains Mono'", "fontWeight": 700, "fontSize": "14px", "color": color}
                ),
                html.Td(delta_str, style={"padding": "8px 10px", "background": THEME["bg_primary"],
                                           "fontFamily": "'JetBrains Mono'", "fontSize": "12px", "color": delta_color}),
                html.Td(
                    html.Span(f"{item['zone']['emoji']} {item['zone']['name']}", style={
                        "fontSize": "9px", "fontWeight": 700, "textTransform": "uppercase",
                        "letterSpacing": "0.5px", "padding": "3px 8px", "borderRadius": "4px",
                        "background": hex_to_rgba(color, 0.13), "color": color, "border": f"1px solid {hex_to_rgba(color, 0.2)}",
                        "whiteSpace": "nowrap",
                    }),
                    style={"padding": "8px 10px", "background": THEME["bg_primary"], "borderRadius": "0 8px 8px 0"}
                ),
            ]))
        return rows

    header = html.Tr([
        html.Th(t, style={"textAlign": "left", "fontSize": "10px", "textTransform": "uppercase",
                           "letterSpacing": "1px", "color": THEME["text_muted"], "padding": "6px 10px", "fontWeight": 600})
        for t in ["Región", "Correlación", "Δ 30d", "Zona"]
    ])

    return html.Table(
        [header] + 
        make_rows(americas_items, "🌎 AMÉRICAS") + 
        make_rows(europa_items, "🌍 EUROPA") + 
        make_rows(asia_items, "🌏 ASIA-PACÍFICO") + 
        make_rows(mea_items, "🐪 MEDIO ORIENTE & ÁFRICA"),
        style={"width": "100%", "borderCollapse": "separate", "borderSpacing": "0 4px", "fontSize": "13px"},
    )


def build_diagnosis(correlations):
    """Construye el panel de diagnóstico automático."""
    diag = generate_diagnosis(correlations)

    children = [
        html.Div(f"📅 Diagnóstico Global — {diag['date']}", style={
            "fontFamily": "'JetBrains Mono'", "fontSize": "11px",
            "color": THEME["text_muted"], "marginBottom": "14px",
        }),
    ]

    order = ["red", "yellow", "green", "blue"]
    descriptions = {
        "red": "Riesgo sistémico. Si USA cae, estos mercados caerán con ella. Sin beneficio de diversificación.",
        "yellow": "Correlación parcial con Wall Street. Diversificación limitada.",
        "green": "Dinámica propia. Oportunidad real de diversificación y posible refugio.",
        "blue": "Movimiento contrario a USA. Posible cobertura natural (hedge).",
    }

    for z_css in order:
        if z_css not in diag["groups"]:
            continue
        group = diag["groups"][z_css]
        zone = group["zone"]
        color = ZONE_COLOR_MAP[z_css]
        regions_str = ", ".join(f"{r['name']} ({r['value']:.2f})" for r in group["regions"])

        children.append(html.Div([
            html.Div(f"{zone['emoji']} {zone['name']}", style={
                "fontWeight": 700, "fontSize": "12px", "textTransform": "uppercase",
                "letterSpacing": "0.5px", "marginBottom": "4px", "color": color,
            }),
            html.P([html.Strong(regions_str), f" — {descriptions[z_css]}"], style={
                "fontSize": "12.5px", "color": THEME["text_secondary"], "lineHeight": "1.6",
            }),
        ], style={
            "marginBottom": "12px", "padding": "10px 14px", "borderRadius": "10px",
            "borderLeft": f"3px solid {color}", "background": hex_to_rgba(color, 0.08),
        }))

    # Trends
    asia_t = diag["asia_trend"]
    americas_t = diag["americas_trend"]
    asia_dir = "subido" if asia_t["pct_change"] >= 0 else "bajado"
    americas_dir = "subido" if americas_t["pct_change"] >= 0 else "bajado"

    children.append(html.Div([
        html.Strong("📈 Tendencia (último mes):"), html.Br(),
        f"La correlación promedio ", html.Strong("Asia-Pacífico–USA"), f" ha ",
        html.Strong(asia_dir), f" un {abs(asia_t['pct_change']):.1f}%.", html.Br(),
        f"La correlación promedio ", html.Strong("Américas–USA"), f" ha ",
        html.Strong(americas_dir), f" un {abs(americas_t['pct_change']):.1f}%.",
    ], style={
        "marginTop": "14px", "padding": "10px 14px", "background": THEME["bg_primary"],
        "borderRadius": "10px", "fontSize": "12px", "color": THEME["text_secondary"],
        "lineHeight": "1.7", "border": f"1px solid {THEME['border']}",
    }))

    return children


# ══════════════════════════════════════════════════════════
# RUN
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n🌍⚖️  El Péndulo de Correlación Global")
    print("=" * 50)
    print("📡 Conectando a Yahoo Finance...")
    print("🌐 Abriendo en: http://127.0.0.1:8050\n")
    app.run(debug=True, host="127.0.0.1", port=8050)
