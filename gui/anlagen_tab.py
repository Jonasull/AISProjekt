from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QGroupBox, QFormLayout, QLineEdit, QComboBox,
    QDoubleSpinBox, QSpinBox, QDateEdit, QTextEdit, QMessageBox,
    QHeaderView, QLabel, QDialog, QDialogButtonBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
import database


class AnlagenDialog(QDialog):
    """Dialog zum Erfassen / Bearbeiten einer Anlage."""

    def __init__(self, parent=None, anlage_data=None):
        super().__init__(parent)
        self.setWindowTitle("Anlage bearbeiten" if anlage_data else "Neue Anlage")
        self.setMinimumWidth(480)
        self._build_ui()
        self._lade_konten()
        if anlage_data:
            self._befuellen(anlage_data)

    def _build_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()
        form.setSpacing(10)

        self.inp_bez = QLineEdit()
        self.inp_bez.setPlaceholderText("z.B. Laptop Dell XPS 15")

        self.inp_datum = QDateEdit(QDate.currentDate())
        self.inp_datum.setCalendarPopup(True)
        self.inp_datum.setDisplayFormat("dd.MM.yyyy")

        self.inp_kosten = QDoubleSpinBox()
        self.inp_kosten.setRange(0.01, 99_999_999.99)
        self.inp_kosten.setDecimals(2)
        self.inp_kosten.setSuffix(" €")

        self.inp_nutzung = QSpinBox()
        self.inp_nutzung.setRange(1, 100)
        self.inp_nutzung.setSuffix(" Jahre")
        self.inp_nutzung.setValue(5)

        self.inp_restwert = QDoubleSpinBox()
        self.inp_restwert.setRange(0.00, 99_999_999.99)
        self.inp_restwert.setDecimals(2)
        self.inp_restwert.setSuffix(" €")

        self.cmb_konto = QComboBox()

        self.inp_notizen = QTextEdit()
        self.inp_notizen.setMaximumHeight(80)
        self.inp_notizen.setPlaceholderText("Optionale Notizen …")

        # Live-Berechnung Abschreibung
        self.lbl_afa = QLabel("Abschreibung p.a.: —")
        self.lbl_afa.setStyleSheet("color: #409eff; font-weight: bold;")
        self.inp_kosten.valueChanged.connect(self._update_afa)
        self.inp_nutzung.valueChanged.connect(self._update_afa)
        self.inp_restwert.valueChanged.connect(self._update_afa)

        form.addRow("Bezeichnung *:", self.inp_bez)
        form.addRow("Anschaffungsdatum *:", self.inp_datum)
        form.addRow("Anschaffungskosten *:", self.inp_kosten)
        form.addRow("Nutzungsdauer *:", self.inp_nutzung)
        form.addRow("Restwert:", self.inp_restwert)
        form.addRow("", self.lbl_afa)
        form.addRow("Konto:", self.cmb_konto)
        form.addRow("Notizen:", self.inp_notizen)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _lade_konten(self):
        self.cmb_konto.clear()
        self.cmb_konto.addItem("— kein Konto —", None)
        for k in database.get_alle_konten():
            if k["konto_typ"] == "Aktiva":
                self.cmb_konto.addItem(f"{k['konto_nr']} – {k['bezeichnung']}", k["konto_nr"])

    def _befuellen(self, d):
        self.inp_bez.setText(d["bezeichnung"])
        datum = QDate.fromString(d["anschaffungsdatum"], "yyyy-MM-dd")
        self.inp_datum.setDate(datum)
        self.inp_kosten.setValue(d["anschaffungskosten"])
        self.inp_nutzung.setValue(d["nutzungsdauer"])
        self.inp_restwert.setValue(d["restwert"])
        if d["konto_nr"]:
            idx = self.cmb_konto.findData(d["konto_nr"])
            if idx >= 0:
                self.cmb_konto.setCurrentIndex(idx)
        self.inp_notizen.setPlainText(d["notizen"] or "")
        self._update_afa()

    def _update_afa(self):
        try:
            afa = (self.inp_kosten.value() - self.inp_restwert.value()) / self.inp_nutzung.value()
            self.lbl_afa.setText(f"Abschreibung p.a.: {afa:,.2f} €")
        except ZeroDivisionError:
            self.lbl_afa.setText("Abschreibung p.a.: —")

    def get_data(self):
        return {
            "bezeichnung":        self.inp_bez.text().strip(),
            "anschaffungsdatum":  self.inp_datum.date().toString("yyyy-MM-dd"),
            "anschaffungskosten": self.inp_kosten.value(),
            "nutzungsdauer":      self.inp_nutzung.value(),
            "restwert":           self.inp_restwert.value(),
            "konto_nr":           self.cmb_konto.currentData(),
            "notizen":            self.inp_notizen.toPlainText().strip(),
        }

    def validate(self):
        d = self.get_data()
        if not d["bezeichnung"]:
            QMessageBox.warning(self, "Pflichtfeld", "Bitte eine Bezeichnung eingeben.")
            return False
        if d["anschaffungskosten"] <= 0:
            QMessageBox.warning(self, "Ungültig", "Anschaffungskosten müssen > 0 sein.")
            return False
        if d["restwert"] >= d["anschaffungskosten"]:
            QMessageBox.warning(self, "Ungültig", "Restwert muss kleiner als Anschaffungskosten sein.")
            return False
        return True

    def accept(self):
        if self.validate():
            super().accept()


class AnlagenTab(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.lade_anlagen()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Kopfzeile mit Aktionsknöpfen
        btn_row = QHBoxLayout()
        self.btn_neu = QPushButton("+ Neue Anlage")
        self.btn_neu.setObjectName("btn_success")
        self.btn_bearbeiten = QPushButton("Bearbeiten")
        self.btn_bearbeiten.setObjectName("btn_warning")
        self.btn_loeschen = QPushButton("Löschen")
        self.btn_loeschen.setObjectName("btn_danger")
        self.btn_afa_buchen = QPushButton("AfA buchen")

        btn_row.addWidget(self.btn_neu)
        btn_row.addWidget(self.btn_bearbeiten)
        btn_row.addWidget(self.btn_loeschen)
        btn_row.addWidget(self.btn_afa_buchen)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Tabelle
        self.tabelle = QTableWidget()
        self.tabelle.setColumnCount(9)
        self.tabelle.setHorizontalHeaderLabels([
            "ID", "Bezeichnung", "Anschaffung", "Kosten (€)",
            "ND (J)", "Restwert (€)", "AfA p.a. (€)", "Konto", "Notizen"
        ])
        self.tabelle.setColumnHidden(0, True)
        self.tabelle.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabelle.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabelle.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabelle.setAlternatingRowColors(True)
        self.tabelle.verticalHeader().setVisible(False)
        layout.addWidget(self.tabelle)

        # Summenzeile
        sum_row = QHBoxLayout()
        self.lbl_gesamt_kosten = QLabel("Gesamt-AK: 0,00 €")
        self.lbl_gesamt_afa = QLabel("Gesamt-AfA p.a.: 0,00 €")
        for lbl in (self.lbl_gesamt_kosten, self.lbl_gesamt_afa):
            lbl.setStyleSheet("font-weight: bold; font-size: 13px; color: #409eff;")
        sum_row.addStretch()
        sum_row.addWidget(self.lbl_gesamt_kosten)
        sum_row.addWidget(QLabel("  |  "))
        sum_row.addWidget(self.lbl_gesamt_afa)
        layout.addLayout(sum_row)

        # Verbindungen
        self.btn_neu.clicked.connect(self._neu)
        self.btn_bearbeiten.clicked.connect(self._bearbeiten)
        self.btn_loeschen.clicked.connect(self._loeschen)
        self.btn_afa_buchen.clicked.connect(self._afa_buchen)
        self.tabelle.doubleClicked.connect(self._bearbeiten)

    def lade_anlagen(self):
        anlagen = database.get_alle_anlagen()
        self.tabelle.setRowCount(len(anlagen))
        gesamt_ak = gesamt_afa = 0.0
        for row, a in enumerate(anlagen):
            datum_anzeige = self._fmt_datum(a["anschaffungsdatum"])
            items = [
                QTableWidgetItem(str(a["anlage_id"])),
                QTableWidgetItem(a["bezeichnung"]),
                QTableWidgetItem(datum_anzeige),
                QTableWidgetItem(f"{a['anschaffungskosten']:,.2f}"),
                QTableWidgetItem(str(a["nutzungsdauer"])),
                QTableWidgetItem(f"{a['restwert']:,.2f}"),
                QTableWidgetItem(f"{a['abschreibung_pa']:,.2f}"),
                QTableWidgetItem(f"{a['konto_nr'] or ''} {a['konto_bez']}".strip()),
                QTableWidgetItem(a["notizen"] or ""),
            ]
            for col in (3, 5, 6):
                items[col].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            for col, item in enumerate(items):
                self.tabelle.setItem(row, col, item)
            gesamt_ak += a["anschaffungskosten"]
            gesamt_afa += a["abschreibung_pa"]

        self.tabelle.resizeColumnsToContents()
        self.tabelle.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.lbl_gesamt_kosten.setText(f"Gesamt-AK: {gesamt_ak:,.2f} €")
        self.lbl_gesamt_afa.setText(f"Gesamt-AfA p.a.: {gesamt_afa:,.2f} €")

    def _neu(self):
        dlg = AnlagenDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            d = dlg.get_data()
            try:
                database.anlage_hinzufuegen(**d)
                self.window().statusBar().showMessage(
                    f"Anlage '{d['bezeichnung']}' hinzugefügt.", 3000
                )
                self.lade_anlagen()
            except Exception as e:
                QMessageBox.critical(self, "Fehler", str(e))

    def _bearbeiten(self):
        row = self.tabelle.currentRow()
        if row < 0:
            QMessageBox.information(self, "Hinweis", "Bitte eine Anlage auswählen.")
            return
        aid = int(self.tabelle.item(row, 0).text())
        anlagen = database.get_alle_anlagen()
        anlage = next((a for a in anlagen if a["anlage_id"] == aid), None)
        if not anlage:
            return
        dlg = AnlagenDialog(self, anlage)
        if dlg.exec_() == QDialog.Accepted:
            d = dlg.get_data()
            try:
                database.anlage_aktualisieren(aid, **d)
                self.window().statusBar().showMessage(
                    f"Anlage '{d['bezeichnung']}' aktualisiert.", 3000
                )
                self.lade_anlagen()
            except Exception as e:
                QMessageBox.critical(self, "Fehler", str(e))

    def _loeschen(self):
        row = self.tabelle.currentRow()
        if row < 0:
            QMessageBox.information(self, "Hinweis", "Bitte eine Anlage auswählen.")
            return
        aid = int(self.tabelle.item(row, 0).text())
        bez = self.tabelle.item(row, 1).text()
        antwort = QMessageBox.question(
            self, "Löschen bestätigen",
            f"Anlage '{bez}' wirklich löschen?",
            QMessageBox.Yes | QMessageBox.No
        )
        if antwort == QMessageBox.Yes:
            try:
                database.anlage_loeschen(aid)
                self.window().statusBar().showMessage(f"Anlage '{bez}' gelöscht.", 3000)
                self.lade_anlagen()
            except Exception as e:
                QMessageBox.critical(self, "Fehler", str(e))

    def _afa_buchen(self):
        """Bucht die jährliche Abschreibung aller Anlagen."""
        anlagen = database.get_alle_anlagen()
        if not anlagen:
            QMessageBox.information(self, "Keine Anlagen", "Es sind keine Anlagen vorhanden.")
            return
        antwort = QMessageBox.question(
            self, "AfA buchen",
            f"Jahresabschreibung für {len(anlagen)} Anlage(n) buchen?",
            QMessageBox.Yes | QMessageBox.No
        )
        if antwort != QMessageBox.Yes:
            return
        fehler = []
        gebucht = 0
        from datetime import date as dt
        for a in anlagen:
            if not a["konto_nr"]:
                fehler.append(f"'{a['bezeichnung']}': kein Konto zugewiesen")
                continue
            try:
                database.buchung_einfuegen(
                    datum=dt.today().isoformat(),
                    belegnummer="AfA",
                    beschreibung=f"Abschreibung {a['bezeichnung']}",
                    soll_konto="4800",
                    haben_konto=a["konto_nr"],
                    betrag=a["abschreibung_pa"],
                )
                gebucht += 1
            except Exception as e:
                fehler.append(f"'{a['bezeichnung']}': {e}")

        msg = f"{gebucht} Buchung(en) erfolgreich erstellt."
        if fehler:
            msg += "\n\nFehler:\n" + "\n".join(fehler)
        QMessageBox.information(self, "AfA gebucht", msg)
        if hasattr(self.window(), "kontenplan_tab"):
            self.window().kontenplan_tab.lade_konten()
        if hasattr(self.window(), "buchungen_tab"):
            self.window().buchungen_tab.lade_buchungen()

    @staticmethod
    def _fmt_datum(iso):
        try:
            y, m, d = iso.split("-")
            return f"{d}.{m}.{y}"
        except Exception:
            return iso
