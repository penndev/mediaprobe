'''
官方flv标准介绍  https://www.adobe.com/content/dam/acom/en/devnet/flv/video_file_format_spec_v10.pdf

提取adts
adtsHeader = [0xff, 0xf1, 0x4c, 0x80,0x00,0x00,0xfc]
adtsLen = len(tag.tag.Data)+7
adtsLen = adtsLen << 5
adtsLen = adtsLen | 0x1f
adtsHeader[4:6] = adtsLen.to_bytes(2,'big')
h.write(bytes(adtsHeader))
h.write(bytes(tag.tag.Data))

提取nalu
0,0,0,1 + nalu.data

'''

from os import close


class TAG:
    
    NALU_HEAD = bytearray([0,0,0,1])

    def getHead(self,data):
        self.tagType = data[0]
        self.dataSize = int.from_bytes(data[1:4], byteorder='big')
        self.timeStamp = int.from_bytes(data[4:7], byteorder='big')
        self.timeStampExtended = data[7]
        self.streamID = int.from_bytes(data[8:11], byteorder='big')
    
    def setData(self,data):
        if(self.tagType == 9): # flv video tag data
            self.frameType = data[0] >> 4
            self.codecID = data[0] & 0x0f
            if(self.codecID == 7): # video type avc
                self.nalu = bytearray()
                self.avcPacketType = data[1]
                self.compositionTime = int.from_bytes(data[2:5], byteorder='big')
                readed = 5
                if self.avcPacketType == 1: # [len + nalu,len + nalu]
                    while (len(data)-5) > readed :
                        naluLen = int.from_bytes(data[readed:readed+4], byteorder='big')
                        readed += 4
                        self.nalu += self.NALU_HEAD + data[readed:readed+naluLen]
                        readed += naluLen
                elif self.avcPacketType == 0: # sps pps
                    spsLen = (data[readed+6] << 8) + data[readed + 7]
                    readed += 8
                    sps = data[readed:readed+spsLen]
                    readed += spsLen
                    ppsLen = (data[readed+1] << 8) + data[readed+2]
                    readed += 3
                    pps = data[readed:readed+ppsLen]
                    # naluSeq = naluHead + sps + naluHead + pps
            else:
                raise NameError("不支持的视频封装格式")
        elif self.tagType == 8:
            self.SoundFormat = (data[0] & 0xf0) >> 4
            if self.SoundFormat == 10: # AAC type
                self.aacPacketType = data[1]
                self.adts = bytearray()
                if self.aacPacketType == 1: # adts data
                    data = data[2:self.dataSize]
                    adtsHeader = [0xff, 0xf1, 0x4c, 0x80,0x00,0x00,0xfc]
                    adtsLen = len(data)+7
                    adtsLen = adtsLen << 5
                    adtsLen = adtsLen | 0x1f
                    adtsHeader[4:6] =  adtsLen.to_bytes(2,'big')
                    self.adts = bytearray(adtsHeader) + data
                elif self.aacPacketType == 0:
                    pass
            elif self.SoundFormat == 2: # MP3 type
                self.audio = data[1:]
            else:
                raise NameError("未知的视频类型")
        elif self.tagType == 18:
            pass
        else:
            raise NameError("未知的tag type:" + str(self.tagType))

class FLV:

    TAG_HEAD_LEN = 11

    def setFile(self,filename):
        self.tags = []
        with open(filename, 'rb') as f:
            self.hex = bytearray(f.read())
        hexCount = len(self.hex)
        readCount = 13

        while hexCount > readCount:
            tag = TAG()
            tag.getHead(self.hex[readCount:readCount+self.TAG_HEAD_LEN])
            # print("debug",tag.tagType,self.hex[readCount:readCount+self.TAG_HEAD_LEN])
            readCount += self.TAG_HEAD_LEN
            tag.setData(self.hex[readCount:readCount+tag.dataSize])
            readCount += tag.dataSize + 4
            self.tags.append(tag)

H264DefaultHZ = 90

if __name__ == "__main__":
    import ts
    flv = FLV()
    flv.setFile("testcopy.flv")
    
    tsFile = open("peng1.ts",'wb')
    tsFile.write(ts.SDT())
    tsFile.write(ts.PAT())
    tsFile.write(ts.PMT())

    mp3File = open("peng.mp3",'wb')

    count = 0
    for tag in flv.tags:
        if tag.tagType == 9:
            count += 1
            if tag.nalu == b'':
                continue
            dts = tag.timeStamp * H264DefaultHZ
            pts = dts + (tag.compositionTime * H264DefaultHZ)
            pes = ts.Pes.setES("Video",tag.nalu,pts,dts)
            tsFile.write(ts.Packet.setPes(pes))
        elif tag.tagType == 8:
            dts = tag.timeStamp * H264DefaultHZ
            if tag.SoundFormat == 2:
                if tag.audio == b'':
                    continue
                mp3File.write(tag.audio)
                pes = ts.Pes.setES("Audio",tag.audio,dts,dts)
                tsFile.write(ts.Packet.setPes(pes))
            elif tag.SoundFormat == 10:
                if tag.adts == b'':
                    continue
                pes = ts.Pes.setES("Audio",tag.adts,dts,dts)
                tsFile.write(ts.Packet.setPes(pes))

    mp3File.close()
    tsFile.close()
