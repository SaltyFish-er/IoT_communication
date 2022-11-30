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
# packet: 待调制的蓝牙数据包，0/1字符串
# fileName:保存wav到的文件
def Modulator(packet, fileName):
    # 生成0信号和1信号
    t = np.linspace(0, duration * channel, int(duration * sample_rate * channel))
    sig_0 = np.sin(2 * np.pi * frequency_0 * t)
    sig_1 = np.sin(2 * np.pi * frequency_1 * t)

    # 生成将要发射的信号
    sig = []
    for i in range(len(packet)):
        if packet[i] == '0':
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
    print('world')
    playsound('test.wav')

# BFSK解调
# 返回 packetList: 蓝牙数据包列表
def Demodulator(packetList):
  pass

# BFSK调制前导码
def Modu_Preamble(preamble):
  # 生成0信号和1信号
  t = np.linspace(0, duration * channel, int(duration * sample_rate * channel))
  sig_0 = np.sin(2 * np.pi * frequency_0 * t)
  sig_1 = np.sin(2 * np.pi * frequency_1 * t)

  # 生成将要发射的信号
  sig = []
  for i in range(len(preamble)):
      if preamble[i] == '0':
        sig = np.append(sig, sig_0)
      else:
        sig = np.append(sig, sig_1)

  return sig