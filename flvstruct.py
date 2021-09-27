# 官方flv标准介绍
# https://www.adobe.com/content/dam/acom/en/devnet/flv/video_file_format_spec_v10.pdf

class FlvHeader:
    data = None
    size = None
    def setHeaderData(self,data):
        self.data = data
    def setPreviousTagSize(self,data):
        self.size = data




class Flv:
    header = None
    def __init__(self,fileDir) -> None:
        self.header = FlvHeader
        with open(fileDir, 'rb') as f:
            self.header.setHeaderData(f.read(9))
            self.header.setPreviousTagSize(f.read(4))
            self.
            while(True):

