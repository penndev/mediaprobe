import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui

class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.button = QtWidgets.QPushButton("Select File")

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.button)
        self.button.clicked.connect(self.openFile)

    @QtCore.Slot()
    def openFile(self):
        directory = QtWidgets.QFileDialog.getOpenFileName(self, "Find Files",
                QtCore.QDir.currentPath(),'*.flv')
        print(directory)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MainWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())