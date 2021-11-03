from PySide6 import  QtWidgets, QtGui
import os, flv,math


NAME = "FLv-Analyze"
ICON = "icon.png"
MYAPPID = 'flv-analyze.penndev.github'

if os.name == 'nt':
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(MYAPPID)


class pMainWidget(QtWidgets.QWidget):
    'Flv-analyze 分析文件GUI控制'
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.flvStruct = None
        self.showContent()

    def showContent(self):
        '展示 flv tag 全部信息'
        # 展示当前所有Tag的列表组件
        self.pTagListTree = QtWidgets.QListWidget()
        self.pTagListTree.clicked.connect(self.pClickFlvItem)

        # 展示当前点击后的tag info内容
        self.pTagInfoText = QtWidgets.QTableWidget()
        self.pTagInfoText.setColumnCount(3)
        self.pTagInfoText.setHorizontalHeaderLabels(["Filed","Position","Info"])
        self.pTagInfoText.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # 展示原始字节流
        self.pTagInfoHex = QtWidgets.QTableWidget()
        self.pTagInfoHex.setColumnCount(16)
        self.pTagInfoHex.setHorizontalHeaderLabels(["0","1", "2", "3","4","5","6","7","8","9","a","b","c","d","e","f"])
        self.pTagInfoHex.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # 增加上下布局
        right = QtWidgets.QVBoxLayout()
        right.addWidget(self.pTagInfoText)
        right.setStretchFactor(self.pTagInfoText,2)
        right.addWidget(self.pTagInfoHex)
        right.setStretchFactor(self.pTagInfoHex,3)

        # 全局布局
        content = QtWidgets.QHBoxLayout()
        content.addWidget(self.pTagListTree)
        content.addLayout(right)
        content.setStretchFactor(self.pTagListTree,1)
        content.setStretchFactor(right,4)
        self.layout.addLayout(content)
    def pClearFlv(self):
        self.pTagListTree.clear()
    def pOpenFlv(self):
        '打开FLv文件操作。'
        pwd = QtWidgets.QFileDialog.getOpenFileName(self, "打开文件", " ",'*.flv')
        self.flvStruct = flv.newFLv(pwd[0])
        self.pTagListTree.clear()
        self.pTagListTree.addItem(self.flvStruct.header.name)
        self.pTagListTree.addItems(self.flvStruct.tagList)


    def pClickFlvItem(self,item):
        '点击某个tag list触发的事件'
        self.pTagInfoText.clearContents()
        self.pTagInfoHex.clearContents()
        # 如果是FLV header 则特殊处理
        print(item.row())
        if(item.row() == 0):
            return self.pClickFlvHeader()
        tag = self.flvStruct.body[item.row()-1]

        tagBodyEnd = 11 + tag.dataSize
        headLs = [
            ("Tag Type","HEX[0]",str(tag.tagType)),
            ("Tag Data Size","HEX[1:4]", str(tag.dataSize)),
            ("Tag TimeStamp","HEX[4:7]", str(tag.timeStamp) ),
            ("Tag TimeStamp Extended","HEX[7]",str(tag.timeStampExtended)),
            ("Tag streamID", "HEX[8:11]", str(tag.streamID)),
            ("Tag Body","HEX[11:"+ str(tagBodyEnd) +"]","ShowMore"),
            ("PreviousTagSize","HEX["+str(tagBodyEnd)+":"+str(tagBodyEnd+4)+"]",str(tag.previousTagSize))
        ]
        self.pTagInfoText.setRowCount(len(headLs))
        for i, (filed, position,info) in enumerate(headLs):
            c = 0
            self.pTagInfoText.setItem(i, c,QtWidgets.QTableWidgetItem(filed))
            c+=1
            self.pTagInfoText.setItem(i, c,QtWidgets.QTableWidgetItem(position))
            c+=1
            self.pTagInfoText.setItem(i, c,QtWidgets.QTableWidgetItem(info))
        # 填充hex当前tag的所有数据。
        self.pTagInfoHex.setRowCount(math.ceil(len(tag.data)/16))
        n = 0
        for i in tag.data:
            item = QtWidgets.QTableWidgetItem(hex(i))
            self.pTagInfoHex.setItem(math.ceil((n)//16),n%16,item)
            n += 1

    def pClickFlvHeader(self):
        headLs = [
            ("FLV Sign","HEX[0:4]",self.flvStruct.header.data[0:3].hex(" ")),
            ("Version","HEX[4]", hex(self.flvStruct.header.data[3])),
            ("Type Flags","HEX[5]", hex(self.flvStruct.header.data[4]) + " |video(byte&1)|audio(byte&4)|" ),
            ("Data offset","HEX[6:9]",self.flvStruct.header.data[5:9].hex(" ")),
            ("PreviousTagSize","HEX[9:12]",self.flvStruct.header.data[9:13].hex(" "))
        ]
        self.pTagInfoText.setRowCount(len(headLs))
        for i, (filed, position,info) in enumerate(headLs):
            c = 0
            self.pTagInfoText.setItem(i, c,QtWidgets.QTableWidgetItem(filed))
            c+=1
            self.pTagInfoText.setItem(i, c,QtWidgets.QTableWidgetItem(position))
            c+=1
            self.pTagInfoText.setItem(i, c,QtWidgets.QTableWidgetItem(info))
        self.pTagInfoHex.setRowCount(math.ceil(len(self.flvStruct.header.data)/16))
        n = 0
        for i in self.flvStruct.header.data:
            item = QtWidgets.QTableWidgetItem(hex(i))
            self.pTagInfoHex.setItem(math.ceil((n)//16),n%16,item)
            n += 1

class pMainWindow(QtWidgets.QMainWindow):
    'Flv-analyze 分析文件GUI控制'
    def __init__(self):
        super().__init__()
        self.pCentent = pMainWidget()
        self.pSetMenuBar()
        self.setCentralWidget(self.pCentent)
        self.resize(960, 800)
        self.setWindowTitle(NAME)
        self.show()

    def pSetMenuBar(self):
        '设置菜单栏'
        actionOpen = QtGui.QAction("&打开文件", self)
        actionOpen.triggered.connect(self.pCentent.pOpenFlv)

        actionClear = QtGui.QAction("&清理", self)
        actionClear.triggered.connect(self.pCentent.pClearFlv)

        actionHelp = QtGui.QAction("&关于", self)
        actionHelp.triggered.connect(self.pOpenLink)

        menuFlv = self.menuBar().addMenu("&文件")
        menuFlv.addAction(actionOpen)
        menuFlv.addAction(actionClear)
        menuHelp = self.menuBar().addMenu("&帮助")
        menuHelp.addAction(actionHelp)

    def pOpenLink(self):
        QtGui.QDesktopServices.openUrl("https://github.com/penndev/flv-analyze")



if __name__ == "__main__":
    app = QtWidgets.QApplication()

    window = pMainWindow()

    app.exec()
