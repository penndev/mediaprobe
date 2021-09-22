from os import read
from PySide6 import QtCore, QtWidgets, QtGui

class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout(self)

        # 打开文件按钮
        self.button = QtWidgets.QPushButton("Select File")
        self.button.clicked.connect(self.openFile)
        self.layout.addWidget(self.button)

        # 展示flv文件详情的面板
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["flv Tag", "File Body"])
        self.layout.addWidget(self.tree)


    @QtCore.Slot()
    def openFile(self):
        directory = QtWidgets.QFileDialog.getOpenFileName(self, "Find Files", " ",'*.flv')
        if directory:
            self.tree.insertTopLevelItems(0, self.getFileItem(directory))
    
    @QtCore.Slot()
    def getFileItem(self,flvFilePath):
        items = []
        with open(flvFilePath[0], 'rb') as f:
            data = f.read(9)
            data = data.hex(" ")
            item = QtWidgets.QTreeWidgetItem(["Flv Header",data])
            item.addChild(QtWidgets.QTreeWidgetItem(["PreviousTagSize", f.read(4).hex(" ") ]))
            items.append(item)
            while(True):
                data = f.read(11)
                if(data == b''):
                    break
                if(data[0] == 18):
                    tagName = "Script Tag"
                elif(data[0] == 9):
                    tagName = "Video Tag"
                elif(data[0] == 8):
                    tagName = "Audit Tag"
                else:
                    break
                item = QtWidgets.QTreeWidgetItem([tagName, data.hex(" ") ])
                len = int.from_bytes(data[1:4], byteorder='big')
                item.addChild(QtWidgets.QTreeWidgetItem(["body",f.read(len).hex(" ")]))
                item.addChild(QtWidgets.QTreeWidgetItem(["PreviousTagSize", f.read(4).hex(" ") ]))
                items.append(item)
        return items


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MainWidget()
    widget.resize(800, 600)
    widget.show()

    app.exec()