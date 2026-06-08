import sqlite3
import os
from datetime import date

DB_PATH = os.path.join(os.path.dirname(__file__), "buchhaltung.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS konten (
                konto_nr    TEXT PRIMARY KEY,
                bezeichnung TEXT NOT NULL,
                konto_typ   TEXT NOT NULL CHECK(konto_typ IN ('Aktiva','Passiva','Aufwand','Ertrag')),
                saldo       REAL NOT NULL DEFAULT 0.0
            );

            CREATE TABLE IF NOT EXISTS anlagen (
                anlage_id           INTEGER PRIMARY KEY AUTOINCREMENT,
                bezeichnung         TEXT NOT NULL,
                anschaffungsdatum   TEXT NOT NULL,
                anschaffungskosten  REAL NOT NULL,
                nutzungsdauer       INTEGER NOT NULL,
                restwert            REAL NOT NULL DEFAULT 0.0,
                abschreibung_pa     REAL GENERATED ALWAYS AS
                    ((anschaffungskosten - restwert) / nutzungsdauer) VIRTUAL,
                konto_nr            TEXT REFERENCES konten(konto_nr) ON UPDATE CASCADE,
                notizen             TEXT
            );

            CREATE TABLE IF NOT EXISTS buchungen (
                buchungs_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                datum           TEXT NOT NULL,
                belegnummer     TEXT,
                beschreibung    TEXT NOT NULL,
                soll_konto      TEXT NOT NULL REFERENCES konten(konto_nr),
                haben_konto     TEXT NOT NULL REFERENCES konten(konto_nr),
                betrag          REAL NOT NULL CHECK(betrag > 0)
            );

            CREATE TABLE IF NOT EXISTS buchungs_positionen (
                position_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                buchungs_id     INTEGER NOT NULL REFERENCES buchungen(buchungs_id) ON DELETE CASCADE,
                konto_nr        TEXT NOT NULL REFERENCES konten(konto_nr),
                seite           TEXT NOT NULL CHECK(seite IN ('Soll','Haben')),
                betrag          REAL NOT NULL
            );
        """)
        _seed_kontenplan(conn)


def _seed_kontenplan(conn):
    existing = conn.execute("SELECT COUNT(*) FROM konten").fetchone()[0]
    if existing > 0:
        return
    konten = [
        # Aktiva
        ("0200", "Gebäude",                   "Aktiva"),
        ("0400", "Maschinen",                 "Aktiva"),
        ("0600", "Fuhrpark",                  "Aktiva"),
        ("0700", "EDV-Anlagen",               "Aktiva"),
        ("1000", "Kasse",                     "Aktiva"),
        ("1200", "Bank",                      "Aktiva"),
        ("2000", "Forderungen aus L&L",       "Aktiva"),
        ("2800", "Vorräte",                   "Aktiva"),
        # Passiva
        ("3000", "Verbindlichkeiten aus L&L", "Passiva"),
        ("3500", "Bankdarlehen",              "Passiva"),
        ("9000", "Eigenkapital",              "Passiva"),
        # Aufwand
        ("4000", "Materialaufwand",           "Aufwand"),
        ("4200", "Personalaufwand",           "Aufwand"),
        ("4800", "Abschreibungen",            "Aufwand"),
        ("4900", "Sonstiger Aufwand",         "Aufwand"),
        # Ertrag
        ("8000", "Umsatzerlöse",              "Ertrag"),
        ("8100", "Sonstige Erträge",          "Ertrag"),
    ]
    conn.executemany(
        "INSERT INTO konten(konto_nr, bezeichnung, konto_typ) VALUES (?,?,?)",
        konten
    )


# ── Konten ────────────────────────────────────────────────────────────────────

def get_alle_konten():
    with get_connection() as conn:
        return conn.execute(
            "SELECT konto_nr, bezeichnung, konto_typ, saldo FROM konten ORDER BY konto_nr"
        ).fetchall()


def konto_hinzufuegen(konto_nr, bezeichnung, konto_typ):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO konten(konto_nr, bezeichnung, konto_typ) VALUES (?,?,?)",
            (konto_nr, bezeichnung, konto_typ)
        )


def konto_loeschen(konto_nr):
    with get_connection() as conn:
        conn.execute("DELETE FROM konten WHERE konto_nr=?", (konto_nr,))


def konto_aktualisieren(konto_nr, bezeichnung, konto_typ):
    with get_connection() as conn:
        conn.execute(
            "UPDATE konten SET bezeichnung=?, konto_typ=? WHERE konto_nr=?",
            (bezeichnung, konto_typ, konto_nr)
        )


# ── Buchungen ─────────────────────────────────────────────────────────────────

def buchung_einfuegen(datum, belegnummer, beschreibung, soll_konto, haben_konto, betrag):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO buchungen(datum, belegnummer, beschreibung, soll_konto, haben_konto, betrag)
               VALUES (?,?,?,?,?,?)""",
            (datum, belegnummer, beschreibung, soll_konto, haben_konto, betrag)
        )
        # Salden aktualisieren
        _update_saldo(conn, soll_konto, betrag, "Soll")
        _update_saldo(conn, haben_konto, betrag, "Haben")


def _update_saldo(conn, konto_nr, betrag, seite):
    row = conn.execute("SELECT konto_typ FROM konten WHERE konto_nr=?", (konto_nr,)).fetchone()
    if not row:
        return
    typ = row["konto_typ"]
    # Aktivkonten: Soll + / Haben -
    # Passiv-/Ertragskonten: Haben + / Soll -
    if typ in ("Aktiva", "Aufwand"):
        delta = betrag if seite == "Soll" else -betrag
    else:
        delta = betrag if seite == "Haben" else -betrag
    conn.execute("UPDATE konten SET saldo = saldo + ? WHERE konto_nr=?", (delta, konto_nr))


def get_alle_buchungen(von=None, bis=None, konto_filter=None):
    sql = """
        SELECT b.buchungs_id, b.datum, b.belegnummer, b.beschreibung,
               b.soll_konto, ks.bezeichnung AS soll_bez,
               b.haben_konto, kh.bezeichnung AS haben_bez,
               b.betrag
        FROM buchungen b
        JOIN konten ks ON b.soll_konto = ks.konto_nr
        JOIN konten kh ON b.haben_konto = kh.konto_nr
        WHERE 1=1
    """
    params = []
    if von:
        sql += " AND b.datum >= ?"
        params.append(von)
    if bis:
        sql += " AND b.datum <= ?"
        params.append(bis)
    if konto_filter:
        sql += " AND (b.soll_konto=? OR b.haben_konto=?)"
        params += [konto_filter, konto_filter]
    sql += " ORDER BY b.datum DESC, b.buchungs_id DESC"
    with get_connection() as conn:
        return conn.execute(sql, params).fetchall()


def buchung_loeschen(buchungs_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT soll_konto, haben_konto, betrag FROM buchungen WHERE buchungs_id=?",
            (buchungs_id,)
        ).fetchone()
        if row:
            _update_saldo(conn, row["soll_konto"], row["betrag"], "Haben")  # Rückbuchung
            _update_saldo(conn, row["haben_konto"], row["betrag"], "Soll")
            conn.execute("DELETE FROM buchungen WHERE buchungs_id=?", (buchungs_id,))


# ── Anlagenverzeichnis ────────────────────────────────────────────────────────

def anlage_hinzufuegen(bezeichnung, anschaffungsdatum, anschaffungskosten,
                       nutzungsdauer, restwert, konto_nr, notizen):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO anlagen(bezeichnung, anschaffungsdatum, anschaffungskosten,
               nutzungsdauer, restwert, konto_nr, notizen)
               VALUES (?,?,?,?,?,?,?)""",
            (bezeichnung, anschaffungsdatum, anschaffungskosten,
             nutzungsdauer, restwert, konto_nr, notizen)
        )


def get_alle_anlagen():
    with get_connection() as conn:
        return conn.execute(
            """SELECT a.anlage_id, a.bezeichnung, a.anschaffungsdatum,
                      a.anschaffungskosten, a.nutzungsdauer, a.restwert,
                      a.abschreibung_pa, a.konto_nr,
                      COALESCE(k.bezeichnung,'—') AS konto_bez, a.notizen
               FROM anlagen a
               LEFT JOIN konten k ON a.konto_nr = k.konto_nr
               ORDER BY a.anlage_id"""
        ).fetchall()


def anlage_loeschen(anlage_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM anlagen WHERE anlage_id=?", (anlage_id,))


def anlage_aktualisieren(anlage_id, bezeichnung, anschaffungsdatum,
                          anschaffungskosten, nutzungsdauer, restwert, konto_nr, notizen):
    with get_connection() as conn:
        conn.execute(
            """UPDATE anlagen SET bezeichnung=?, anschaffungsdatum=?,
               anschaffungskosten=?, nutzungsdauer=?, restwert=?,
               konto_nr=?, notizen=?
               WHERE anlage_id=?""",
            (bezeichnung, anschaffungsdatum, anschaffungskosten,
             nutzungsdauer, restwert, konto_nr, notizen, anlage_id)
        )


# ── Auswertungen ──────────────────────────────────────────────────────────────

def get_bilanz():
    with get_connection() as conn:
        aktiva = conn.execute(
            "SELECT konto_nr, bezeichnung, saldo FROM konten WHERE konto_typ='Aktiva' ORDER BY konto_nr"
        ).fetchall()
        passiva = conn.execute(
            "SELECT konto_nr, bezeichnung, saldo FROM konten WHERE konto_typ='Passiva' ORDER BY konto_nr"
        ).fetchall()
        return aktiva, passiva


def get_guv():
    with get_connection() as conn:
        aufwand = conn.execute(
            "SELECT konto_nr, bezeichnung, saldo FROM konten WHERE konto_typ='Aufwand' ORDER BY konto_nr"
        ).fetchall()
        ertrag = conn.execute(
            "SELECT konto_nr, bezeichnung, saldo FROM konten WHERE konto_typ='Ertrag' ORDER BY konto_nr"
        ).fetchall()
        return aufwand, ertrag
