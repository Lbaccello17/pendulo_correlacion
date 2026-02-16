"""
Configuración central del Péndulo de Correlación Global.
"""

# ── TICKERS ──
REFERENCE_TICKER = "^GSPC"
REFERENCE_NAME = "S&P 500"

TICKERS = {
    "^GSPC": "S&P 500",
    "FXI":   "China 🇨🇳",
    "INDA":  "India 🇮🇳",
    "EWJ":   "Japón 🇯🇵",
    "EWY":   "Corea del Sur 🇰🇷",
    "EWZ":   "Brasil 🇧🇷",
    "EWW":   "México 🇲🇽",
    "ECH":   "Chile 🇨🇱",
    "GXG":   "Colombia 🇨🇴",
}

BLOCKS = {
    "Asia 🌏": ["China 🇨🇳", "India 🇮🇳", "Japón 🇯🇵", "Corea del Sur 🇰🇷"],
    "Latinoamérica 🌎": ["Brasil 🇧🇷", "México 🇲🇽", "Chile 🇨🇱", "Colombia 🇨🇴"],
}

# ── ZONAS DE CORRELACIÓN ──
ZONES = [
    {"min": 0.70, "max": 1.00, "name": "Sincronía Alta",       "emoji": "🔴", "color": "#E63946", "css": "red"},
    {"min": 0.40, "max": 0.69, "name": "Sincronía Moderada",   "emoji": "🟡", "color": "#F4A261", "css": "yellow"},
    {"min": 0.00, "max": 0.39, "name": "Desacoplamiento",      "emoji": "🟢", "color": "#2A9D8F", "css": "green"},
    {"min":-1.00, "max":-0.01, "name": "Inversión / Cobertura", "emoji": "🔵", "color": "#4895EF", "css": "blue"},
]

# ── COLORES DE LÍNEA POR REGIÓN ──
LINE_COLORS = {
    "China 🇨🇳":       "#EF476F",
    "India 🇮🇳":       "#FFD166",
    "Japón 🇯🇵":       "#118AB2",
    "Corea del Sur 🇰🇷": "#06D6A0",
    "Brasil 🇧🇷":      "#F78C6B",
    "México 🇲🇽":      "#83C5BE",
    "Chile 🇨🇱":       "#FFDDD2",
    "Colombia 🇨🇴":    "#E29578",
}

# ── DEFAULTS ──
DEFAULT_WINDOW = 30
DEFAULT_PERIOD = "2y"

PERIOD_OPTIONS = [
    {"label": "6 meses",  "value": "6mo"},
    {"label": "1 año",    "value": "1y"},
    {"label": "2 años",   "value": "2y"},
    {"label": "5 años",   "value": "5y"},
]

WINDOW_MARKS = {10: "10", 20: "20", 30: "30", 60: "60", 90: "90"}
