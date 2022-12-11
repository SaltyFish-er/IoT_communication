import numpy as np
import wave
import matplotlib.pyplot as plt
from scipy import signal

import FSK

# 蓝牙物理层数据包参数
PREAMBLE_SIZE = 1
ACCESS_ADDRESS_SIZE = 4
PDU_LENGTH_SIZE = 1
PDU_DATA_MAXSIZE = 4

# 参数配置
sample_rate = 48000
frequency_0 = 1000
frequency_1 = 3500
duration = 0.025
volume = 1

sample_width = 2
channel = 1


# 生成蓝牙数据包
# codes: 用户输入的字符串
def generatePacket(codes: str):
    # 设置蓝牙数据包的一些参数
    preamble = '01010101' # 前导码
    address = '10001110100010011011111011010110' # 广播地址
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
    sig = data[0]

    return t, sig
    
def sig2num_list(sig):
    sig_list = list(sig)
    sig_num_list = [int(x) for x in sig_list]
    return sig_num_list

# 从信号中提取中蓝牙数据包
# sig: 信号
# preamble_sig: 前导码调制成的信号
def extract_packet(sig, preamble_sig):
    # 先滤波
    sig = bandpass(sig, 3800, 700)
    # print(len(sig), len(preamble_sig))
    # print("sig after bandpass")
    # plt.plot(sig)
    # plt.show()

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
            if value > 0.5:
                begin = i
                break

        window_length = int(duration * sample_rate)
        end = min(begin + window_length * 8, len(cross_corr))
        match = max(cross_corr[begin:end])
        match_index = list(cross_corr).index(match)
        print('begin, end: ', begin, end)
        print('match_index: ', match_index)
        # print("cross_corr")
        plt.plot(cross_corr)
        plt.title('cross correlation Analysis')
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

        while flag:
            # fft解码
            end1 = min(index + window_length, len(sig))
            sig1 = list(sig)[index: end1]
            frequency = fft_frequency(sig1)
            # try:
            #     frequency_es = fft_frequency(sig1)
            # except:
            #     print('len(sig)', len(sig))
            #     print('index and end', index, end1)
            dis_0 = abs(frequency - frequency_0)
            dis_1 = abs(frequency - frequency_1)
            decode_char = '0' 
            if dis_0 > dis_1:
                decode_char = '1'
                
            index += window_length

            # 合并
            bit_num += 1
            one_byte += decode_char

            if bit_num == 8:
                bit_num = 0 
                byte_num += 1
                print("byte", byte_num, "--",one_byte)           
                if byte_num == 6:
                    payload_length = int(one_byte, 2)
                    print("payload",payload_length)
                packet.append(one_byte)

                if byte_num == 6 + payload_length/8:
                    flag = False
                
                one_byte = ''
            
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
    max_value = max(abs_fft_sig)
    # plt.plot(frq1, abs_fft_sig)
    # plt.show()
    max_index = list(abs_fft_sig).index(max_value)
    # frequency_high = abs_fft_sig[list(frq1).index(frequency_1+20)]
    # frequency_low = abs_fft_sig[list(frq1).index(frequency_0)]
    frequency = frq1[max_index]
    return frequency

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
    # generatePacket("apple pen")
    # exit(0)
    t, sig = get_signal_from_wav("test.wav")
    sig1 = [0]*48000
    t1 = np.linspace(0,1,48001)
    t = t + 1
    t = np.append(t1[:-1], t)
    sig = np.append(sig1,sig)
    #sig = bandpass(sig, 1800, 800)
    STFT(t, sig, 300)
    # print(len(t), t[-1])
    preamble_sig = FSK.Modu_Preamble()
    # sig = sig[9600:]
    packetList = extract_packet(sig, preamble_sig)
    print(packetList)
    result = ''
    for packet in packetList:
        result += FSK.Demodulator(packet)
    print("decode string:", result)
    #print("cal envelope corr...")
    #envelope_corr = envelope_extraction(cross_corr)
    #plt.subplot(211)
    #plt.plot(cross_corr)
    #plt.subplot(212)
    #plt.plot(envelope_corr)

    #plt.plot(cross_corr)
    #plt.show()