
class TsPacketHeader:
    def __init__(self,data) -> None:
        self.sync = data[0]
        self.error = data[1] >> 7  #是否报错
        self.payloadStart = data[1] >> 6 & 1 
        self.priority = data[1] >> 5 & 1 #优先级
        self.pid = int.from_bytes([data[1] & 0x1f,data[2]],"big")
        self.scrambling = data[3] >> 6 #传输加扰。
        self.adaption = data[3] >> 4 & 3
        self.continuity = data[3] & 0x0f

class TsPacket:
    def __init__(self,data) -> None:
        self.header = TsPacketHeader(data[0:4])
        self.body = []
        self.adaptLen = data[4]
        if self.header.adaption >= 2:#存在调整字段
            self.adapt = data[5:5+self.adaptLen]
            if self.header.adaption == 3:#同时存在es
                self.body = data[5+self.adaptLen:]
            else:
                self.body = []
        elif self.header.adaption == 1:
            if self.header.payloadStart == 1:
                startLen = 5 + data[5]
                self.body = data[startLen:]
            else:
                self.body = data[4:]

class Ts:
    def __init__(self,pwd) -> None:
        self.body = []
        with open(pwd,'rb') as tsf:
            while True:
                tspck = tsf.read(188)
                if tspck == b'':
                    break
                self.body.append(TsPacket(tspck))


#256
VideoPid = 0x100 

# 提取PES到文件
class PesHeader:
    def __init__(self,data) -> None:
        self.start_code_prefix = data[0:3]
        self.stream_id = data[3]
        self.pes_packet_length = int.from_bytes(data[4:6],'big')

        self.reserved = data[6] >> 6
        self.pes_scrambling_control = data[6] >> 4 & 3
        self.pes_priority = data[6] >> 3 & 1
        self.copyright = data[6] >> 1 & 1
        self.original_or_copy = data[6] & 1

        self.pts_dts_flags = data[7] >> 6
        self.escr_flags = data[7] >> 5 & 1
        self.es_rate_flag = data[7] >> 4 & 1
        self.dsm_trick_mode_flag = data[7] >> 3 & 1
        self.additional_copy_info_flag = data[7] >> 2 & 1
        self.pes_crc_flag = data[7] >> 1 & 1
        self.pes_extension_flag = data[7] & 1

        print(self.pts_dts_flags,self.escr_flags,self.es_rate_flag,self.dsm_trick_mode_flag)
        print(self.additional_copy_info_flag,self.pes_crc_flag,self.pes_extension_flag)

        exit()

        self.pes_header_data_length = data[8]
        

class Pes:
    def __init__(self,data) -> None:
        self.header = PesHeader(data[0:9])
        self.pes_header_data = data[9:9+self.pes_header_data_length]
        self.body = data[9+self.pes_header_data_length:]
        # print(self.pes_header_data)
        # print(self.body)


# 单信道
# 不做多路复用
class AnalyzePes:
    def __init__(self) -> None:
        self.PesVideo = []
        TmpPes = []
        ts = Ts("test.ts")
        self.PesVideoCount = 1
        for pkg in ts.body:
            if pkg.header.pid == VideoPid:
                if pkg.header.payloadStart == 1:
                    if self.PesVideoCount != 1:
                        self.PesVideo.append(Pes(TmpPes))
                    self.PesVideoCount += 1
                    TmpPes = []
                TmpPes += pkg.body
        self.PesVideo.append(Pes(TmpPes))

pes = AnalyzePes()
with open('test_mpegts.h264','wb') as ts:
    for pkg in pes.PesVideo:
        # print(pkg)
        ts.write(bytes(pkg.body))
