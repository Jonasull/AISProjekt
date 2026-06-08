import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
import database

if __name__ == "__main__":
    database.init_db()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
