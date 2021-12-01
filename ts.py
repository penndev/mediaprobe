


class PES:
    "可以对PES进行封包和拆包"
    
    START_CODE = [0x00, 0x00, 0x01]
    VIDEO = 0xe0
    AUDIO = 0xc0

    def __init__(self) -> None:
        self.hex = []
        self.tagType = False

    def setHead(self, tag, pts = False, dts = False):
        '根据参数生成 pes header 的 hex'
        self.tagType = tag
        self.pts = pts
        self.dts = dts
        # 初始化
        self.hex = self.START_CODE + [0] * 6
        self.hex[3] = getattr(self,tag)
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
        return self

    def setData(self,data):
        self.hex += data
        return self.hex

    def hexDtsPts(self, dts = False, pts = False):
        '生成pts and dts hex数据并返回'
        if dts != False:
            dpvalue = dts
            dptype = 0x11
        else:
            dpvalue = pts
            dptype = 0x31
        dphex = [0] * 5
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
        self.hex = bytearray()
        first = True
        data = pes.hex
        while len(data):
            pack = bytearray([0xff]*188)
            mixed = len(data) < 184
            pack[0:4] = self.setHead(pes.tagType,adapta=first,mixed=mixed) 
            start = 4
            if mixed : # 最后一步,优先级最高
                pack[4] = 183 - len(data)
                if pack[4] != 0:
                    pack[5] = 0
                start = pack[4] + 5
            elif first : # adapta 
                pcr = self.setAdapta(pes.dts)
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
        if tag == 'VIDEO':
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

Pes = PES()
Packet = PACKET() 

if __name__ == "__main__":
    print(PES().setHead('VIDEO',396270,381240).setData([9,9,9,9]))
