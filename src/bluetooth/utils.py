import numpy as np
import wave
import matplotlib.pyplot as plt
from scipy import signal

import FSK

# 蓝牙物理层数据包参数
PREAMBLE_SIZE = 1
ACCESS_ADDRESS_SIZE = 4
PDU_LENGTH_SIZE = 1
PDU_DATA_MAXSIZE = 10

# 参数配置
sample_rate = 48000
frequency_0 = 3000
frequency_1 = 5000
duration = 0.025
volume = 1

sample_width = 2
channel = 1
t = np.linspace(0, duration * channel, int(duration * sample_rate * channel))
sig_0 = 0.65*np.sin(2 * np.pi * frequency_0 * t)
sig_111 = np.sin(2 * np.pi * frequency_1 * t)
# 生成蓝牙数据包
# codes: 用户输入的字符串
def generatePacket(codes: str):
    # 设置蓝牙数据包的一些参数
    is_english = 1
    code_temp = bin(ord(codes[0]))[2:]
    if len(code_temp) > 8:
        is_english = 0
        print('开始是中文')
    packetList = []
    packet = ''
    for i in codes:
        #print((bin(ord(i))))
        #print(bin(ord(i))[2:])
        code_temp = bin(ord(i))[2:]
        if len(code_temp) > 8:
            for i in range(16 - len(code_temp)):
                code_temp = "0" + code_temp
            if is_english == 0:
                packet = packet + code_temp
                if len(packet) >= 80:
                    length = int(len(packet) / 16)
                    b_length = bin(length)
                    pdu_length = b_length[2:]
                    print("pdu_length: ", pdu_length)
                    for i in range(8 - len(pdu_length)):
                        pdu_length = "0" + pdu_length
                    packet = pdu_length + packet
                    packetList.append(packet)
                    packet = ''
            if is_english == 1:
                is_english = 0
                length = int(len(packet))
                b_length = bin(length)
                pdu_length = b_length[2:]
                print("pdu_length: ", pdu_length)
                for i in range(8 - len(pdu_length)):
                    pdu_length = "0" + pdu_length
                packet = pdu_length + packet
                packetList.append(packet)
                packet = code_temp
        else:
            for i in range(8 - len(code_temp)):
                code_temp = "0" + code_temp
            if is_english == 1:
                packet = packet + code_temp
                if len(packet) >= 80:
                    length = int(len(packet))
                    b_length = bin(length)
                    pdu_length = b_length[2:]
                    print("pdu_length: ", pdu_length)
                    for i in range(8 - len(pdu_length)):
                        pdu_length = "0" + pdu_length
                    packet = pdu_length + packet
                    packetList.append(packet)
                    packet = ''
            if is_english == 0:
                is_english = 1
                length = int(len(packet)/16)
                b_length = bin(length)
                pdu_length = b_length[2:]
                print("pdu_length: ", pdu_length)
                for i in range(8 - len(pdu_length)):
                    pdu_length = "0" + pdu_length
                packet = pdu_length + packet
                packetList.append(packet)
                packet = code_temp
    if len(packet) > 0:
        if is_english == 0:
            length = int(len(packet)/16)
            b_length = bin(length)
            pdu_length = b_length[2:]
            print("pdu_length: ", pdu_length)
            for i in range(8 - len(pdu_length)):
                pdu_length = "0" + pdu_length
            packet = pdu_length + packet
            packetList.append(packet)
        if is_english == 1:
            length = int(len(packet))
            b_length = bin(length)
            pdu_length = b_length[2:]
            print("pdu_length: ", pdu_length)
            for i in range(8 - len(pdu_length)):
                pdu_length = "0" + pdu_length
            packet = pdu_length + packet
            packetList.append(packet)
    return packetList
  
        




'''
    codes_bytes = bytes(codes, "ascii")
    #print(codes_bytes)
    # 将输入的字符串转为二进制
    data = ""
    for x in codes_bytes:
        #print(x)
        binary_converted = "{0:b}".format(x)
        for i in range(8 - len(binary_converted)):
            binary_converted = "0" + binary_converted
        #print(binary_converted)
        data = data + binary_converted
    
    # 将输入数据分段并封包
    packetList = []
    data_size = int(len(data))
    #print('data_size: ', data_size)
    begin = 0
    while(begin < data_size):
        length = min(PDU_DATA_MAXSIZE * 8, data_size - begin)
        length = int(length)
        print("length: ", length)
        b_length = bin(length)
        pdu_length = b_length[2:]
        print("pdu_length: ", pdu_length)
        for i in range(8 - len(pdu_length)):
            pdu_length = "0" + pdu_length
        print("pdu_length_converted: ", pdu_length)
        end = begin + length
        pdu_data = data[begin:end]
        print('begin: ', begin,' end: ', end)
        # packet = preamble + address + pdu_length + pdu_data
        packet = pdu_length + pdu_data
        packetList.append(packet)
        
        begin += length

    return packetList
    '''

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
    sig = data[0]

    return t, sig
    
def sig2num_list(sig):
    sig_list = list(sig)
    sig_num_list = [int(x) for x in sig_list]
    return sig_num_list

def get_preamble_sig(f0, f1):
    t0 = np.linspace(0, 1 * duration * channel, 1 * int(duration * sample_rate * channel))
    preamble = signal.chirp(t0, f0=f0, f1=f1, t1=0.025, method='linear')
    return preamble

def extract_message(sig, begin):
    temp_index = 0
    sum_0 = 0
    sum_1 = 0
    index = begin
    num_power = 256
    message_len = 0
    while num_power > 1:
        begin = index
        index += 1200
        sig1 = sig[begin: begin+1200]
        temp_index = temp_index+1
        if temp_index==2 or temp_index==3:
            sum_0 = sum_0 + 2*abs(np.correlate(sig1, sig_0)[0])
            sum_1 = sum_1 + 2*abs(np.correlate(sig1, sig_111)[0])
        else:
            sum_0 = sum_0 + abs(np.correlate(sig1, sig_0)[0])
            sum_1 = sum_1 + abs(np.correlate(sig1, sig_111)[0])
        if temp_index == 4:
            num_power = num_power / 2
            if sum_0 < sum_1:
                message_len = message_len + num_power
            temp_index = 0
            sum_0 = 0
            sum_1 = 0
    #print("信號包的長度爲:",message_len)
    #if message_len > 80:
        #return 0 #发生丢包
    message_list = ''
    if message_len >= 8:
        message_len = int(message_len/8)
        if message_len > 10:
            message_len = 10 
        for i in range(message_len):
            num_power = 256
            message_len = 0
            while num_power > 1:
                begin = index
                index += 1200
                if index >= len(sig):
                    return 0 #发生丢包
                sig1 = sig[begin: begin+1200]
                temp_index = temp_index+1
                if temp_index==2 or temp_index==3:
                    sum_0 = sum_0 + 1.6*abs(np.correlate(sig1, sig_0)[0])
                    sum_1 = sum_1 + 1.6*abs(np.correlate(sig1, sig_111)[0])
                else:
                    sum_0 = sum_0 + abs(np.correlate(sig1, sig_0)[0])
                    sum_1 = sum_1 + abs(np.correlate(sig1, sig_111)[0])
                if temp_index == 4:
                    num_power = num_power / 2
                    if sum_0 < sum_1:
                        message_len = message_len + num_power
                    temp_index = 0
                    sum_0 = 0
                    sum_1 = 0
            if message_len > 128:
                message_len = message_len-128
            print("信息為:",chr(int(message_len)))
            message_list = message_list+(chr(int(message_len)))
    else:
        for i in range(int(message_len)):
            num_power = 65536
            message_len = 0
            while num_power > 1:
                begin = index
                index += 1200
                if index >= len(sig):
                    return 0 #发生丢包
                sig1 = sig[begin: begin+1200]
                temp_index = temp_index+1
                if temp_index==2 or temp_index==3:
                    sum_0 = sum_0 + 2*abs(np.correlate(sig1, sig_0)[0])
                    sum_1 = sum_1 + 2*abs(np.correlate(sig1, sig_111)[0])
                else:
                    sum_0 = sum_0 + abs(np.correlate(sig1, sig_0)[0])
                    sum_1 = sum_1 + abs(np.correlate(sig1, sig_111)[0])
                if temp_index == 4:
                    num_power = num_power / 2
                    if sum_0 < sum_1:
                        message_len = message_len + num_power
                    temp_index = 0
                    sum_0 = 0
                    sum_1 = 0
            print("信息為:",chr(int(message_len)))
            message_list = message_list+(chr(int(message_len)))
    return message_list


# 从信号中提取中蓝牙数据包
# sig: 信号
# preamble_sig: 前导码调制成的信号
def extract_packet(sig, preamble_sig):
    # 先滤波
    #sig = bandpass(sig, 3800, 700)
    # print(len(sig), len(preamble_sig))
    #print("sig after bandpass")
    #plt.plot(sig)
    #plt.show()

    packet_flag = True
    packetList = []
    index = 0
    # 匹配前导码
    while packet_flag:
        try:
            cross_corr = np.correlate(sig, preamble_sig, 'valid')
        except:
            break

        begin = 0
        for i, value in enumerate(cross_corr):
            if value > 50000:
                begin = i
                break

        window_length = int(duration * sample_rate)
        end = min(begin + window_length * 2, len(cross_corr))
        match = max(cross_corr[begin:end])
        #match_index = list(cross_corr).index(match)+7200
        match_index = 45900
        print('begin, end: ', begin, end)
        print('match_index: ', match_index)
        print("cross_corr")
        plt.plot(cross_corr)
        plt.show()
        # FFT变换
        # 8个一组提取01数据
        packet = []

        byte_num = 0
        bit_num = 0
        payload_length = 0
        one_byte = ''

        index = match_index
        flag = True
        end1 = 0
        div_value = 0
        last_div_value = 0

        ###测试
        #    for i in range(12):
        #        print(i)
        #        match_index = match_index+10
        #        sig1 = list(sig)[match_index: match_index + window_length]
        #        frequency_high, frequency_low = fft_frequency(sig1)
         #   print('hello')
        ###测试

        temp_index = 0
        sum_0 = 0
        sum_1 = 0
        while flag:
            begin = index
            sig1 = sig[begin: begin+1200]
            #frequency_high, frequency_low = fft_frequency(sig1)
            #print(len(sig1),"   ",len(sig_0),"   ",len(sig_1))
            #print(np.correlate(sig1, sig_0)[0],"  ", np.correlate(sig1, sig_111)[0])
            temp_index = temp_index+1
            #print("和0的相似度",np.correlate(sig1, sig_0))
            #print("和1的相似度",np.correlate(sig1, sig_111))
            if temp_index==2 or temp_index==3:
                sum_0 = sum_0 + 2*abs(np.correlate(sig1, sig_0)[0])
                sum_1 = sum_1 + 2*abs(np.correlate(sig1, sig_111)[0])
                #fft_frequency(sig1)
            else:
                sum_0 = sum_0 + abs(np.correlate(sig1, sig_0)[0])
                sum_1 = sum_1 + abs(np.correlate(sig1, sig_111)[0])
            if temp_index == 4:
                #print("和0的相似度",sum_0)
                #print("和1的相似度",sum_1)
                # 合并
                decode_char = '0' 
                if abs(sum_1) > abs(sum_0):
                    decode_char = '1' 
                index += window_length
                bit_num += 1
                one_byte += decode_char

                if bit_num == 8:
                    bit_num = 0 
                    byte_num += 1
                    print("byte", byte_num, "--",one_byte)     
                    t = input()      
                    if byte_num == 7:
                        payload_length = int(one_byte, 2)
                        print("payload",payload_length)
                    packet.append(one_byte)

                    if byte_num == 7 + payload_length/8:
                        flag = False
                    
                    one_byte = ''
                temp_index = 0
                sum_0 = 0
                sum_1 = 0
            else:
                index += window_length
        packetList.append(packet)
        sig = sig[end1:]
    return packetList

# 给一段信号，FFT分析频率
def fft_frequency(sig):
    n = len(sig)
    k = np.arange(n)            
    T = n / sample_rate         # 共有的周期数
    frq = k/T                   # 两侧频率范围
    frq1 = frq[range(int(n/2))] # 由于对称性，取一半区间

    fft_sig = np.fft.fft(sig)
    fft_sig = fft_sig[range(int(n/2))]
    abs_fft_sig = abs(fft_sig)
    #max_value = max(abs_fft_sig)
    plt.plot(frq1, abs_fft_sig)
    plt.show()
    #max_index = list(abs_fft_sig).index(max_value)
    frequency_high = abs_fft_sig[list(frq1).index(frequency_1+40)]
    frequency_low = abs_fft_sig[list(frq1).index(frequency_0+40)]
    print(frequency_high)
    
    return frequency_high, frequency_low

# 带通滤波
def bandpass(y: np.ndarray, high, low):
    # 设置带通滤波的上下界
    wn1 = 2 * low / sample_rate
    wn2 = 2 * high / sample_rate
    # 按时间间隔的每个滑动窗口进行滤波
    length = int(duration * sample_rate * channel)
    window_num = int(y.size / length)
    result = np.array([])
    for i in range(window_num):
        b, a = signal.butter(6, [wn1, wn2], 'bandpass')
        filtedData = signal.filtfilt(b, a, y[i * length : (i+1) * length])
        result = np.append(result, filtedData)
    return result

def STFT(t, y, window):
    N = len(t)
    fs = (N-1) /(t[N-1] - t[0])
    f, t, Zxx = signal.stft(y, fs, nperseg = window)
    plt.pcolormesh(t, f, np.abs(Zxx))
    plt.title('STFT Analysis')
    plt.ylabel('Frequency(Hz)')
    plt.xlabel('Time(sec)')
    plt.colorbar()
    plt.show()

if __name__ == "__main__":

    t, sig = get_signal_from_wav("len2.wav")
    sig1 = [0]*48000
    # 添加一段空白
    t1 = np.linspace(0,1,48001)
    t = t + 1
    t = np.append(t1[:-1], t)
    sig = np.append(sig1,sig)    
    plt.plot(t, sig)
    plt.show()

    # 前导码匹配
    preamble = get_preamble_sig(6000,6500)
    cross_corr = np.correlate(sig, preamble, 'valid')

    plt.plot(cross_corr)
    plt.show()

    #match_pos = np.argmax(cross_corr)
    #print(match_pos) #开始匹配上的位置

    #extract_message(sig, match_pos+4800)

    index = 0
    match_list = []
    while index < len(cross_corr):
        if cross_corr[index] > 50000:
            temp = cross_corr[index:index+3600]
            match_pos = np.argmax(temp)
            match_pos = match_pos + index
            print(match_pos) #开始匹配上的位置
            match_list.append(match_pos)
            index = index + 3600
        else:
            index = index+1
    
    for match_pos in match_list:
        extract_message(sig, match_pos+4800)