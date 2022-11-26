import random
import numpy as np
import wave
import struct
import matplotlib.pyplot as plt
from scipy import signal

# 参数配置
sample_rate = 48000
frequency = 20000
duration = 0.025
volume = 1

sample_width = 2
channel = 1

# 预处理函数，如果待调制数据长度不是偶数，添加0
# codes: 待调制的数据
def preProcess(codes: str):
    flag = False
    if len(codes) % 2 == 1:
        codes = codes + "0"
        flag = True
    return codes, flag

# QPSK调制函数
# codes: 待调制的数据，0/1数组
# fileName:保存wav到的文件
# sigSNR: 信噪比
def Modulator(codes, fileName, sigSNR):
    # 生成I信号和Q信号
    t = np.linspace(0, duration * channel, int(duration * sample_rate * channel))
    sigI = np.sin(2 * np.pi * frequency * t)
    sigQ = np.cos(2 * np.pi * frequency * t)

    # 生成两路基带信号，并相加
    cLen = len(codes)
    sig = []
    for i in range(int(cLen/2)):
        fI = (1 - 2 * int(codes[i*2])) * np.sqrt(2) / 2
        fQ = (1 - 2 * int(codes[i*2 + 1])) * np.sqrt(2) / 2
        # print("i=",i,",fI=",fI,",fQ=",fQ)
        sig = np.append(sig, fI * sigI + fQ * sigQ)

    sig = sig + add_noise(sig, sigSNR)
    # 保存信号波形为.wav文件
    wav_file = wave.open(fileName, 'wb')
    wav_file.setnchannels(channel)
    wav_file.setframerate(sample_rate)
    wav_file.setsampwidth(sample_width)
    for i in sig:
        # wave 只能以int形式保存帧，因此必须*1000以保证信息正常，在解调时重新配置就好了
        value = struct.pack('<h', int(i*1000))
        wav_file.writeframesraw(value)
    wav_file.close()
    return sig

# QBSK解调函数
# fileName: 调制数据得到的信号文件
# flag: 是否去掉最后一位
def Demodulator(fileName, flag):
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

    # 进行带通滤波
    sig = bandpass(sig)

    # 生成sin信号和cos信号
    t0 = np.linspace(0, duration * nchannels, int(duration * frame_rate * nchannels))
    y1 = np.sin(2 * np.pi * t0 * frequency) * volume
    y2 = np.cos(2 * np.pi * t0 * frequency) * volume
    
    # 计算每个间隔的积分得到i,q序列
    index = 0
    seq_i = []
    seq_q = []
    while index < len(sig):
        step_num = int(frame_rate * duration * nchannels)
        sig_interval = sig[index : index + step_num]
        sig_interval_i = 0
        sig_interval_q = 0
        for j in range(len(sig_interval)):
            sig_interval_i += sig_interval[j] * y1[j] / frame_rate * 2 / duration / frequency
            sig_interval_q += sig_interval[j] * y2[j] / frame_rate * 2 / duration / frequency
        seq_i.append(sig_interval_i)
        seq_q.append(sig_interval_q)
        index = index + step_num

    # 根据i,q序列还原0,1序列
    seq = []
    for i in range(len(seq_i)):
        if seq_i[i] > 0 and seq_q[i] > 0:
            seq.append(0)
            seq.append(0)
        elif seq_i[i] > 0 and seq_q[i] <= 0:
            seq.append(0)
            seq.append(1)
        elif seq_i[i] <= 0 and seq_q[i] > 0:
            seq.append(1)
            seq.append(0)
        elif seq_i[i] <= 0 and seq_q[i] <= 0:
            seq.append(1)
            seq.append(1)
    seq = [str(i) for i in seq]
    if flag:
        seq = seq[:-1]
    seq = ''.join(seq)
    return seq

# 添加白噪音的函数
# sig: 待添加白噪音的信号
# sigSNR: 模拟信道的信噪比
def add_noise(sig, sigSNR):
    sig_std =  np.sqrt(np.linalg.norm(sig - sig.mean()) ** 2 / sig.shape[0])
    noise_std = sig_std / np.power(10, (sigSNR / 20))
    noise = sig.mean() + np.random.randn(sig.shape[0]) * noise_std
    return noise

# 带通滤波
def bandpass(y: np.ndarray):
    # 设置带通滤波的上下界
    wn1 = 2 * (frequency - 1000) / sample_rate
    wn2 = 2 * (frequency + 1000) / sample_rate
    # 按时间间隔的每个滑动窗口进行滤波
    length = int(duration * sample_rate * channel)
    window_num = int(y.size / length)
    result = np.array([])
    for i in range(window_num):
        b, a = signal.butter(6, [wn1, wn2], 'bandpass')
        filtedData = signal.filtfilt(b, a, y[i * length : (i+1) * length])
        result = np.append(result, filtedData)
    return result

# 随机生成01字符串
def generate_msg(len):
    seed = "01"
    elem = []
    for i in range(len):
        elem.append(random.choice(seed))
    msg = ''.join(elem)
    return msg

# 绘制信号
def draw_sig(fileName):
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
    y = data[0]/1000
    print("=======绘制波形图=======")
    plt.figure()
    plt.plot(t,y,linewidth=1.0)
    plt.xlabel("time(sec)")
    plt.ylabel("volume")
    plt.title("wave figure")
    plt.grid()
    plt.show()

# 单独测试
def single_test():
    codes = input("please input sequence of 0/1: ")
    sigSNR = int(input("please input signal-noise-rate(dB): "))
    codes, flag = preProcess(codes)
    Modulator(codes, "qbsk.wav", sigSNR)
    seq = Demodulator("qbsk.wav", flag)
    print("demodulate sequence is: ", seq)

# 批量测试
# num: 测例数量
# ratio: 信噪比
# len: 每一个01序列的长度
def patch_test(num, ratio, len):
    print("================begin test================")
    print("signal_noise_ratio = ", ratio, "dB")
    correct = 0
    for i in range(num):
        codes = generate_msg(len)
        pre_codes, flag = preProcess(codes)
        Modulator(pre_codes, "qbsk.wav", ratio)
        seq = Demodulator("qbsk.wav", flag)
        print("seq input: ", codes , "  seq output: ",seq)
        if codes == seq:
            correct = correct + 1
    wrong = num - correct
    print("================test over================")
    print("testcase: ", num, "correct: ", correct, "wrong: ", wrong, "correct rate: ", float(correct/num))

if __name__ == "__main__":
    single_test()