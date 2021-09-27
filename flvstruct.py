# 官方flv标准介绍
# https://www.adobe.com/content/dam/acom/en/devnet/flv/video_file_format_spec_v10.pdf

class FlvHeader:
    data = None
    tagSize = None
    def setHeaderData(self,data):
        self.data = data
    def setPreviousTagSize(self,data):
        self.tagSize = int.from_bytes(data, byteorder='big')

class FlvTag:
    tagType = None
    dataSize = None
    timeStamp = None
    timeStampExtended = None
    streamID = None
    data = None
    tagSize = None
    def setHeaderData(self,data):
        self.tagType = data[0]
        self.dataSize = int.from_bytes(data[1:4], byteorder='big')
        self.timeStamp = int.from_bytes(data[4:7], byteorder='big')
        self.timeStampExtended = data[7]
        self.streamID = data[8:11]
    def setData(self,data):
        self.data = data
    def setPreviousTagSize(self,data):
        self.tagSize = int.from_bytes(data, byteorder='big')

class Flv:
    header = None
    body = []
    def __init__(self,fileDir) -> None:
        self.header = FlvHeader()
        with open(fileDir, 'rb') as f:
            self.header.setHeaderData(f.read(9))
            self.header.setPreviousTagSize(f.read(4))
            while(True):
                header = f.read(11)
                if(header == b''):
                    break
                tag = FlvTag()
                tag.setHeaderData(header)
                tag.setData(f.read(tag.dataSize))
                tag.setPreviousTagSize(f.read(4))
                self.body.append(tag)

flv = Flv("test.flv")
print(flv.header.data)
print(flv.body[0].tagType)
print(flv.body[1].tagType)
print(flv.body[2].tagType)