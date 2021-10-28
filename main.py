from PySide6 import QtCore, QtWidgets, QtGui
import ctypes,os,flv

if os.name == 'nt':
    myappid = 'flv-analyze.github.pennilessfor@gmail' 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class MainWidget(QtWidgets.QWidget):
    'Flv-analyze 分析文件GUI控制'

    def __init__(self):
        super().__init__()
        # 应用程序主面板布局
        self.layout = QtWidgets.QVBoxLayout(self)

        self.pBtnSize = QtCore.QSize(80,40)            # 默认按钮组大小配置
        self.pOpenFlvBtn = QtWidgets.QPushButton("打开文件")  # 打开文件默认按钮
        self.pTagListTree = QtWidgets.QListWidget()    # 展示当前所有Tag的列表组件
        self.pTagInfoText = QtWidgets.QTextEdit()      # 展示当前点击后的tag info内容
        self.pTagInfoHex  = QtWidgets.QPlainTextEdit() # 展示原始字节流

        # 与FLV文件交互IO
        self.flvStruct = None 

        self.showTop()
        self.showContent()

    def showTop(self):
        '顶部按钮组'
        self.pOpenFlvBtn.clicked.connect(self.pOpenFlv)
        self.pOpenFlvBtn.setStyleSheet("background-color: #FFF;border:none")
        self.pOpenFlvBtn.setFixedSize(self.pBtnSize)
        self.layout.addWidget(self.pOpenFlvBtn)

    def showContent(self):
        '展示 flv tag 全部信息'
        # 设置组件的默认展示属性。
        self.pTagListTree.clicked.connect(self.pClickFlvItem)
        self.pTagInfoText.setReadOnly(True)
        self.pTagInfoHex.setReadOnly(True)
        # 增加上下布局
        right = QtWidgets.QVBoxLayout()
        right.addWidget(self.pTagInfoText)
        right.setStretchFactor(self.pTagInfoText,3)
        right.addWidget(self.pTagInfoHex)
        right.setStretchFactor(self.pTagInfoHex,2)
        # 左右布局
        content = QtWidgets.QHBoxLayout()
        content.addWidget(self.pTagListTree)
        content.addLayout(right)
        content.setStretchFactor(self.pTagListTree,1)
        content.setStretchFactor(right,4)
        # 增加布局
        self.layout.addLayout(content)


    def pOpenFlv(self):
        '打开FLv文件操作。'
        pwd = QtWidgets.QFileDialog.getOpenFileName(self, "打开文件", " ",'*.flv')
        self.flvStruct = flv.newFLv(pwd[0])

        self.pTagListTree.addItem(self.flvStruct.header.name)
        self.pTagListTree.addItems(self.flvStruct.tagList)

    def pClickFlvItem(self,item):
        '点击某个tag list触发的事件'

        # 如果是FLV header 则特殊处理
        if(item.row() == 0):
            self.pTagInfoHex.setPlainText(self.flvStruct.header.data.hex(' '))
            return



        tag = self.flvStruct.body[item.row()-1]
        # 填充解析后的详情
        self.pTagInfoText.setText("Tag Type: " + str(tag.tagType))
        self.pTagInfoText.append("Tag Data Size: " + str(tag.dataSize))
        self.pTagInfoText.append("Tag TimeStamp: " + str(tag.timeStamp))
        self.pTagInfoText.append("Tag TimeStamp Extended: " + str(tag.timeStampExtended))
        self.pTagInfoText.append("Tag streamID: " + str(tag.streamID))
        self.pTagInfoText.append("PreviousTagSize: " + str(tag.previousTagSize))
        
        # 填充hex当前tag的所有数据。
        self.pTagInfoHex.setPlainText(tag.data.hex(' '))


if __name__ == "__main__":
    app = QtWidgets.QApplication()
    app.setWindowIcon(QtGui.QIcon("icon.png"))
    app.setApplicationName("FLv-Analyze")


    widget = MainWidget()
    widget.setWindowTitle("FLv-Analyze")
    widget.resize(960, 800)
    widget.show()


    app.exec()




