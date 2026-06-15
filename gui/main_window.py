from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QStatusBar, QLabel,
    QAction, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from gui.styles import STYLESHEET, FARBEN
from gui.kontenplan_tab import KontenplanTab
from gui.buchungen_tab import BuchungenTab
from gui.anlagen_tab import AnlagenTab
from gui.auswertung_tab import AuswertungTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Buchhaltungsprogramm – AIS 2026")
        self.resize(1280, 800)
        self.setStyleSheet(STYLESHEET)

        # Wrapper-Widget, weil QMainWindow kein Layout direkt bekommt
        wrapper = QWidget()
        wrapper_lay = QVBoxLayout(wrapper)
        wrapper_lay.setContentsMargins(0, 0, 0, 0)
        wrapper_lay.setSpacing(0)

        wrapper_lay.addWidget(self._build_header())
        wrapper_lay.addWidget(self._build_tabs())

        self.setCentralWidget(wrapper)
        self._build_statusbar()
        self._build_menu()

    # ── Header-Banner ────────────────────────────────────────────────────────
    def _build_header(self):
        """Gradient-Banner oben mit App-Name und Untertitel."""
        header = QWidget()
        header.setFixedHeight(64)
        # Gradient-Hintergrund über Inline-Style (geht nur auf dem Widget selbst)
        header.setStyleSheet(f"""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 {FARBEN['akzent1']}, stop:1 {FARBEN['akzent2']}
            );
        """)

        lay = QHBoxLayout(header)
        lay.setContentsMargins(20, 0, 20, 0)

        titel = QLabel("Buchhaltungsprogramm")
        titel.setStyleSheet("color: white; font-size: 22px; font-weight: bold;")

        untertitel = QLabel("AIS Schulprojekt 2026  |  Python · PyQt5 · SQLite")
        untertitel.setStyleSheet("color: rgba(255,255,255,0.75); font-size: 13px;")

        lay.addWidget(titel)
        lay.addStretch()
        lay.addWidget(untertitel)

        return header

    # ── Tab-Widget ───────────────────────────────────────────────────────────
    def _build_tabs(self):
        """Vier Tabs – jeder Tab ist eine eigene Klasse in gui/."""
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        # Tabs anlegen und als Instanzvariablen speichern,
        # damit andere Tabs sie zum Aktualisieren aufrufen können.
        self.kontenplan_tab = KontenplanTab()
        self.buchungen_tab  = BuchungenTab()
        self.anlagen_tab    = AnlagenTab()
        self.auswertung_tab = AuswertungTab()

        self.tabs.addTab(self.kontenplan_tab, "  Kontenplan  ")
        self.tabs.addTab(self.buchungen_tab,  "  Buchungen  ")
        self.tabs.addTab(self.anlagen_tab,    "  Anlagenverzeichnis  ")
        self.tabs.addTab(self.auswertung_tab, "  Auswertung / GuV  ")

        # Beim Tab-Wechsel zur Auswertung: Zahlen sofort neu laden
        self.tabs.currentChanged.connect(self._tab_gewechselt)
        return self.tabs

    # ── Statusleiste ─────────────────────────────────────────────────────────
    def _build_statusbar(self):
        sb = QStatusBar()
        self.setStatusBar(sb)
        sb.showMessage("Bereit.")
        # Permanente Info rechts in der Statusleiste
        lbl = QLabel("  DB: buchhaltung.db  ")
        sb.addPermanentWidget(lbl)

    # ── Menüleiste ───────────────────────────────────────────────────────────
    def _build_menu(self):
        mb = self.menuBar()

        # Datei-Menü
        m_datei = mb.addMenu("Datei")
        act_beenden = QAction("Beenden  Ctrl+Q", self)
        act_beenden.setShortcut("Ctrl+Q")
        act_beenden.triggered.connect(self.close)
        m_datei.addAction(act_beenden)

        # Ansicht-Menü: schnell zu jedem Tab springen
        m_ansicht = mb.addMenu("Ansicht")
        tab_namen = ["Kontenplan", "Buchungen", "Anlagenverzeichnis", "Auswertung"]
        for i, name in enumerate(tab_namen):
            act = QAction(f"{name}  Ctrl+{i+1}", self)
            act.setShortcut(f"Ctrl+{i+1}")
            act.triggered.connect(lambda _, idx=i: self.tabs.setCurrentIndex(idx))
            m_ansicht.addAction(act)

        # Hilfe-Menü
        m_hilfe = mb.addMenu("Hilfe")
        act_info = QAction("Über das Programm", self)
        act_info.triggered.connect(self._zeige_info)
        m_hilfe.addAction(act_info)

    # ── Callbacks ────────────────────────────────────────────────────────────
    def _tab_gewechselt(self, index):
        # Auswertungs-Tab (Index 3) immer frisch befüllen
        if index == 3:
            self.auswertung_tab.aktualisieren()

    def _zeige_info(self):
        QMessageBox.information(
            self, "Über",
            "Buchhaltungsprogramm\n"
            "AIS Schulprojekt 2026\n\n"
            "Technologien: Python · PyQt5 · SQLite\n\n"
            "Tabs:\n"
            "  Kontenplan          – Konten verwalten\n"
            "  Buchungen           – Buchungen erfassen & filtern\n"
            "  Anlagenverzeichnis  – Anlagen + AfA-Berechnung\n"
            "  Auswertung / GuV    – Bilanz & Gewinn/Verlust"
        )
