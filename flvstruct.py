# 官方flv标准介绍
# https://www.adobe.com/content/dam/acom/en/devnet/flv/video_file_format_spec_v10.pdf

class AVCPacket:
    Type = None
    CompositionTime = None
    Data = None
    def __init__(self, data):
        self.Type = data[0]
        self.CompositionTime = int.from_bytes(data[1:4], byteorder='big')
        if self.Type == 0:
            print("遇到了avcdecoder")
            #AVCDecoderConfigurationRecord
        elif self.Type == 1:
            n = 4
            while True:
                if n == len(data):
                    break
                naluLen = int.from_bytes(data[n:n+4], byteorder='big')
                endSize = n+4+naluLen
                nalu = data[n+4:endSize]
                n = endSize
                print(n)
        else:
            pass
        

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
        # 拆分出aac和avc数据
        if(self.tagType == 18):
            self.onMetaData() 
        elif self.tagType == 9:
            self.videoTag()
        elif self.tagType == 8:
            self.audioTag()      
        else:
            pass
    def setPreviousTagSize(self,data):
        self.tagSize = int.from_bytes(data, byteorder='big')
    def onMetaData(self):
        pass
    def audioTag(self):
        pass
    def videoTag(self):
        self.FrameType = self.data[0] >> 4
        self.CodecID = self.data[0] & 0xf
        if(self.CodecID == 7):#h264
            AVCPacket(self.data[1:])

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

Flv("test.flv")