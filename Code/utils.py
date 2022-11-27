
# 生成蓝牙数据包
# codes: 用户输入的字符串
def generatePacket(codes: str):
    # 设置蓝牙数据包的一些参数
    preamble = '01010101' # 前导码
    address = '10001110100010011011111011010110' # 广播地址
    codes_bytes = bytes(codes, "ascii")
    
    # 将输入的字符串转为二进制
    data = ""
    for x in codes_bytes:
        binary_converted = "{0:b}".format(x)
        for i in range(8 - len(binary_converted)):
            binary_converted = "0" + binary_converted
        data = data + binary_converted
    
    # 将输入数据分段并封包
    packetList = []
    data_size = len(data) / 8
    begin = 0
    while(begin < data_size):
        length = min(32, data_size - begin)
        b_length = bin(length)
        pdu_length = b_length[2:]
        for i in range(8 - len(pdu_length)):
            pdu_length = "0" + pdu_length

        end = begin + length
        pdu_data = data[begin:end]
        
        packet = preamble + address + pdu_length + pdu_data
        packetList.append(packet)
        
        begin += length

    return packetList



if __name__ == "__main__":
    generatePacket()