#256
VideoPid = 0x100 
AudioPid = 0x101 

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

class TsPacketAdapt:
    def __init__(self,data) -> None:
        self.discontinuity_indicator = data[0] >> 7 & 1
        self.random_access_indicator = data[0] >> 6 & 1
        self.elementary_stream_priority_indicator = data[0] >> 5 & 1
        self.PCR_flag = data[0] >> 4 & 1
        self.OPCR_flag = data[0] >> 3 & 1
        self.splicing_point_flag = data[0] >> 2 & 1
        self.transport_private_data_flag = data[0] >> 1 & 1
        self.adaptation_field_extension_flag = data[0] & 1
        if self.PCR_flag == 1:
            self.pcr = (int.from_bytes(data[1:5],'big') << 2) + (data[4] >> 6)

class TsPacket:
    def __init__(self,data) -> None:
        self.header = TsPacketHeader(data[0:4])
        self.body = []
        self.adaptLen = data[4]
        if self.header.adaption >= 2:#存在调整字段
            if(self.adaptLen>0):
                self.adapt = TsPacketAdapt(data[5:5+self.adaptLen])
            if self.header.adaption == 3:#同时存在es
                self.body = data[5+self.adaptLen:]
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

        print(data[7],self.pts_dts_flags,self.escr_flags,self.es_rate_flag,self.dsm_trick_mode_flag,self.additional_copy_info_flag,self.pes_crc_flag,self.pes_extension_flag)
        self.pes_header_data_length = data[8]

        self.pts = 0
        self.dts = 0
    
    def splitFlag(self,data):
        if(self.pts_dts_flags > 1):# must pts
            pts = []
            pts.append(data[0]>>3 & 1)
            pts.append(((data[0]>>1 & 5)<<5) + (data[1]>>2))
            pts.append((data[1]<<6 & 3) + (data[2]>>2))
            pts.append(((data[2]>>1 & 1)<<7) + (data[3]>>1))
            pts.append(((data[3]&1)<<7) + (data[4]>>1))
            self.pts = int.from_bytes(pts,'big')
        if(self.pts_dts_flags > 2): # had dts
            dts = []
            dts.append(data[5]>>3 & 1)
            dts.append(((data[5]>>1 & 5)<<5) + (data[6]>>2))
            dts.append((data[6]<<6 & 3 ) + (data[7]>>2))
            dts.append(((data[7]>>1 & 1) << 7) + (data[8]>>1))
            dts.append(((data[8]&1)<<7) + (data[9]>>1))
            self.dts = int.from_bytes(dts,'big')
        print(data,self.pts,self.dts)
        exit()


class Pes:
    def __init__(self,data) -> None:
        self.header = PesHeader(data[0:9])
        headerEnd = 9 + self.header.pes_header_data_length
        self.header.splitFlag(data[9:headerEnd])
        self.body = data[headerEnd:]


# 单信道
# 不做多路复用
class AnalyzePes:
    def __init__(self) -> None:
        self.PesVideo = []
        self.PesAudio = []

        TmpPesVideo = []
        TmpPesAudio = []
        
        self.PesVideoCount = 1
        self.PesAudioCount = 1

        ts = Ts("test.ts")
        for pkg in ts.body:
            if pkg.header.pid == VideoPid:
                if pkg.header.payloadStart == 1:
                    if self.PesVideoCount != 1:
                        self.PesVideo.append(Pes(TmpPesVideo))
                    self.PesVideoCount += 1
                    TmpPesVideo = []
                TmpPesVideo += pkg.body
            if pkg.header.pid == AudioPid:
                if pkg.header.payloadStart == 1:
                    if self.PesAudioCount != 1:
                        self.PesAudio.append(Pes(TmpPesAudio))
                    self.PesAudioCount += 1
                    TmpPesAudio = []
                TmpPesAudio += pkg.body
        self.PesVideo.append(Pes(TmpPesVideo))
        self.PesVideo.append(Pes(TmpPesAudio))

pes = AnalyzePes()
with open('test_mpegts.h264','wb') as ts:
    for pkg in pes.PesVideo:
        ts.write(bytes(pkg.body))

with open('test_mpegts.aac','wb') as ts:
    for pkg in pes.PesAudio:
        ts.write(bytes(pkg.body))
