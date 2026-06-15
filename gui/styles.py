# Farb-Konstanten – hier zentral ändern, gilt überall
FARBEN = {
    "bg_dunkel":  "#1a1d2e",   # Haupt-Hintergrund
    "bg_karte":   "#252842",   # Karten / GroupBoxen
    "bg_zeile":   "#2d3150",   # Jede zweite Tabellenzeile
    "rand":       "#363a5a",   # Rahmen und Trennlinien
    "text":       "#e0e0e0",   # Normaler Text
    "text_dim":   "#8890a4",   # Abgedunkelter Text
    "akzent1":    "#6c63ff",   # Primär-Akzent (Lila)
    "akzent2":    "#3ecfcf",   # Sekundär-Akzent (Türkis)
    "gruen1":     "#43e97b",   # Erfolg
    "gruen2":     "#38f9d7",
    "rot1":       "#ff6584",   # Gefahr / Löschen
    "rot2":       "#ff4d6d",
    "gelb1":      "#f6d365",   # Warnung / Bearbeiten
    "gelb2":      "#fda085",
}

# Gradient-Helfer für den Stylesheet-String
def _grad(c1, c2, vertikal=False):
    x2, y2 = ("0", "1") if vertikal else ("1", "0")
    return f"qlineargradient(x1:0, y1:0, x2:{x2}, y2:{y2}, stop:0 {c1}, stop:1 {c2})"

F = FARBEN  # Kurzname für den langen Dict

STYLESHEET = f"""
/* ══ Fenster & Hintergrund ══════════════════════════════════════════════════ */
QMainWindow, QDialog {{
    background-color: {F['bg_dunkel']};
}}

/* ══ Tab-Leiste ══════════════════════════════════════════════════════════════ */
QTabWidget::pane {{
    border: none;
    background: {F['bg_karte']};
    border-radius: 0px 8px 8px 8px;
}}

QTabBar::tab {{
    background: {F['bg_dunkel']};
    color: {F['text_dim']};
    padding: 10px 24px;
    font-weight: bold;
    font-size: 13px;
    border: 1px solid {F['rand']};
    border-bottom: none;
    border-radius: 8px 8px 0 0;
    margin-right: 2px;
    min-width: 130px;
}}

QTabBar::tab:selected {{
    background: {_grad(F['akzent1'], F['akzent2'])};
    color: #ffffff;
    border-color: {F['akzent1']};
}}

QTabBar::tab:hover:!selected {{
    background: {F['bg_zeile']};
    color: {F['text']};
}}

/* ══ Tabellen ════════════════════════════════════════════════════════════════ */
QTableWidget {{
    background-color: {F['bg_karte']};
    alternate-background-color: {F['bg_zeile']};
    gridline-color: {F['rand']};
    border: none;
    border-radius: 8px;
    font-size: 13px;
    color: {F['text']};
}}

QTableWidget::item:selected {{
    background-color: {F['akzent1']};
    color: #ffffff;
}}

QHeaderView::section {{
    background: {_grad(F['akzent1'], F['akzent2'])};
    color: #ffffff;
    padding: 9px 12px;
    border: none;
    font-weight: bold;
    font-size: 13px;
}}

/* ══ Buttons ═════════════════════════════════════════════════════════════════ */
QPushButton {{
    background: {_grad(F['akzent1'], F['akzent2'])};
    color: white;
    border: none;
    padding: 8px 20px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: bold;
    min-width: 90px;
}}
QPushButton:hover  {{ background: {_grad('#7c73ff', '#4edfdf')}; }}
QPushButton:pressed {{ background: {_grad('#5c53ef', '#2ebfbf')}; }}

QPushButton#btn_danger  {{ background: {_grad(F['rot1'],  F['rot2'])}; }}
QPushButton#btn_danger:hover {{ background: {_grad('#ff7594', '#ff5d7d')}; }}

QPushButton#btn_success {{
    background: {_grad(F['gruen1'], F['gruen2'])};
    color: {F['bg_dunkel']};  /* dunkler Text auf hellem Grün */
}}
QPushButton#btn_success:hover {{
    background: {_grad('#53f98b', '#48ffe7')};
    color: {F['bg_dunkel']};
}}

QPushButton#btn_warning {{
    background: {_grad(F['gelb1'], F['gelb2'])};
    color: {F['bg_dunkel']};
}}
QPushButton#btn_warning:hover {{
    background: {_grad('#f6e375', '#fdb095')};
    color: {F['bg_dunkel']};
}}

/* ══ Eingabefelder ═══════════════════════════════════════════════════════════ */
QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QDateEdit, QTextEdit {{
    border: 2px solid {F['rand']};
    border-radius: 6px;
    padding: 6px 10px;
    background: {F['bg_dunkel']};
    color: {F['text']};
    font-size: 13px;
    min-height: 30px;
}}

/* Fokus: Rand wird zur Akzentfarbe */
QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus,
QSpinBox:focus, QDateEdit:focus, QTextEdit:focus {{
    border-color: {F['akzent1']};
}}

QComboBox::drop-down {{ border: none; }}

QComboBox QAbstractItemView {{
    background: {F['bg_karte']};
    color: {F['text']};
    selection-background-color: {F['akzent1']};
    border: 1px solid {F['rand']};
    border-radius: 4px;
}}

/* ══ GroupBox = Karte mit Überschrift ════════════════════════════════════════ */
QGroupBox {{
    font-weight: bold;
    font-size: 13px;
    border: 1px solid {F['rand']};
    border-radius: 10px;
    margin-top: 14px;
    padding: 14px 12px 10px 12px;
    background: {F['bg_karte']};
    color: {F['text']};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 8px;
    color: {F['akzent1']};
    font-size: 14px;
}}

/* ══ Labels ══════════════════════════════════════════════════════════════════ */
QLabel {{
    font-size: 13px;
    color: {F['text_dim']};
}}

/* ══ Menüleiste ══════════════════════════════════════════════════════════════ */
QMenuBar {{
    background: {F['bg_dunkel']};
    color: {F['text_dim']};
    border-bottom: 1px solid {F['rand']};
    font-size: 13px;
}}
QMenuBar::item:selected {{
    background: {F['akzent1']};
    color: white;
    border-radius: 4px;
}}

QMenu {{
    background: {F['bg_karte']};
    color: {F['text']};
    border: 1px solid {F['rand']};
    border-radius: 6px;
    padding: 4px;
}}
QMenu::item:selected {{
    background: {F['akzent1']};
    color: white;
    border-radius: 4px;
}}

/* ══ Statusleiste unten ══════════════════════════════════════════════════════ */
QStatusBar {{
    background: {_grad(F['akzent1'], F['akzent2'])};
    color: white;
    font-size: 12px;
    font-weight: bold;
}}

/* ══ Scrollbar (schlank, modern) ═════════════════════════════════════════════ */
QScrollBar:vertical {{
    border: none;
    background: {F['bg_dunkel']};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {F['rand']};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {F['akzent1']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}

QScrollBar:horizontal {{
    border: none;
    background: {F['bg_dunkel']};
    height: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: {F['rand']};
    border-radius: 4px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {F['akzent1']};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; }}

/* ══ Splitter-Trennlinie ═════════════════════════════════════════════════════ */
QSplitter::handle {{
    background: {F['rand']};
    width: 2px;
}}
"""
