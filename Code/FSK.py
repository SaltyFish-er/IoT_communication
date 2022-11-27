import random
import numpy as np
import wave
import struct
import matplotlib.pyplot as plt
from scipy import signal
from playsound import playsound

# 蓝牙物理层数据包参数
PREAMBLE_SIZE = 1
ACCESS_ADDRESS_SIZE = 4
PDU_LENGTH_SIZE = 1
PDU_DATA_MAXSIZE = 37
CRC_SIZE = 3

# 参数配置
sample_rate = 48000
frequency_0 = 18000
frequency_1 = 21000
duration = 0.025
volume = 1

sample_width = 2
channel = 1



# BFSK调制函数
# codes: 待调制的数据，0/1数组
# fileName:保存wav到的文件
# sigSNR: 信噪比
def Modulator(codes, fileName):
    # 生成I信号和Q信号
    t = np.linspace(0, duration * channel, int(duration * sample_rate * channel))
    sig_0 = np.sin(2 * np.pi * frequency_0 * t)
    sig_1 = np.sin(2 * np.pi * frequency_1 * t)

    # 生成将要发射的信号
    sig = []
    for i in range(len(codes)):
        if codes[i] == '0':
          sig = np.append(sig, sig_0)
        else:
          sig = np.append(sig, sig_1)

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

    # 将声音文件播放出来
    playsound('test.wav')
