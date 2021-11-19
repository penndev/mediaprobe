'官方flv标准介绍  https://www.adobe.com/content/dam/acom/en/devnet/flv/video_file_format_spec_v10.pdf'

'''
提取adts
adtsHeader = [0xff, 0xf1, 0x4c, 0x80,0x00,0x00,0xfc]
adtsLen = len(tag.tag.Data)+7
adtsLen = adtsLen << 5
adtsLen = adtsLen | 0x1f
adtsHeader[4:6] = adtsLen.to_bytes(2,'big')
h.write(bytes(adtsHeader))
h.write(bytes(tag.tag.Data))
'''

'''
提取nalu
0,0,0,1 + nalu.data
'''


class FlvTag:
    tagTypeItem = {8:"Audit Tag",9:"Video Tag",18:"Script Tag"}
    def __init__(self,data) -> None:
        '分析flv tag header 内容获取datasize'
        self.data = data
        self.tagType = data[0]
        self.dataSize = int.from_bytes(data[1:4], byteorder='big')
        self.timeStamp = int.from_bytes(data[4:7], byteorder='big')
        self.timeStampExtended = data[7]
        self.streamID = int.from_bytes(data[8:11], byteorder='big')
        self.frameType = None
        self.codecID = None
        self.avcPacketType = None
        self.nalu = []

    def setData(self,data):
        '解码媒体源数据'
        self.data += data
        if(self.tagType == 9):
            self.frameType = data[0] >> 4
            self.codecID = data[0] & 0x0f
            if(self.codecID == 7):
                self.avcPacketType = data[1]
                self.compositionTime = int.from_bytes(data[2:5], byteorder='big')
                i = 5
                if (self.avcPacketType == 1):
                    while(True):
                        naluLen = int.from_bytes(data[i:i+4], byteorder='big')
                        if(i == 5):
                            self.nalu = self.nalu + [0,0,0,1]
                        else:
                            self.nalu = self.nalu + [0,0,1]
                        i = i + 4
                        self.nalu = self.nalu + list(data[i:i+naluLen])
                        i = i + naluLen
                        if(len(data) <= i):
                            break

        self.previousTagSize = int.from_bytes(data[self.dataSize:], byteorder='big')

    def getTagType(self):
        '输出TagType名称'
        return self.tagTypeItem[self.tagType]
    

class FlvHeader:
    name = "Flv Header"
    def __init__(self,data) -> None:
        self.data = data
        self.previousTagSize = int.from_bytes(self.data[9:14], byteorder='big')

class Flv:
    def __init__(self,flv) -> None:
        self.header = FlvHeader(flv.read(13))
        self.body = []
        self.tagList = [] # del
        while(True):
            header = flv.read(11)
            if(header == b''):
                break
            tag = FlvTag(header)
            tag.setData(flv.read(tag.dataSize + 4))
            self.body.append(tag)
            # 展示标签列表
            self.tagList.append(tag.getTagType()) # del

def newFLv(pwd):
    with open(pwd, 'rb') as flv:
        return Flv(flv)


ts = newFLv("./test.flv")


h264DefaultHZ = 90

import mpegts

with open("testgen.ts",'wb') as h:
    h.write(mpegts.PAT())
    h.write(mpegts.PMT())
    for tag in ts.body:
        if tag.tagType == 9:
            if tag.nalu == []:
                continue
            dts = tag.timeStamp * h264DefaultHZ
            pts = dts + (tag.compositionTime * h264DefaultHZ)
            peshead = mpegts.PES(pts,dts)
            pes = peshead.data + bytes(tag.nalu)
            h.write(mpegts.PACKET(pes,dts))
            exit()
