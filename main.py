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

        self.showTop()
        self.showContent()

    def showTop(self):
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

        right = QtWidgets.QVBoxLayout()
        self.infoBrower = QtWidgets.QPlainTextEdit()
        self.infoBrower.setReadOnly(True)
        right.addWidget(self.infoBrower)

        self.hexBrower = QtWidgets.QPlainTextEdit()
        self.hexBrower.setReadOnly(True)
        right.addWidget(self.hexBrower)

        content.addLayout(right)
        content.setStretchFactor(right,4)

        self.layout.addLayout(content)


    def openFlv(self):
        pwd = QtWidgets.QFileDialog.getOpenFileName(self, "打开文件", " ",'*.flv')
        self.flvStruct = flv.newFLv(pwd[0])
        self.tree.addItems(self.flvStruct.getBody())

    def clickFlvItem(self,item):
        tag = self.flvStruct.body[item.row()]

        self.infoBrower.setPlainText("hello world")
        
        self.hexBrower.setPlainText(tag.data.hex(' '))


if __name__ == "__main__":
    app = QtWidgets.QApplication()
    app.setWindowIcon(QtGui.QIcon("flv.png"))

    widget = MainWidget()
    widget.resize(960, 800)
    widget.show()
    
    app.exec()