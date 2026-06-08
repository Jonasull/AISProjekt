from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QGroupBox, QFormLayout, QLineEdit, QComboBox,
    QMessageBox, QHeaderView, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import database


TYPEN = ["Aktiva", "Passiva", "Aufwand", "Ertrag"]

TYP_FARBE = {
    "Aktiva":  "#e1f3d8",
    "Passiva": "#fde2e2",
    "Aufwand": "#fdf6ec",
    "Ertrag":  "#d9ecff",
}


class KontenplanTab(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.lade_konten()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # ── Eingabeformular ──────────────────────────────────────────────────
        form_box = QGroupBox("Konto hinzufügen / bearbeiten")
        form_lay = QFormLayout(form_box)
        form_lay.setSpacing(8)

        self.inp_nr = QLineEdit()
        self.inp_nr.setPlaceholderText("z.B. 1000")
        self.inp_bez = QLineEdit()
        self.inp_bez.setPlaceholderText("z.B. Kasse")
        self.inp_typ = QComboBox()
        self.inp_typ.addItems(TYPEN)

        form_lay.addRow("Konto-Nr.:", self.inp_nr)
        form_lay.addRow("Bezeichnung:", self.inp_bez)
        form_lay.addRow("Kontotyp:", self.inp_typ)

        btn_row = QHBoxLayout()
        self.btn_speichern = QPushButton("Speichern")
        self.btn_speichern.setObjectName("btn_success")
        self.btn_loeschen = QPushButton("Löschen")
        self.btn_loeschen.setObjectName("btn_danger")
        self.btn_neu = QPushButton("Neu")
        btn_row.addWidget(self.btn_speichern)
        btn_row.addWidget(self.btn_loeschen)
        btn_row.addWidget(self.btn_neu)
        btn_row.addStretch()
        form_lay.addRow(btn_row)

        layout.addWidget(form_box)

        # ── Tabelle ──────────────────────────────────────────────────────────
        self.tabelle = QTableWidget()
        self.tabelle.setColumnCount(4)
        self.tabelle.setHorizontalHeaderLabels(["Konto-Nr.", "Bezeichnung", "Typ", "Saldo (€)"])
        self.tabelle.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabelle.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabelle.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabelle.setAlternatingRowColors(True)
        self.tabelle.verticalHeader().setVisible(False)
        layout.addWidget(self.tabelle)

        # Verbindungen
        self.btn_speichern.clicked.connect(self._speichern)
        self.btn_loeschen.clicked.connect(self._loeschen)
        self.btn_neu.clicked.connect(self._neu)
        self.tabelle.itemSelectionChanged.connect(self._auswahl_geaendert)

        self._edit_modus = False  # True = bestehend bearbeiten

    def lade_konten(self):
        konten = database.get_alle_konten()
        self.tabelle.setRowCount(len(konten))
        for row, k in enumerate(konten):
            farbe = QColor(TYP_FARBE.get(k["konto_typ"], "#ffffff"))
            items = [
                QTableWidgetItem(k["konto_nr"]),
                QTableWidgetItem(k["bezeichnung"]),
                QTableWidgetItem(k["konto_typ"]),
                QTableWidgetItem(f"{k['saldo']:,.2f}"),
            ]
            items[3].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            for col, item in enumerate(items):
                item.setBackground(farbe)
                self.tabelle.setItem(row, col, item)
        self.tabelle.resizeColumnsToContents()
        self.tabelle.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

    def _speichern(self):
        nr = self.inp_nr.text().strip()
        bez = self.inp_bez.text().strip()
        typ = self.inp_typ.currentText()

        if not nr or not bez:
            QMessageBox.warning(self, "Eingabe fehlt", "Konto-Nr. und Bezeichnung sind Pflichtfelder.")
            return

        try:
            if self._edit_modus:
                database.konto_aktualisieren(nr, bez, typ)
                self.window().statusBar().showMessage(f"Konto {nr} aktualisiert.", 3000)
            else:
                database.konto_hinzufuegen(nr, bez, typ)
                self.window().statusBar().showMessage(f"Konto {nr} hinzugefügt.", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", str(e))
            return

        self._neu()
        self.lade_konten()

    def _loeschen(self):
        row = self.tabelle.currentRow()
        if row < 0:
            return
        nr = self.tabelle.item(row, 0).text()
        antwort = QMessageBox.question(
            self, "Löschen bestätigen",
            f"Konto {nr} wirklich löschen?\nAlle verknüpften Buchungen bleiben erhalten.",
            QMessageBox.Yes | QMessageBox.No
        )
        if antwort == QMessageBox.Yes:
            try:
                database.konto_loeschen(nr)
                self.window().statusBar().showMessage(f"Konto {nr} gelöscht.", 3000)
                self._neu()
                self.lade_konten()
            except Exception as e:
                QMessageBox.critical(self, "Fehler", str(e))

    def _neu(self):
        self.inp_nr.clear()
        self.inp_bez.clear()
        self.inp_typ.setCurrentIndex(0)
        self.inp_nr.setReadOnly(False)
        self._edit_modus = False
        self.tabelle.clearSelection()

    def _auswahl_geaendert(self):
        row = self.tabelle.currentRow()
        if row < 0:
            return
        self.inp_nr.setText(self.tabelle.item(row, 0).text())
        self.inp_bez.setText(self.tabelle.item(row, 1).text())
        typ = self.tabelle.item(row, 2).text()
        self.inp_typ.setCurrentText(typ)
        self.inp_nr.setReadOnly(True)
        self._edit_modus = True
