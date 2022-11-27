import numpy as np
import wave
import matplotlib.pyplot as plt

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

# 将wav文件读取为信号
# fileName: 文件名
def get_signal_from_wav(fileName):
    wave_file = wave.open(fileName,'rb')
    # 读取参数
    nchannels = wave_file.getnchannels()
    frame_rate = wave_file.getframerate()
    nframes = wave_file.getnframes()
    # 读取波形数据
    str_data = wave_file.readframes(nframes)
    wave_file.close()
    data = np.frombuffer(str_data, dtype=np.short)
    data = np.reshape(data,[nframes,nchannels])
    data = data.T
    t = np.arange(0,nframes) * (1.0/frame_rate)
    sig = data[0]/1000

    return t, sig
    
def sig2num_list(sig):
    sig_list = list(sig)
    sig_num_list = [int(x) for x in sig_list]
    return sig_num_list

# 包络检波
def envelope_extraction(signal):
    s = signal.astype(float)

    x = []
    y = [] 

    # 检测波峰和波谷，并标记其在sig中的位置 

    for k in range(1,len(s)-1):
        if (s[k]-s[k-1]>0) and (s[k]-s[k+1]>0):
            x.append(k)
            y.append(s[k])

    # 填充最后一个点
    x.append(len(s)-1)
    y.append(s[-1])
    
    # 把包络转为和输入数据相同大小的数组
    envelope_y = np.zeros(len(signal))
    
    # 上包络
    last_idx,next_idx = 0, 0
    k, b = linear_params(x[0], y[0], x[1], y[1]) #初始的k,b
    for i in range(1,len(envelope_y)-1):

        if i not in x:
            v = k * i + b
            envelope_y[i] = v
        else:
            idx = x.index(i)
            envelope_y[i] = y[idx]
            last_idx = x.index(i)
            next_idx = x.index(i) + 1
            # 求连续两个点之间的直线方程
            k, b = linear_params(x[last_idx], y[last_idx], x[next_idx], y[next_idx])        
    return envelope_y

# 一次函数求解 y = kx + b
# (x1, y1) (x2, y2) 两个点
# 返回 k, b 
def linear_params(x1, y1, x2, y2):
    k = (y1 - y2) / (x1 - x2)
    b = (x1*y2 - x2*y1) / (x1 - x2)
    return k, b

# 从信号中提取中蓝牙数据包
# sig: 信号
# preamble_sig: 前导码调制成的信号
def extract_packet(sig, preamble_sig):
    # 和前导码求相关性
    cross_corr = np.correlate(sig, preamble_sig, 'valid')
    # 计算包络
    envelope_corr = envelope_extraction(cross_corr)
    # TODO: 测试并设定阈值，然后取第一个极值作为前导码匹配点
    # TODO: 或者参考sgl，取一段窗口，在其中取最值作为前导码匹配点