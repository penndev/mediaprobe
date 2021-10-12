

# typedef struct TS_packet_header
# {
# 	unsigned sync_byte                    : 8;	//同步字节, 固定为0x47,表示后面的是一个TS分组
# 	unsigned transport_error_indicator    : 1;	//传输误码指示符
# 	unsigned payload_unit_start_indicator : 1;	//效荷载单元起始指示符
# 	unsigned transport_priority           : 1;	//传输优先, 1表示高优先级,传输机制可能用到，解码用不着
# 	unsigned PID                          : 13;	//PID
# 	unsigned transport_scrambling_control : 2;	//传输加扰控制
# 	unsigned adaption_field_control       : 2;	//自适应控制 01仅含有效负载，10仅含调整字段，11含有调整字段和有效负载。为00解码器不进行处理
# 	unsigned continuity_counter           : 4;	//连续计数器 一个4bit的计数器，范围0-15
# } TS_packet_header;


# if (adaption_field_control == '10' || adaption_field_control == '11') {
#         adaption_fields() //调整字段的处理
# }
# if (adaption_field_control == '01' || adaption_field_control == '11') {
# 	for(i = 0; i < N ; i++) //N值 = 184 - 调整字段的字节数
#     {

#     }
# }

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
        self.header = TsPacket(data[0:4])
        if self.header.adaption >= 2:#存在调整字段
            self.adaptLen = data[4]
            self.adapt = data[5:5+self.adaptLen]

class Ts:
    def __init__(self,pwd) -> None:
        self.body = []
        with open(pwd,'rb') as tsf:
            size = 0
            while True:
                size += 1
                tspck = tsf.read(188)
                if tspck == b'':
                    break
                self.body.append(TsPacket(tspck))

# Ts("test.ts")
print(TsPacketHeader([0x47, 0x40, 0x11,0x10]))