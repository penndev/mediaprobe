from PySide6 import QtCore, QtWidgets, QtGui
import ctypes,os,flv

if os.name == 'nt':
    myappid = 'flv-analyze.github.pennilessfor@gmail' 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FLv-Analyze")

        self.layout = QtWidgets.QVBoxLayout(self)
        # 本次打开的flv struct
        self.flvStruct = None 
        # 顶部按钮组
        self.btnSize = QtCore.QSize(80,40)

        self.showFlvFile()
        self.showContent()

    def showFlvFile(self):
        '打开flv文件按钮'
        self.buttonFlv = QtWidgets.QPushButton("打开文件")
        self.buttonFlv.clicked.connect(self.openFlv)
        self.buttonFlv.setStyleSheet("background-color: #FFF;border:none")
        self.buttonFlv.setFixedSize(self.btnSize)
        self.layout.addWidget(self.buttonFlv)

    def showContent(self):
        '展示flv文件详情的面板'
        content = QtWidgets.QHBoxLayout()
        self.tree = QtWidgets.QListWidget()
        self.tree.clicked.connect(self.clickFlvItem)
        content.addWidget(self.tree)
        content.setStretchFactor(self.tree,1)

        self.hexBrower = QtWidgets.QPlainTextEdit()
        self.hexBrower.setReadOnly(True)
        content.addWidget(self.hexBrower)
        content.setStretchFactor(self.hexBrower,3)

        self.layout.addLayout(content)

    def openFlv(self):
        pwd = QtWidgets.QFileDialog.getOpenFileName(self, "打开文件", " ",'*.flv')
        self.flvStruct = flv.newFLv(pwd[0])
        self.tree.addItems(self.flvStruct.getBody())

    def clickFlvItem(self,item):
        index = item.row()
        data = self.flvStruct.body[index].data
        self.hexBrower.setPlainText(data.hex(' '))

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MainWidget()
    widget.resize(960, 800)

    widget.show()
    app.setWindowIcon(QtGui.QIcon("main.png"))
    app.exec()