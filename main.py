import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui

class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout(self)

        # 打开文件按钮
        self.button = QtWidgets.QPushButton("Select File")
        self.button.clicked.connect(self.openFile)
        self.layout.addWidget(self.button)

        # 展示flv文件详情
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["flv Tag", "File Body"])
        # self.tree.insertTopLevelItems(0, self.getFileItem())
        self.layout.addWidget(self.tree)


    @QtCore.Slot()
    def openFile(self):
        directory = QtWidgets.QFileDialog.getOpenFileName(self, "Find Files",
                QtCore.QDir.currentPath(),'*.flv')
        if directory:
            self.tree.insertTopLevelItems(0, self.getFileItem(directory))
    
    @QtCore.Slot()
    def getFileItem(self,flvFilePath):
        # print(flvFilePath)
        items = []
        with open(flvFilePath[0], 'rt') as f:
            data = f.read(1).hex()
            
            print(data)
            item = QtWidgets.QTreeWidgetItem(["Flv Header"])
            item.addChild(QtWidgets.QTreeWidgetItem(["hex", data]))
            items.append(item)
        return items

        # data = {"Project A": ["file_a.py", "file_a.txt", "something.xls"],
        #         "Project B": ["file_b.csv", "photo.jpg"],
        #         "Project C": []}
        
        # for key, values in data.items():
        #     item = QtWidgets.QTreeWidgetItem([key])
        #     for value in values:
        #         ext = value.split(".")[-1].upper()
        #         child = QtWidgets.QTreeWidgetItem([value, ext])
        #         item.addChild(child)
        #     items.append(item)
        # return items

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MainWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())