
class TsPacketHeader:
    def __init__(self,data) -> None:
        self.sync = data[0]
        self.error = data[1] >> 7  #是否报错
        self.payloadStart = data[1] >> 6 & 1 
        self.priority = data[1] >> 5 & 1 #优先级
        data[1] &= 0x1f
        self.pid = int.from_bytes(data[1:3],"big")
        self.scrambling = data[3] >> 6 #传输加扰。
        self.adaption = data[3] >> 4 & 3
        self.continuity = data[3] & 0x0f

class TsPacket:
    def __init__(self,data) -> None:
        'adaption 01{1}仅含有效负载，10{2}仅含调整字段，11{3}含有调整字段和有效负载。为00解码器不进行处理'
        self.header = TsPacket(data[0:4])
        self.body = []
        if self.header.adaption >= 2:#存在调整字段
            self.adaptLen = data[4]
            self.adapt = data[5:5+self.adaptLen]
            if self.header.adaption == 3:#同时存在es
                self.body = data[5+self.adaptLen:]
            else:
                self.body = []
        elif self.header.adaptLen == 1:
            if self.header.payloadStart == 1:
                startLen = 5 + data[5]
                self.body = data[startLen:]
            else:
                self.body = data[4:]

# ts = Ts("test.ts")
# for pkg in ts.body:
#     pass
class Ts:
    def __init__(self,pwd) -> None:
        self.body = []
        with open(pwd,'rb') as tsf:
            while True:
                tspck = tsf.read(188)
                if tspck == b'':
                    break
                self.body.append(TsPacket(tspck))

class TS:
    Sync = 0x47

def PAT():
    bt = bytearray([0xff]*188)
    hex = [
        0x47, 0x40, 0x00, 0x10, #ts packet hd
        0x00, #adaption
        0x00, 0xB0, 0x0D, 0x00, 0x01, 0xC1, 0x00, 0x00, 0x00, 0x01, 
        0xF0, 0x00, 0x2A, 0xB1, 0x04, 0xB2
    ]
    bt[0:20] = hex
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
    bt[0:30] = hex
    return bt

class PES():

    _StartCode = [0x00, 0x00, 0x01]
    _StreamId = {"video":0xe0,"audit":0xc0}
    _PESLength = [0x00,0x00]
    def __init__(self,pts,dts) -> None:
        self.data = bytearray([0]*188)
        self.data[0:3] = [0x00, 0x00, 0x01]
        self.data[3] = 0xe0
        self.data[4:6] = [0x00,0x00]
        self.data[6] = 0x80 # pes-info信息
        self.data[7] = 0xc0 # 默认存在dts和pts
        self.data[8] = 0x0a # len

        # pts
        self.data[9] = (3 << 4) | ((pts>>30) << 1) | 1
        gc = ((pts >> 15) & 0x7fff) << 1 | 1
        self.data[10] = gc >> 8
        self.data[11] = gc & 0xff
        gc = ((pts & 0x7fff) << 1 ) | 1
        self.data[12] = gc >> 8
        self.data[13] = gc & 0xff

        # dts
        self.data[14] = (1 << 4) | ((dts>>30) << 1) | 1
        gc = ((dts >> 15) & 0x7fff) << 1 | 1
        self.data[15] = gc >> 8
        self.data[16] = gc & 0xff
        gc = ((dts & 0x7fff) << 1 ) | 1
        self.data[17] = gc >> 8
        self.data[18] = gc & 0xff

a = PES(131940,126000)

print(a.data.hex(" "))