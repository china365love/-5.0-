from PyQt5 import QtWidgets, QtGui


def apply_pink_theme(app: QtWidgets.QApplication):
    app.setStyle('Fusion')
    palette = QtGui.QPalette()
    base = QtGui.QColor(255, 240, 245)  # #fff0f5
    highlight = QtGui.QColor(255, 105, 180)  # #ff69b4
    text = QtGui.QColor(60, 60, 60)
    palette.setColor(QtGui.QPalette.Window, base)
    palette.setColor(QtGui.QPalette.WindowText, text)
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(255, 228, 237))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.ToolTipText, text)
    palette.setColor(QtGui.QPalette.Text, text)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(255, 224, 230))
    palette.setColor(QtGui.QPalette.ButtonText, text)
    palette.setColor(QtGui.QPalette.Highlight, highlight)
    palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255))
    app.setPalette(palette)

    app.setStyleSheet(
        """
        QMainWindow, QWidget { background-color: #fff0f5; }
        QGroupBox {
            font-weight: bold;
            border: 1px solid #ffc0cb;
            border-radius: 6px;
            margin-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 6px;
            color: #c2185b;
        }
        QPushButton {
            background-color: #ff69b4;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 6px 12px;
        }
        QPushButton:hover { background-color: #ff85c1; }
        QPushButton:pressed { background-color: #f06292; }
        QLineEdit, QSpinBox {
            border: 1px solid #ffc0cb;
            border-radius: 4px;
            padding: 4px 6px;
            background: #ffffff;
        }
        QHeaderView::section {
            background-color: #ffd1dc;
            padding: 6px;
            border: none;
        }
        QTableWidget {
            gridline-color: #ffd1dc;
            alternate-background-color: #fff5f8;
        }
        QToolTip {
            background-color: #ffe4ec;
            color: #333;
            border: 1px solid #ffb6c1;
        }
        """
    )