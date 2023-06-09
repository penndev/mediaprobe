'''
>  mpeg2-ts 初次接触是因为hls默认生成的视频封装格式。
给我的感觉是封装复杂而且其他的0xff的填充也造成冗余，
不太适应现在较为稳定的网络传输环境（本来就是为了无线通讯）。
但是还是值得学习的。

参考文档：
    - `https://tsduck.io/download/docs/mpegts-introduction.pdf`
    - `https://www.itu.int/rec/T-REC-H.222.0`
    - `https://en.wikipedia.org/wiki/MPEG_transport_stream`
    - `https://dvd.sourceforge.net/dvdinfo/pes-hdr.html`
'''


class Pes:
    def __init__(self) -> None:
        self.head = None



    def test(self,filepath:str):
        pes_video = bytearray()
        with open(filepath,"rb") as i_file:
            while True:
                # 文件字节流转换为 Ts Pakcet
                i_pk = i_file.read(188)
                if not i_pk:
                    break
                tspack = TsPacket().set(i_pk)
                
                # Ts Packet 提取 PES
                if tspack.pid == 0x100: # 视频
                    # 如果pes_video空则表示是第一个pes
                    if tspack.payload_unit_start_indicator == 1 and len(pes_video) > 0: 
                        # 如何操作PES数据呢。
                        print(pes_video)

                        pes_video = tspack.body # 必须置空
                    else:
                        pes += tspack.body
                # 提取出pes数据


    def __del__(self):
        self.file.close()

def get_pcr(data: bytes):
    '''
    根据文档提取 pcr 的数据
    '''
    pcr_base = 0 | (data[0] & 0xFF) << 25
    pcr_base |= (data[1] & 0xFF) << 17
    pcr_base |= (data[2] & 0xFF) << 9
    pcr_base |= (data[3] & 0xFF) << 1
    pcr_base |= (data[4] & 0x80) >> 7
    pcr_extension = ((data[4] & 0x01) << 8) | (data[5] & 0xFF)
    return pcr_base, pcr_extension

def set_pcr(pcr_base: int, pcr_extension: int) -> bytes:
    '''
    根据文档将 pcr 数据生成 bytes
    '''
    data = bytearray(6)
    data[0] = (pcr_base >> 25) & 0xFF
    data[1] = (pcr_base >> 17) & 0xFF
    data[2] = (pcr_base >> 9) & 0xFF
    data[3] = (pcr_base >> 1) & 0xFF
    data[4] = (pcr_base << 7 & 0xFF | 0x7e) | ((pcr_extension >> 8) & 0x01) 
    data[5] = pcr_extension & 0xFF
    return bytes(data)

class TsPacket:
    def __init__(self) -> None:
        '''
            Transport Packet 数据包进行拆包组包的实际实现
        '''
        ##### ts packet header
        self.sync = 0x47 # 固定标识头 0x47 71
        self.transport_error_indicator = None
        self.payload_unit_start_indicator = None
        self.transport_priority = None
        self.pid = None
        self.transport_scrambling_control = None
        self.adaptation_field_control = None
        self.continuity_counter = None
        # ts packet adaptation 
        self.adaptation_field_length = None  
        self.discontinuity_indicator = None 
        self.random_access_indicator = None 
        self.elementary_stream_priority_indicator = None 
        self.PCR_flag = None 
        self.OPCR_flag = None 
        self.splicing_point_flag = None 
        self.transport_private_data_flag = None 
        self.adaptation_field_extension_flag = None 
        self.pcr_base = None      # - if self.PCR_flag == 1
        self.pcr_extension = None # -  (pcr_base * 300 + pcr_extension) / 27hz = pcr
        # pes data
        self.body = None

    def set(self,data:bytes):
        '''
            将 188个字节进行类实例的填充
        '''
        if len(data) != 188 :
            raise Exception("数据长度不足188")
        if data[0] != 0x47:
            raise Exception("同步字节错误，应为0x47")
        self.sync = data[0]
        self.transport_error_indicator = data[1] >> 7
        self.payload_unit_start_indicator = data[1] >> 6 & 1 
        self.transport_priority = data[1] >> 5 & 1
        self.pid = int.from_bytes([data[1] & 0x1f,data[2]],"big")
        self.transport_scrambling_control = data[3] >> 6
        self.adaptation_field_control = data[3] >> 4 & 3
        self.continuity_counter = data[3] & 0x0f
        if self.adaptation_field_control == 3 or self.adaptation_field_control == 2: 
            self.adaptation_field_length = data[4]
            self.discontinuity_indicator = data[5] >> 7
            self.random_access_indicator = (data[5] >> 6) & 1
            self.elementary_stream_priority_indicator = (data[5] >> 5) & 1 
            self.PCR_flag = (data[5] >> 4) & 1 
            self.OPCR_flag = (data[5] >> 3) & 1 
            self.splicing_point_flag = (data[5] >> 2) & 1 
            self.transport_private_data_flag =  (data[5] >> 1) & 1 
            self.adaptation_field_extension_flag = data[5] & 1 
            if self.PCR_flag == 1 :
                self.pcr_base, self.pcr_extension = get_pcr(data[6:12])
            self.body = data[5+self.adaptation_field_length:]
        elif self.adaptation_field_control == 1:
            self.body = data[4:]
        else:
            raise Exception("错误的 adaptation_field_control")
        return self

    def get(self):
        '''
            封装数据到ts 字节数据
        '''
        data = bytearray([0XFF] * 188)
        data[0] = self.sync
        data[1] = 0
        if self.transport_error_indicator : data[1] |= 0b10000000
        if self.payload_unit_start_indicator : data[1] |= 0b1000000
        if self.transport_priority : data[1] |= 0b100000
        data[1] |= (self.pid >> 8) & 0b11111
        data[2] = self.pid & 0xff
        data[3] = 0
        data[3] |= (self.transport_scrambling_control & 0xff) << 6
        data[3] |= (self.adaptation_field_control & 0b111111) << 4
        data[3] |= self.continuity_counter & 0b1111
        # 完成head
        if self.adaptation_field_control == 3 or self.adaptation_field_control == 2:
            data[4] = self.adaptation_field_length
            data[5] = 0 | self.discontinuity_indicator << 7
            data[5] |= self.random_access_indicator << 6
            data[5] |= self.elementary_stream_priority_indicator << 5
            data[5] |= self.PCR_flag << 4
            data[5] |= self.OPCR_flag << 3
            data[5] |= self.splicing_point_flag << 2
            data[5] |= self.transport_private_data_flag << 1
            data[5] |= self.adaptation_field_extension_flag
            if self.PCR_flag == 1 :
                data[6:12]  = set_pcr(self.pcr_base, self.pcr_extension)
            data[5+self.adaptation_field_length:] = self.body
        elif self.adaptation_field_control == 1:
            # if self.payload_unit_start_indicator == 1:
            #     raise Exception("特殊情况")
            # else:
                data[4:] = self.body
        else:
            raise Exception("错误的 adaptation_field_control")
        if len(data) != 188:
            raise Exception("错误的 数据长度")
        return data

    def test(self,file:str):
        '''进行ts拆包封装测试'''
        with open(file,'rb') as i_file:
            with open("new_" + file,"wb") as o_file: 
                while True:
                    i_pk = i_file.read(188)
                    if not i_pk:
                        break
                    o_file.write(TsPacket().set(i_pk).r_ts.get())

if __name__ == "__main__":
    
    print(Pes().test("file/in.ts"))