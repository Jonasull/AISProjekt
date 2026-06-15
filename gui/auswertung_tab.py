from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QGroupBox, QLabel, QHeaderView, QSplitter
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
import database


class AuswertungTab(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.aktualisieren()

    # ── UI aufbauen ──────────────────────────────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Aktualisieren-Button
        btn_row = QHBoxLayout()
        self.btn_refresh = QPushButton("Aktualisieren")
        btn_row.addWidget(self.btn_refresh)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Bilanz links, GuV rechts – nebeneinander mit Trennlinie
        splitter = QSplitter(Qt.Horizontal)

        splitter.addWidget(self._bilanz_widget())
        splitter.addWidget(self._guv_widget())
        splitter.setSizes([500, 500])   # Gleiche Startbreite

        layout.addWidget(splitter)
        self.btn_refresh.clicked.connect(self.aktualisieren)

    def _bilanz_widget(self):
        box = QGroupBox("Bilanz")
        lay = QVBoxLayout(box)
        self.bilanz_tbl = self._neue_tabelle()
        self.lbl_bilanz = QLabel()
        self.lbl_bilanz.setAlignment(Qt.AlignRight)
        self.lbl_bilanz.setStyleSheet("font-weight: bold; color: #6c63ff; font-size: 13px;")
        lay.addWidget(self.bilanz_tbl)
        lay.addWidget(self.lbl_bilanz)
        return box

    def _guv_widget(self):
        box = QGroupBox("Gewinn- und Verlustrechnung (GuV)")
        lay = QVBoxLayout(box)
        self.guv_tbl = self._neue_tabelle()
        self.lbl_guv = QLabel()
        self.lbl_guv.setAlignment(Qt.AlignRight)
        self.lbl_guv.setTextFormat(Qt.RichText)
        self.lbl_guv.setStyleSheet("font-weight: bold; font-size: 14px;")
        lay.addWidget(self.guv_tbl)
        lay.addWidget(self.lbl_guv)
        return box

    @staticmethod
    def _neue_tabelle():
        """Erstellt eine einheitlich konfigurierte Tabelle."""
        tbl = QTableWidget()
        tbl.setColumnCount(3)
        tbl.setHorizontalHeaderLabels(["Konto-Nr.", "Bezeichnung", "Saldo (€)"])
        tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        tbl.setAlternatingRowColors(True)
        tbl.verticalHeader().setVisible(False)
        return tbl

    # ── Daten laden ──────────────────────────────────────────────────────────
    def aktualisieren(self):
        self._lade_bilanz()
        self._lade_guv()

    def _lade_bilanz(self):
        aktiva, passiva = database.get_bilanz()

        # Abschnitte: Überschrift + Zeilen + Summenzeile
        abschnitte = [
            ("AKTIVA",  aktiva,  "#1e3a2f", "#253830"),
            ("PASSIVA", passiva, "#3a1e1e", "#382525"),
        ]
        zeilen = self._abschnitte_zu_zeilen(abschnitte)
        self._tabelle_befuellen(self.bilanz_tbl, zeilen)

        sum_a = sum(k["saldo"] for k in aktiva)
        sum_p = sum(k["saldo"] for k in passiva)
        self.lbl_bilanz.setText(
            f"Aktiva: {sum_a:,.2f} €   |   Passiva: {sum_p:,.2f} €   |   "
            f"Differenz: {sum_a - sum_p:,.2f} €"
        )

    def _lade_guv(self):
        aufwand, ertrag = database.get_guv()

        abschnitte = [
            ("ERTRÄGE",      ertrag,  "#1e3a2f", "#253830"),
            ("AUFWENDUNGEN", aufwand, "#3a321e", "#383025"),
        ]
        zeilen = self._abschnitte_zu_zeilen(abschnitte)
        self._tabelle_befuellen(self.guv_tbl, zeilen)

        sum_e = sum(k["saldo"] for k in ertrag)
        sum_a = sum(k["saldo"] for k in aufwand)
        gewinn = sum_e - sum_a
        farbe  = "#43e97b" if gewinn >= 0 else "#ff6584"
        label  = "Gewinn" if gewinn >= 0 else "Verlust"
        self.lbl_guv.setText(
            f"Erträge: {sum_e:,.2f} €  –  Aufwand: {sum_a:,.2f} €  =  "
            f"<span style='color:{farbe}'>{label}: {abs(gewinn):,.2f} €</span>"
        )

    # ── Helfer ───────────────────────────────────────────────────────────────
    @staticmethod
    def _abschnitte_zu_zeilen(abschnitte):
        """
        Wandelt eine Liste von (Titel, Konten, Kopf-Farbe, Zeilen-Farbe)
        in eine flache Zeilen-Liste um, die die Tabelle befüllen kann.
        Jede Zeile: (konto_nr, bezeichnung, saldo, hintergrundfarbe, fett?)
        """
        zeilen = []
        for titel, konten, kopf_farbe, zeilen_farbe in abschnitte:
            zeilen.append(("", titel, None, kopf_farbe, True))      # Abschnitts-Überschrift
            for k in konten:
                zeilen.append((k["konto_nr"], k["bezeichnung"], k["saldo"], zeilen_farbe, False))
            summe = sum(k["saldo"] for k in konten)
            zeilen.append(("", f"Summe {titel.capitalize()}", summe, kopf_farbe, True))
            zeilen.append(("", "", None, "#1a1d2e", False))          # Leerzeile als Trenner
        return zeilen

    @staticmethod
    def _tabelle_befuellen(tabelle, zeilen):
        tabelle.setRowCount(len(zeilen))
        for row, (nr, bez, saldo, farbe, fett) in enumerate(zeilen):
            saldo_text = f"{saldo:,.2f}" if saldo is not None else ""
            items = [
                QTableWidgetItem(nr),
                QTableWidgetItem(bez),
                QTableWidgetItem(saldo_text),
            ]
            if saldo is not None:
                items[2].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            for item in items:
                item.setBackground(QColor(farbe))
                item.setForeground(QColor("#e0e0e0"))
                if fett:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
            for col, item in enumerate(items):
                tabelle.setItem(row, col, item)
        tabelle.resizeColumnsToContents()
        tabelle.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
