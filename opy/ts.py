'''  
处理ts封包器  
文档
https://web.archive.org/web/20190217042838/

ISO/IEC 13818-4: "Information Technology - Generic coding of moving pictures and associated audio information:
Compliance".

ETSI TS 101 211: "Digital Video Broadcasting (DVB); Guidelines on implementation and usage of Service
Information (SI)".

ETSI TS 101 154: " Digital Video Broadcasting (DVB); Specification for the use of Video and Audio Coding in
Broadcasting Applications based on the MPEG-2 Transport Stream".

'''


class PES:
    "可以对PES进行封包和拆包"
    
    START_CODE = [0x00, 0x00, 0x01]
    TAG = {
        "Video" : 0xe0,
        "Audio" : 0xc0
    }

    def setES(self, tag, es = bytearray(), pts = False, dts = False):
        '根据参数生成 pes header 的 hex'
        self.tag = tag
        self.pts = pts
        self.dts = dts
        # 初始化
        self.hex = bytearray( self.START_CODE + [self.TAG[tag]] + [0] * 5 )
        # if taglen != False:
        #     self.hex[4:6] = [PesLen >> 8,PesLen & 0xff]
        # pes-info信息
        self.hex[6] = 0x80 
        # 设置pts | dts
        if pts != False:
            if dts != False:
                self.hex[7] = 0xc0 # 默认存在dts和pts
                self.hex[8] = 0x0a # len
                self.hexDtsPts(pts=pts) 
                self.hexDtsPts(dts=dts)
            else:
                self.hex[7] = 0x80 # 默认存在dts和pts
                self.hex[8] = 0x05 # len
                self.hexDtsPts(pts=pts)
        else:
            raise NameError('可以不存在dts，但是必须存在pts.')
        self.hex += es
        return self

    def hexDtsPts(self, dts = False, pts = False):
        '生成pts and dts hex数据并返回'
        if dts != False:
            dpvalue = dts
            dptype = 0x11
        else:
            dpvalue = pts
            dptype = 0x31
        dphex = bytearray([0] * 5)
        dphex[0] = dptype | (dpvalue >> 29)
        hp = ((dpvalue >> 15) & 0x7fff) * 2 + 1 
        dphex[1] = hp >> 8
        dphex[2] = hp & 0xff
        he = (dpvalue & 0x7fff) * 2 + 1 
        dphex[3] = he >> 8
        dphex[4] = he & 0xff
        # return dphex
        self.hex += dphex

class PACKET:
    VIDEO_COUNT=0
    AUDIO_COUNT=0

    VIDEO_PID = 0x100
    AUDIO_PID = 0x101

    def setPes(self,pes):
        'pes [class PES]'
        tagType = pes.tag
        data = pes.hex
        dts = pes.dts

        self.hex = bytearray()
        first = True
        while len(data):
            pack = bytearray([0xff]*188)
            mixed = len(data) < 184
            pack[0:4] = self.setHead(tagType,adapta=first,mixed=mixed) 
            start = 4
            if mixed : # 最后一步,优先级最高
                pack[4] = 183 - len(data)
                if pack[4] != 0:
                    pack[5] = 0
                start = pack[4] + 5
            elif first : # adapta 
                pcr = self.setAdapta(dts)
                pack[4] = len(pcr)
                start = 5 + pack[4]
                pack[5:start] = pcr
            end = 188 - start
            pack[start:] = data[:end]
            if len(pack) != 188:
                raise NameError("ts packet len error")
            # 无关写入数据操作。
            data = data[end:]
            self.hex += pack
            if first:
                first = False
        return self.hex

    def setAdapta(self,dts):
        adapt = bytearray([0]*7)
        adapt[0] =  0x50
        adapt[1] = dts >> 25
        adapt[2] = (dts >> 17) & 0xff
        adapt[3] = (dts >> 9) & 0xff
        adapt[4] = (dts >> 1) & 0xff
        adapt[5] = ((dts & 0x1) << 7) | 0x7e
        return adapt

    def setHead(self,tag,adapta=False,mixed=False):
        'tag [AUDIO:VIDEO] 类型 adapta 是否有拓展字段,mixed是否有混肴字段'
        tsHead = bytearray([0]*4)
        tsHead[0] = 0x47
        if adapta:
            tsHead[1] |= 0x40
        # 写入PID
        if tag == 'Video':
            tsHead[1] |= self.VIDEO_PID >> 8
            tsHead[2] |= self.VIDEO_PID & 0xff
            tsHead[3] |= self.VIDEO_COUNT
            self.VIDEO_COUNT = (self.VIDEO_COUNT + 1 ) % 16
        else:
            tsHead[1] |= self.AUDIO_PID >> 8
            tsHead[2] |= self.AUDIO_PID & 0xff
            tsHead[3] |= self.AUDIO_COUNT
            self.AUDIO_COUNT = (self.AUDIO_COUNT + 1 ) % 16
        # 写入是否存在拓展字段
        if adapta or mixed:
            tsHead[3] |= 0x30
        else:
            tsHead[3] |= 0x10
        return tsHead

def SDT():
    bt = bytearray([0xff]*188)
    hex = [
        0x47, 0x40, 0x11, 0x10, 
        0x00, 0x42, 0xF0, 0x25, 0x00, 0x01, 0xC1, 0x00, 0x00, 0xFF, 
        0x01, 0xFF, 0x00, 0x01, 0xFC, 0x80, 0x14, 0x48, 0x12, 0x01, 
        0x06, 0x46, 0x46, 0x6D, 0x70, 0x65, 0x67, 0x09, 0x53, 0x65, 
        0x72, 0x76, 0x69, 0x63, 0x65, 0x30, 0x31, 0x77, 0x7C, 0x43, 
        0xCA
    ]
    bt[0:45] = hex
    return bt

def PAT():
    bt = bytearray([0xff]*188)
    hex = [
        0x47, 0x40, 0x00, 0x10, #ts packet hd
        0x00, #adaption
        0x00, 0xB0, 0x0D, 0x00, 0x01, 0xC1, 0x00, 0x00, 0x00, 0x01, 
        0xF0, 0x00, 0x2A, 0xB1, 0x04, 0xB2
    ]
    bt[0:21] = hex
    return bt

def PMT():
    bt = bytearray([0xff]*188)
    hex = [
        0x47, 0x50, 0x00, 0x10,
        0x00,
        0x02, 0xB0, 0x17, 0x00, 0x01, 0xC1, 0x00, 0x00, 0xE1, 0x00,
        0xF0, 0x00, 0x1B, 0xE1, 0x00, 0xF0, 0x00, 0x0F, 0xE1, 0x01,
        0xF0, 0x00, 0x2F, 0x44, 0xB9, 0x9B
    ]
    bt[0:31] = hex
    return bt

Pes = PES()
Packet = PACKET() 

if __name__ == "__main__":
    Pes.setHead('Video',396270,381240)
    Pes.setData([0,1,2,3,4,5])
    print(Pes.hex)
    # -.-