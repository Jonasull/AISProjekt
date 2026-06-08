from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QGroupBox, QLabel, QHeaderView, QSplitter, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
import database


class AuswertungTab(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.aktualisieren()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        btn_row = QHBoxLayout()
        self.btn_refresh = QPushButton("Aktualisieren")
        btn_row.addWidget(self.btn_refresh)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        splitter = QSplitter(Qt.Horizontal)

        # ── Bilanz ───────────────────────────────────────────────────────────
        bilanz_box = QGroupBox("Bilanz")
        bilanz_lay = QVBoxLayout(bilanz_box)

        self.bilanz_tbl = QTableWidget()
        self.bilanz_tbl.setColumnCount(3)
        self.bilanz_tbl.setHorizontalHeaderLabels(["Konto-Nr.", "Bezeichnung", "Saldo (€)"])
        self.bilanz_tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.bilanz_tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        self.bilanz_tbl.setAlternatingRowColors(True)
        self.bilanz_tbl.verticalHeader().setVisible(False)
        bilanz_lay.addWidget(self.bilanz_tbl)

        self.lbl_bilanz_sum = QLabel()
        self.lbl_bilanz_sum.setAlignment(Qt.AlignRight)
        self.lbl_bilanz_sum.setStyleSheet("font-weight: bold; color: #409eff;")
        bilanz_lay.addWidget(self.lbl_bilanz_sum)

        splitter.addWidget(bilanz_box)

        # ── GuV ──────────────────────────────────────────────────────────────
        guv_box = QGroupBox("Gewinn- und Verlustrechnung (GuV)")
        guv_lay = QVBoxLayout(guv_box)

        self.guv_tbl = QTableWidget()
        self.guv_tbl.setColumnCount(3)
        self.guv_tbl.setHorizontalHeaderLabels(["Konto-Nr.", "Bezeichnung", "Saldo (€)"])
        self.guv_tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.guv_tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        self.guv_tbl.setAlternatingRowColors(True)
        self.guv_tbl.verticalHeader().setVisible(False)
        guv_lay.addWidget(self.guv_tbl)

        self.lbl_guv_ergebnis = QLabel()
        self.lbl_guv_ergebnis.setAlignment(Qt.AlignRight)
        self.lbl_guv_ergebnis.setStyleSheet("font-weight: bold; font-size: 14px;")
        guv_lay.addWidget(self.lbl_guv_ergebnis)

        splitter.addWidget(guv_box)
        layout.addWidget(splitter)

        self.btn_refresh.clicked.connect(self.aktualisieren)

    def aktualisieren(self):
        self._lade_bilanz()
        self._lade_guv()

    def _lade_bilanz(self):
        aktiva, passiva = database.get_bilanz()
        rows = []
        rows.append(("", "AKTIVA", None, "#dbeafe"))
        for k in aktiva:
            rows.append((k["konto_nr"], k["bezeichnung"], k["saldo"], "#eff6ff"))
        sum_aktiva = sum(k["saldo"] for k in aktiva)
        rows.append(("", f"Summe Aktiva", sum_aktiva, "#bfdbfe"))

        rows.append(("", "", None, "#ffffff"))
        rows.append(("", "PASSIVA", None, "#fee2e2"))
        for k in passiva:
            rows.append((k["konto_nr"], k["bezeichnung"], k["saldo"], "#fef2f2"))
        sum_passiva = sum(k["saldo"] for k in passiva)
        rows.append(("", "Summe Passiva", sum_passiva, "#fecaca"))

        self.bilanz_tbl.setRowCount(len(rows))
        for r, (nr, bez, saldo, farbe) in enumerate(rows):
            items = [
                QTableWidgetItem(nr),
                QTableWidgetItem(bez),
                QTableWidgetItem(f"{saldo:,.2f}" if saldo is not None else ""),
            ]
            if saldo is not None:
                items[2].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            for col, item in enumerate(items):
                item.setBackground(QColor(farbe))
                if nr == "" and saldo is not None:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                self.bilanz_tbl.setItem(r, col, item)

        self.bilanz_tbl.resizeColumnsToContents()
        self.bilanz_tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        differenz = sum_aktiva - sum_passiva
        self.lbl_bilanz_sum.setText(
            f"Aktiva: {sum_aktiva:,.2f} €  |  Passiva: {sum_passiva:,.2f} €  |  "
            f"Differenz: {differenz:,.2f} €"
        )

    def _lade_guv(self):
        aufwand, ertrag = database.get_guv()
        rows = []
        rows.append(("", "ERTRÄGE", None, "#d1fae5"))
        for k in ertrag:
            rows.append((k["konto_nr"], k["bezeichnung"], k["saldo"], "#ecfdf5"))
        sum_ertrag = sum(k["saldo"] for k in ertrag)
        rows.append(("", "Summe Erträge", sum_ertrag, "#a7f3d0"))

        rows.append(("", "", None, "#ffffff"))
        rows.append(("", "AUFWENDUNGEN", None, "#fef3c7"))
        for k in aufwand:
            rows.append((k["konto_nr"], k["bezeichnung"], k["saldo"], "#fffbeb"))
        sum_aufwand = sum(k["saldo"] for k in aufwand)
        rows.append(("", "Summe Aufwendungen", sum_aufwand, "#fde68a"))

        self.guv_tbl.setRowCount(len(rows))
        for r, (nr, bez, saldo, farbe) in enumerate(rows):
            items = [
                QTableWidgetItem(nr),
                QTableWidgetItem(bez),
                QTableWidgetItem(f"{saldo:,.2f}" if saldo is not None else ""),
            ]
            if saldo is not None:
                items[2].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            for col, item in enumerate(items):
                item.setBackground(QColor(farbe))
                if nr == "" and saldo is not None:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                self.guv_tbl.setItem(r, col, item)

        self.guv_tbl.resizeColumnsToContents()
        self.guv_tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        gewinn = sum_ertrag - sum_aufwand
        farbe_text = "#16a34a" if gewinn >= 0 else "#dc2626"
        label = "Gewinn" if gewinn >= 0 else "Verlust"
        self.lbl_guv_ergebnis.setText(
            f"Erträge: {sum_ertrag:,.2f} €  –  Aufwand: {sum_aufwand:,.2f} €  =  "
            f"<span style='color:{farbe_text}'>{label}: {abs(gewinn):,.2f} €</span>"
        )
        self.lbl_guv_ergebnis.setTextFormat(Qt.RichText)
