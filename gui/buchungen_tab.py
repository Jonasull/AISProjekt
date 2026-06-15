from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QGroupBox, QFormLayout, QLineEdit, QComboBox,
    QDoubleSpinBox, QDateEdit, QMessageBox, QHeaderView, QLabel
)
from PyQt5.QtCore import Qt, QDate
import database


class BuchungenTab(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self._lade_konten_combo()   # Dropdowns mit Konten füllen
        self.lade_buchungen()       # Tabelle befüllen

    # ── UI aufbauen ──────────────────────────────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # ── Eingabe-Karte ────────────────────────────────────────────────────
        form_box = QGroupBox("Neue Buchung erfassen")
        form_lay = QFormLayout(form_box)
        form_lay.setSpacing(10)

        self.inp_datum = QDateEdit(QDate.currentDate())
        self.inp_datum.setCalendarPopup(True)
        self.inp_datum.setDisplayFormat("dd.MM.yyyy")

        self.inp_beleg = QLineEdit(placeholderText="Belegnummer (optional)")
        self.inp_beschr = QLineEdit(placeholderText="Was wurde gebucht? z.B. Kauf Büromaterial")

        # Soll/Haben – beide Dropdowns zeigen alle Konten
        self.cmb_soll  = QComboBox(); self.cmb_soll.setMinimumWidth(280)
        self.cmb_haben = QComboBox(); self.cmb_haben.setMinimumWidth(280)

        self.inp_betrag = QDoubleSpinBox()
        self.inp_betrag.setRange(0.01, 99_999_999.99)
        self.inp_betrag.setDecimals(2)
        self.inp_betrag.setSuffix(" €")

        form_lay.addRow("Datum:",        self.inp_datum)
        form_lay.addRow("Beleg-Nr.:",    self.inp_beleg)
        form_lay.addRow("Beschreibung:", self.inp_beschr)
        form_lay.addRow("Soll-Konto:",   self.cmb_soll)
        form_lay.addRow("Haben-Konto:",  self.cmb_haben)
        form_lay.addRow("Betrag:",       self.inp_betrag)

        btn_row = QHBoxLayout()
        self.btn_buchen   = QPushButton("Buchen");         self.btn_buchen.setObjectName("btn_success")
        self.btn_loeschen = QPushButton("Buchung löschen"); self.btn_loeschen.setObjectName("btn_danger")
        self.btn_reset    = QPushButton("Zurücksetzen")
        btn_row.addWidget(self.btn_buchen)
        btn_row.addWidget(self.btn_loeschen)
        btn_row.addWidget(self.btn_reset)
        btn_row.addStretch()
        form_lay.addRow(btn_row)

        layout.addWidget(form_box)

        # ── Filter-Karte ─────────────────────────────────────────────────────
        filter_box = QGroupBox("Filter")
        filter_lay = QHBoxLayout(filter_box)

        self.flt_von = QDateEdit(QDate.currentDate().addMonths(-1))
        self.flt_von.setCalendarPopup(True)
        self.flt_von.setDisplayFormat("dd.MM.yyyy")

        self.flt_bis = QDateEdit(QDate.currentDate())
        self.flt_bis.setCalendarPopup(True)
        self.flt_bis.setDisplayFormat("dd.MM.yyyy")

        self.flt_konto = QComboBox()
        self.flt_konto.addItem("Alle Konten", None)

        self.btn_filter       = QPushButton("Filtern")
        self.btn_filter_reset = QPushButton("Alle anzeigen")

        for widget in (QLabel("Von:"), self.flt_von, QLabel("Bis:"), self.flt_bis,
                       QLabel("Konto:"), self.flt_konto,
                       self.btn_filter, self.btn_filter_reset):
            filter_lay.addWidget(widget)
        filter_lay.addStretch()

        layout.addWidget(filter_box)

        # ── Buchungs-Tabelle ─────────────────────────────────────────────────
        self.tabelle = QTableWidget()
        self.tabelle.setColumnCount(7)
        self.tabelle.setHorizontalHeaderLabels(
            ["ID", "Datum", "Beleg", "Beschreibung", "Soll", "Haben", "Betrag (€)"]
        )
        self.tabelle.setColumnHidden(0, True)                                    # ID intern, nicht anzeigen
        self.tabelle.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tabelle.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabelle.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabelle.setAlternatingRowColors(True)
        self.tabelle.verticalHeader().setVisible(False)
        layout.addWidget(self.tabelle)

        # Gesamtsumme der angezeigten Buchungen
        sum_row = QHBoxLayout()
        self.lbl_summe = QLabel("Summe: 0,00 €")
        self.lbl_summe.setStyleSheet(
            "font-weight: bold; font-size: 14px; color: #6c63ff;"
        )
        sum_row.addStretch()
        sum_row.addWidget(self.lbl_summe)
        layout.addLayout(sum_row)

        # Signale verbinden
        self.btn_buchen.clicked.connect(self._buchen)
        self.btn_loeschen.clicked.connect(self._loeschen)
        self.btn_reset.clicked.connect(self._reset_form)
        self.btn_filter.clicked.connect(self.lade_buchungen)
        self.btn_filter_reset.clicked.connect(self._filter_reset)

    # ── Hilfsmethoden ────────────────────────────────────────────────────────
    def _lade_konten_combo(self):
        """Alle Konten in Soll/Haben-Dropdowns und im Filter eintragen."""
        konten = database.get_alle_konten()
        for cmb in (self.cmb_soll, self.cmb_haben):
            cmb.clear()
        for k in konten:
            label = f"{k['konto_nr']} – {k['bezeichnung']}"
            self.cmb_soll.addItem(label, k["konto_nr"])
            self.cmb_haben.addItem(label, k["konto_nr"])
            self.flt_konto.addItem(label, k["konto_nr"])

    def lade_buchungen(self):
        """Buchungen aus der DB holen (mit aktivem Filter) und anzeigen."""
        von   = self.flt_von.date().toString("yyyy-MM-dd")
        bis   = self.flt_bis.date().toString("yyyy-MM-dd")
        konto = self.flt_konto.currentData()   # None = kein Filter

        buchungen = database.get_alle_buchungen(von, bis, konto)
        self.tabelle.setRowCount(len(buchungen))
        gesamt = 0.0

        for row, b in enumerate(buchungen):
            items = [
                QTableWidgetItem(str(b["buchungs_id"])),
                QTableWidgetItem(self._iso_zu_de(b["datum"])),
                QTableWidgetItem(b["belegnummer"] or ""),
                QTableWidgetItem(b["beschreibung"]),
                QTableWidgetItem(f"{b['soll_konto']}  {b['soll_bez']}"),
                QTableWidgetItem(f"{b['haben_konto']}  {b['haben_bez']}"),
                QTableWidgetItem(f"{b['betrag']:,.2f}"),
            ]
            items[6].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            for col, item in enumerate(items):
                self.tabelle.setItem(row, col, item)
            gesamt += b["betrag"]

        self.tabelle.resizeColumnsToContents()
        self.tabelle.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.lbl_summe.setText(f"Summe: {gesamt:,.2f} €")

    # ── Aktionen ─────────────────────────────────────────────────────────────
    def _buchen(self):
        """Eingaben validieren und neue Buchung in die DB schreiben."""
        datum  = self.inp_datum.date().toString("yyyy-MM-dd")
        beleg  = self.inp_beleg.text().strip()
        beschr = self.inp_beschr.text().strip()
        soll   = self.cmb_soll.currentData()
        haben  = self.cmb_haben.currentData()
        betrag = self.inp_betrag.value()

        # Validierung
        if not beschr:
            QMessageBox.warning(self, "Fehlende Eingabe", "Bitte eine Beschreibung eingeben.")
            return
        if soll == haben:
            QMessageBox.warning(self, "Ungültig",
                                "Soll- und Haben-Konto dürfen nicht gleich sein.")
            return
        if betrag <= 0:
            QMessageBox.warning(self, "Ungültig", "Betrag muss größer als 0 sein.")
            return

        try:
            database.buchung_einfuegen(datum, beleg, beschr, soll, haben, betrag)
            self.window().statusBar().showMessage(
                f"'{beschr}'  –  {betrag:,.2f} € gebucht.", 4000
            )
            self._reset_form()
            self.lade_buchungen()
            # Kontenplan-Salden aktualisieren (Soll/Haben-Saldo hat sich geändert)
            if hasattr(self.window(), "kontenplan_tab"):
                self.window().kontenplan_tab.lade_konten()
        except Exception as e:
            QMessageBox.critical(self, "DB-Fehler", str(e))

    def _loeschen(self):
        """Ausgewählte Buchung löschen + Kontosalden automatisch korrigieren."""
        row = self.tabelle.currentRow()
        if row < 0:
            QMessageBox.information(self, "Hinweis", "Bitte zuerst eine Buchung auswählen.")
            return

        bid   = int(self.tabelle.item(row, 0).text())
        beschr = self.tabelle.item(row, 3).text()

        antwort = QMessageBox.question(
            self, "Buchung löschen",
            f"'{beschr}' wirklich löschen?\n"
            "Die Kontosalden werden automatisch korrigiert.",
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
                QMessageBox.critical(self, "DB-Fehler", str(e))

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
    def _iso_zu_de(datum_iso):
        """'2026-06-15' → '15.06.2026'"""
        try:
            y, m, d = datum_iso.split("-")
            return f"{d}.{m}.{y}"
        except Exception:
            return datum_iso
