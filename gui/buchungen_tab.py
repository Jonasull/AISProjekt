from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QGroupBox, QFormLayout, QLineEdit, QComboBox,
    QDoubleSpinBox, QDateEdit, QMessageBox, QHeaderView, QLabel,
    QSizePolicy
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor
import database


class BuchungenTab(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self._lade_konten_combo()
        self.lade_buchungen()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # ── Buchungsformular ─────────────────────────────────────────────────
        form_box = QGroupBox("Neue Buchung erfassen")
        form_lay = QFormLayout(form_box)
        form_lay.setSpacing(8)

        self.inp_datum = QDateEdit(QDate.currentDate())
        self.inp_datum.setCalendarPopup(True)
        self.inp_datum.setDisplayFormat("dd.MM.yyyy")

        self.inp_beleg = QLineEdit()
        self.inp_beleg.setPlaceholderText("Belegnummer (optional)")

        self.inp_beschr = QLineEdit()
        self.inp_beschr.setPlaceholderText("Buchungstext / Beschreibung")

        self.cmb_soll = QComboBox()
        self.cmb_soll.setMinimumWidth(280)
        self.cmb_haben = QComboBox()
        self.cmb_haben.setMinimumWidth(280)

        self.inp_betrag = QDoubleSpinBox()
        self.inp_betrag.setRange(0.01, 99_999_999.99)
        self.inp_betrag.setDecimals(2)
        self.inp_betrag.setSuffix(" €")
        self.inp_betrag.setValue(0.00)

        form_lay.addRow("Datum:", self.inp_datum)
        form_lay.addRow("Beleg-Nr.:", self.inp_beleg)
        form_lay.addRow("Beschreibung:", self.inp_beschr)
        form_lay.addRow("Soll-Konto:", self.cmb_soll)
        form_lay.addRow("Haben-Konto:", self.cmb_haben)
        form_lay.addRow("Betrag:", self.inp_betrag)

        btn_row = QHBoxLayout()
        self.btn_buchen = QPushButton("Buchen")
        self.btn_buchen.setObjectName("btn_success")
        self.btn_loeschen = QPushButton("Buchung löschen")
        self.btn_loeschen.setObjectName("btn_danger")
        self.btn_reset = QPushButton("Zurücksetzen")
        btn_row.addWidget(self.btn_buchen)
        btn_row.addWidget(self.btn_loeschen)
        btn_row.addWidget(self.btn_reset)
        btn_row.addStretch()
        form_lay.addRow(btn_row)

        layout.addWidget(form_box)

        # ── Filter ───────────────────────────────────────────────────────────
        filter_box = QGroupBox("Filter")
        filter_lay = QHBoxLayout(filter_box)

        filter_lay.addWidget(QLabel("Von:"))
        self.flt_von = QDateEdit()
        self.flt_von.setCalendarPopup(True)
        self.flt_von.setDisplayFormat("dd.MM.yyyy")
        self.flt_von.setDate(QDate.currentDate().addMonths(-1))
        filter_lay.addWidget(self.flt_von)

        filter_lay.addWidget(QLabel("Bis:"))
        self.flt_bis = QDateEdit(QDate.currentDate())
        self.flt_bis.setCalendarPopup(True)
        self.flt_bis.setDisplayFormat("dd.MM.yyyy")
        filter_lay.addWidget(self.flt_bis)

        filter_lay.addWidget(QLabel("Konto:"))
        self.flt_konto = QComboBox()
        self.flt_konto.addItem("Alle", None)
        filter_lay.addWidget(self.flt_konto)

        self.btn_filter = QPushButton("Filtern")
        self.btn_filter_reset = QPushButton("Alle anzeigen")
        filter_lay.addWidget(self.btn_filter)
        filter_lay.addWidget(self.btn_filter_reset)
        filter_lay.addStretch()

        layout.addWidget(filter_box)

        # ── Tabelle ──────────────────────────────────────────────────────────
        self.tabelle = QTableWidget()
        self.tabelle.setColumnCount(7)
        self.tabelle.setHorizontalHeaderLabels([
            "ID", "Datum", "Beleg", "Beschreibung",
            "Soll", "Haben", "Betrag (€)"
        ])
        self.tabelle.setColumnHidden(0, True)
        self.tabelle.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tabelle.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabelle.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabelle.setAlternatingRowColors(True)
        self.tabelle.verticalHeader().setVisible(False)
        layout.addWidget(self.tabelle)

        # Summenzeile
        sum_row = QHBoxLayout()
        self.lbl_summe = QLabel("Summe: 0,00 €")
        self.lbl_summe.setStyleSheet("font-weight: bold; font-size: 14px; color: #409eff;")
        sum_row.addStretch()
        sum_row.addWidget(self.lbl_summe)
        layout.addLayout(sum_row)

        # Verbindungen
        self.btn_buchen.clicked.connect(self._buchen)
        self.btn_loeschen.clicked.connect(self._loeschen)
        self.btn_reset.clicked.connect(self._reset_form)
        self.btn_filter.clicked.connect(self.lade_buchungen)
        self.btn_filter_reset.clicked.connect(self._filter_reset)

    def _lade_konten_combo(self):
        konten = database.get_alle_konten()
        for cmb in (self.cmb_soll, self.cmb_haben):
            cmb.clear()
        for k in konten:
            label = f"{k['konto_nr']} – {k['bezeichnung']}"
            self.cmb_soll.addItem(label, k["konto_nr"])
            self.cmb_haben.addItem(label, k["konto_nr"])
            self.flt_konto.addItem(label, k["konto_nr"])

    def lade_buchungen(self):
        von = self.flt_von.date().toString("yyyy-MM-dd")
        bis = self.flt_bis.date().toString("yyyy-MM-dd")
        konto = self.flt_konto.currentData()

        buchungen = database.get_alle_buchungen(von, bis, konto)
        self.tabelle.setRowCount(len(buchungen))
        gesamt = 0.0
        for row, b in enumerate(buchungen):
            datum_anzeige = self._fmt_datum(b["datum"])
            soll_text = f"{b['soll_konto']} {b['soll_bez']}"
            haben_text = f"{b['haben_konto']} {b['haben_bez']}"
            items = [
                QTableWidgetItem(str(b["buchungs_id"])),
                QTableWidgetItem(datum_anzeige),
                QTableWidgetItem(b["belegnummer"] or ""),
                QTableWidgetItem(b["beschreibung"]),
                QTableWidgetItem(soll_text),
                QTableWidgetItem(haben_text),
                QTableWidgetItem(f"{b['betrag']:,.2f}"),
            ]
            items[6].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            for col, item in enumerate(items):
                self.tabelle.setItem(row, col, item)
            gesamt += b["betrag"]

        self.tabelle.resizeColumnsToContents()
        self.tabelle.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.lbl_summe.setText(f"Summe: {gesamt:,.2f} €")

    def _buchen(self):
        datum = self.inp_datum.date().toString("yyyy-MM-dd")
        beleg = self.inp_beleg.text().strip()
        beschr = self.inp_beschr.text().strip()
        soll = self.cmb_soll.currentData()
        haben = self.cmb_haben.currentData()
        betrag = self.inp_betrag.value()

        if not beschr:
            QMessageBox.warning(self, "Eingabe fehlt", "Bitte eine Beschreibung eingeben.")
            return
        if soll == haben:
            QMessageBox.warning(self, "Fehler", "Soll- und Haben-Konto dürfen nicht identisch sein.")
            return
        if betrag <= 0:
            QMessageBox.warning(self, "Fehler", "Betrag muss größer als 0 sein.")
            return

        try:
            database.buchung_einfuegen(datum, beleg, beschr, soll, haben, betrag)
            self.window().statusBar().showMessage(
                f"Buchung '{beschr}' über {betrag:,.2f} € erfasst.", 4000
            )
            self._reset_form()
            self.lade_buchungen()
            # Kontenplan-Salden aktualisieren
            if hasattr(self.window(), "kontenplan_tab"):
                self.window().kontenplan_tab.lade_konten()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", str(e))

    def _loeschen(self):
        row = self.tabelle.currentRow()
        if row < 0:
            QMessageBox.information(self, "Hinweis", "Bitte zuerst eine Buchung auswählen.")
            return
        bid = int(self.tabelle.item(row, 0).text())
        beschr = self.tabelle.item(row, 3).text()
        antwort = QMessageBox.question(
            self, "Buchung löschen",
            f"Buchung '{beschr}' wirklich löschen?\nDie Kontosalden werden korrigiert.",
            QMessageBox.Yes | QMessageBox.No
        )
        if antwort == QMessageBox.Yes:
            try:
                database.buchung_loeschen(bid)
                self.window().statusBar().showMessage("Buchung gelöscht.", 3000)
                self.lade_buchungen()
                if hasattr(self.window(), "kontenplan_tab"):
                    self.window().kontenplan_tab.lade_konten()
            except Exception as e:
                QMessageBox.critical(self, "Fehler", str(e))

    def _reset_form(self):
        self.inp_datum.setDate(QDate.currentDate())
        self.inp_beleg.clear()
        self.inp_beschr.clear()
        self.inp_betrag.setValue(0.00)
        self.tabelle.clearSelection()

    def _filter_reset(self):
        self.flt_von.setDate(QDate.currentDate().addMonths(-1))
        self.flt_bis.setDate(QDate.currentDate())
        self.flt_konto.setCurrentIndex(0)
        self.lade_buchungen()

    @staticmethod
    def _fmt_datum(iso):
        try:
            y, m, d = iso.split("-")
            return f"{d}.{m}.{y}"
        except Exception:
            return iso
