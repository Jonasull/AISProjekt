STYLESHEET = """
QMainWindow, QDialog {
    background-color: #f0f2f5;
}

QTabWidget::pane {
    border: 1px solid #c0c4cc;
    background: #ffffff;
    border-radius: 4px;
}

QTabBar::tab {
    background: #e4e7ed;
    color: #303133;
    padding: 8px 18px;
    border: 1px solid #c0c4cc;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    font-weight: bold;
    min-width: 100px;
}

QTabBar::tab:selected {
    background: #409eff;
    color: #ffffff;
}

QTabBar::tab:hover:!selected {
    background: #b3d8ff;
}

QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #f5f7fa;
    gridline-color: #ebeef5;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    font-size: 13px;
}

QTableWidget::item:selected {
    background-color: #ecf5ff;
    color: #303133;
}

QHeaderView::section {
    background-color: #409eff;
    color: #ffffff;
    padding: 6px 10px;
    border: none;
    font-weight: bold;
    font-size: 13px;
}

QPushButton {
    background-color: #409eff;
    color: white;
    border: none;
    padding: 7px 18px;
    border-radius: 4px;
    font-size: 13px;
    font-weight: bold;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #66b1ff;
}

QPushButton:pressed {
    background-color: #3a8ee6;
}

QPushButton#btn_danger {
    background-color: #f56c6c;
}

QPushButton#btn_danger:hover {
    background-color: #f78989;
}

QPushButton#btn_success {
    background-color: #67c23a;
}

QPushButton#btn_success:hover {
    background-color: #85ce61;
}

QPushButton#btn_warning {
    background-color: #e6a23c;
}

QPushButton#btn_warning:hover {
    background-color: #ebb563;
}

QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QDateEdit, QTextEdit {
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    padding: 5px 8px;
    background: #ffffff;
    font-size: 13px;
    min-height: 28px;
}

QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus,
QSpinBox:focus, QDateEdit:focus, QTextEdit:focus {
    border-color: #409eff;
}

QGroupBox {
    font-weight: bold;
    font-size: 13px;
    border: 1px solid #dcdfe6;
    border-radius: 6px;
    margin-top: 12px;
    padding: 10px;
    background: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #409eff;
}

QLabel {
    font-size: 13px;
    color: #303133;
}

QStatusBar {
    background: #409eff;
    color: white;
    font-size: 12px;
}

QScrollBar:vertical {
    border: none;
    background: #f0f2f5;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background: #c0c4cc;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
