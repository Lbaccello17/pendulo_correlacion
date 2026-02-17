"""
Configuración central del Péndulo de Correlación Global.
"""

# ── TICKERS ──
REFERENCE_TICKER = "^GSPC"
REFERENCE_NAME = "S&P 500"

TICKERS = {
    "^GSPC": "S&P 500",
    "EWC":   "Canadá 🇨🇦",
    "EWW":   "México 🇲🇽",
    "EWZ":   "Brasil 🇧🇷",
    "ECH":   "Chile 🇨🇱",
    "GXG":   "Colombia 🇨🇴",
    "EPU":   "Perú 🇵🇪",
    "ARGT":  "Argentina 🇦🇷",
    
    # Europa
    "EWG":   "Alemania 🇩🇪",
    "EWQ":   "Francia 🇫🇷",
    "EWI":   "Italia 🇮🇹",
    "EWP":   "España 🇪🇸",
    "EWU":   "Reino Unido 🇬🇧",
    "EWL":   "Suiza 🇨🇭",
    "EWN":   "Países Bajos 🇳🇱",
    "EWD":   "Suecia 🇸🇪",
    "EWK":   "Bélgica 🇧🇪",
    "EWO":   "Austria 🇦🇹",
    "EIRL":  "Irlanda 🇮🇪",
    "EDEN":  "Dinamarca 🇩🇰",
    "NORW":  "Noruega 🇳🇴",
    "EFNL":  "Finlandia 🇫🇮",
    "EPOL":  "Polonia 🇵🇱",
    "GREK":  "Grecia 🇬🇷",
    "TUR":   "Turquía 🇹🇷",

    # Asia - Pacífico
    "FXI":   "China 🇨🇳",
    "EWJ":   "Japón 🇯🇵",
    "INDA":  "India 🇮🇳",
    "EWY":   "Corea del Sur 🇰🇷",
    "EWT":   "Taiwán 🇹🇼",
    "EWA":   "Australia 🇦🇺",
    "EWS":   "Singapur 🇸🇬",
    "EWM":   "Malasia 🇲🇾",
    "EIDO":  "Indonesia 🇮🇩",
    "THD":   "Tailandia 🇹🇭",
    "EPHE":  "Filipinas 🇵🇭",
    "VNM":   "Vietnam 🇻🇳",

    # Medio Oriente & África
    "EZA":   "Sudáfrica 🇿🇦",
    "KSA":   "Arabia Saudita 🇸🇦",
    "EIS":   "Israel 🇮🇱",
    "UAE":   "EAU 🇦🇪",
}

BLOCKS = {
    "Américas 🌎": ["Canadá 🇨🇦", "México 🇲🇽", "Brasil 🇧🇷", "Chile 🇨🇱", "Colombia 🇨🇴", "Perú 🇵🇪", "Argentina 🇦🇷"],
    "Europa 🌍": ["Alemania 🇩🇪", "Francia 🇫🇷", "Reino Unido 🇬🇧", "Italia 🇮🇹", "España 🇪🇸", "Suiza 🇨🇭", "Países Bajos 🇳🇱", "Suecia 🇸🇪", "Bélgica 🇧🇪", "Austria 🇦🇹", "Irlanda 🇮🇪", "Dinamarca 🇩🇰", "Noruega 🇳🇴", "Finlandia 🇫🇮", "Polonia 🇵🇱", "Grecia 🇬🇷", "Turquía 🇹🇷"],
    "Asia-Pacífico 🌏": ["China 🇨🇳", "Japón 🇯🇵", "India 🇮🇳", "Corea del Sur 🇰🇷", "Taiwán 🇹🇼", "Australia 🇦🇺", "Singapur 🇸🇬", "Malasia 🇲🇾", "Indonesia 🇮🇩", "Tailandia 🇹🇭", "Filipinas 🇵🇭", "Vietnam 🇻🇳"],
    "Medio Oriente & África 🐪": ["Sudáfrica 🇿🇦", "Arabia Saudita 🇸🇦", "Israel 🇮🇱", "EAU 🇦🇪"],
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
    # Américas
    "Canadá 🇨🇦":      "#A6192E",
    "México 🇲🇽":      "#006847",
    "Brasil 🇧🇷":      "#009C3B",
    "Chile 🇨🇱":       "#0039A6",
    "Colombia 🇨🇴":    "#FCD116",
    "Perú 🇵🇪":        "#D91023",
    "Argentina 🇦🇷":   "#75AADB",

    # Europa
    "Alemania 🇩🇪":    "#DD0000",
    "Francia 🇫🇷":     "#0055A4",
    "Italia 🇮🇹":      "#008C45",
    "España 🇪🇸":      "#AA151B",
    "Reino Unido 🇬🇧": "#012169",
    "Suiza 🇨🇭":       "#FF0000",
    "Países Bajos 🇳🇱": "#AE1C28",
    "Suecia 🇸🇪":      "#FECC00",
    "Bélgica 🇧🇪":     "#DAA520", # Goldenrod for contrast
    "Austria 🇦🇹":     "#ED2939",
    "Irlanda 🇮🇪":     "#169B62",
    "Dinamarca 🇩🇰":   "#C60C30",
    "Noruega 🇳🇴":     "#BA0C2F",
    "Finlandia 🇫🇮":   "#003580",
    "Polonia 🇵🇱":     "#DC143C",
    "Grecia 🇬🇷":      "#0D5EAF",
    "Turquía 🇹🇷":     "#E30A17",

    # Asia-Pacífico
    "China 🇨🇳":       "#DE2910",
    "Japón 🇯🇵":       "#BC002D",
    "India 🇮🇳":       "#FF9933",
    "Corea del Sur 🇰🇷": "#0F64CD",
    "Taiwán 🇹🇼":      "#000095",
    "Australia 🇦🇺":   "#FFD700", # Green/Gold ideally, but Gold works
    "Singapur 🇸🇬":    "#EF3340",
    "Malasia 🇲🇾":     "#010066",
    "Indonesia 🇮🇩":   "#FF0000",
    "Tailandia 🇹🇭":   "#2D2A4A",
    "Filipinas 🇵🇭":   "#FCD116",
    "Vietnam 🇻🇳":     "#DA251D",

    # MEA
    "Sudáfrica 🇿🇦":   "#007A4D",
    "Arabia Saudita 🇸🇦": "#006C35",
    "Israel 🇮🇱":      "#0038B8",
    "EAU 🇦🇪":         "#00732F",
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
