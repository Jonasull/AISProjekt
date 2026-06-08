from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QStatusBar, QLabel, QMenuBar, QAction,
    QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from gui.styles import STYLESHEET
from gui.kontenplan_tab import KontenplanTab
from gui.buchungen_tab import BuchungenTab
from gui.anlagen_tab import AnlagenTab
from gui.auswertung_tab import AuswertungTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Buchhaltungsprogramm – AIS Projekt 2026")
        self.resize(1200, 750)
        self.setStyleSheet(STYLESHEET)
        self._build_menu()
        self._build_tabs()
        self._build_statusbar()

    def _build_menu(self):
        mb = self.menuBar()

        m_datei = mb.addMenu("Datei")
        act_beenden = QAction("Beenden", self)
        act_beenden.setShortcut("Ctrl+Q")
        act_beenden.triggered.connect(self.close)
        m_datei.addAction(act_beenden)

        m_ansicht = mb.addMenu("Ansicht")
        for i, name in enumerate(["Kontenplan", "Buchungen", "Anlagenverzeichnis", "Auswertung"]):
            act = QAction(name, self)
            act.setShortcut(f"Ctrl+{i+1}")
            act.setData(i)
            act.triggered.connect(lambda checked, idx=i: self.tabs.setCurrentIndex(idx))
            m_ansicht.addAction(act)

        m_hilfe = mb.addMenu("Hilfe")
        act_info = QAction("Über", self)
        act_info.triggered.connect(self._zeige_info)
        m_hilfe.addAction(act_info)

    def _build_tabs(self):
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.kontenplan_tab = KontenplanTab()
        self.buchungen_tab = BuchungenTab()
        self.anlagen_tab = AnlagenTab()
        self.auswertung_tab = AuswertungTab()

        self.tabs.addTab(self.kontenplan_tab, "Kontenplan")
        self.tabs.addTab(self.buchungen_tab, "Buchungen")
        self.tabs.addTab(self.anlagen_tab, "Anlagenverzeichnis")
        self.tabs.addTab(self.auswertung_tab, "Auswertung / GuV")

        self.tabs.currentChanged.connect(self._tab_gewechselt)
        self.setCentralWidget(self.tabs)

    def _build_statusbar(self):
        sb = QStatusBar()
        self.setStatusBar(sb)
        sb.showMessage("Bereit.")
        self._lbl_db = QLabel("  DB: buchhaltung.db  ")
        sb.addPermanentWidget(self._lbl_db)

    def _tab_gewechselt(self, index):
        if index == 3:  # Auswertung
            self.auswertung_tab.aktualisieren()

    def _zeige_info(self):
        QMessageBox.information(
            self, "Über",
            "Buchhaltungsprogramm\n"
            "AIS Schulprojekt 2026\n\n"
            "Technologien: Python · PyQt5 · SQLite\n"
            "Funktionen: Kontenplan, Buchungserfassung,\n"
            "Anlagenverzeichnis, Bilanz & GuV"
        )
