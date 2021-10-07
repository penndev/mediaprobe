# 官方flv标准介绍
# https://www.adobe.com/content/dam/acom/en/devnet/flv/video_file_format_spec_v10.pdf



class AVCPacket:
    def __init__(self, data):
        self.Type = 2
        self.CompositionTime = 0
        self.Data = []

        self.Type = data[0]
        self.CompositionTime = int.from_bytes(data[1:4], byteorder='big')
        if self.Type == 0:
            self.Data = data[4:]
            #AVCDecoderConfigurationRecord
        elif self.Type == 1:
            start = 4
            while True:
                if start >= len(data[4:]):
                    break
                naluLen = int.from_bytes(data[start:start+4], byteorder='big')
                start += 4
                end = start + naluLen
                nalu = data[start:end]
                start += naluLen
                self.Data.append(nalu)
        else:
            pass

class AACPacket:
    def __init__(self, data):
        self.Type = data[0]
        if self.Type == 0:
            self.Data = data[1:]
        elif self.Type == 1:
            # add adts header
            self.Data = data[1:]

class FlvHeader:
    data = None
    tagSize = None
    def setHeaderData(self,data):
        self.data = data
    def setPreviousTagSize(self,data):
        self.tagSize = int.from_bytes(data, byteorder='big')

class FlvTag:
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
        self.SoundFormat = self.data[0] >> 4
        if(self.SoundFormat == 10):
            self.tag = AACPacket(self.data[1:])
        else:
            print("暂未支持的音频封装" + self.SoundFormat)
            exit()
    def videoTag(self):
        self.FrameType = self.data[0] >> 4
        self.CodecID = self.data[0] & 0xf
        if(self.CodecID == 7):#h264
            self.tag = AVCPacket(self.data[1:])
        else:
            print("暂未支持的视频容器封装" + self.CodecID)
            exit()

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

flvAnalyze = Flv("test.flv")

# with open("test.h264",'wb') as h:
#     for tag in flvAnalyze.body:
#         if tag.tagType == 9:
#             if tag.tag.Type == 1:
#                 for nalu in tag.tag.Data:
#                     h.write(bytes([0,0,0,1]))
#                     h.write(bytes(nalu))

# with open("test.aac",'wb') as h:
#     for tag in flvAnalyze.body:
#         if tag.tagType == 8:
#             if tag.tag.Type == 1:
#                 adtsHeader = [0xff, 0xf1, 0x4c, 0x80,0x00,0x00,0xfc]
#                 adtsLen = len(tag.tag.Data)+7
#                 adtsLen = adtsLen << 5
#                 adtsLen = adtsLen | 0x1f
#                 adtsHeader[4:6] = adtsLen.to_bytes(2,'big')
#                 h.write(bytes(adtsHeader))
#                 h.write(bytes(tag.tag.Data))
