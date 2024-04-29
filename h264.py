# - h.264官方文档 https://www.itu.int/rec/T-REC-H.264
# h.264由多组nalu组成

import itertools


if __name__ == "__main__":
    hex = None
    with open("./vfile/d/output.h264", 'rb') as f:
        hex = bytearray(f.read())
    nal = None
    hexLen = len(hex)
    i = 0
    while i < hexLen:
        if hex[i] == 0 and hex[i+1] == 0:
            print(i)
            # break
        i+=1