import sys

from PySide6 import QtWidgets

from gui.main_widjet import MyWidget


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.show()

    sys.exit(app.exec())