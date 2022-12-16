import random
import numpy as np
import wave
import struct
import matplotlib.pyplot as plt
import utils
import binascii

from scipy import signal
from playsound import playsound

# 蓝牙物理层数据包参数
PREAMBLE_SIZE = 1
ACCESS_ADDRESS_SIZE = 4
PDU_LENGTH_SIZE = 1
PDU_DATA_MAXSIZE = 4

# 参数配置
sample_rate = 48000
frequency_0 = 3000
frequency_1 = 5000
frequency_temp = 4000
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
    sig_0 = 0.65*np.sin(2 * np.pi * frequency_0 * t)
    sig_1 = np.sin(2 * np.pi * frequency_1 * t)
    sig_temp = 0*np.sin(2 * np.pi * frequency_1 * t)
    
    # 生成将要发射的信号
    sig = []

    # 生成前导码
    preamble = utils.get_preamble_sig(6000,6500)
    sig.append(preamble)
    sig = np.append(sig,sig_temp)
    sig = np.append(sig,sig_temp)
    sig = np.append(sig,sig_temp)
    # 生成其他包数据    
    for i in range(len(packet)):
        if packet[i] == '0':
          sig = np.append(sig, sig_0)
        else:
          sig = np.append(sig, sig_1)
        sig = np.append(sig,sig_temp)
        sig = np.append(sig,sig_temp)
        sig = np.append(sig,sig_temp)#空了三个静音拍

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
    playsound(fileName)

# BFSK解调
# packet: 蓝牙数据包
# 返回: 解码后的字符串
def Demodulator(packet):
  if len(packet) < 6:
    print('ERROR: packet size too small, ignoring')
    return None
  
  pdu_length = int(packet[6], 2)
  data_size = int(pdu_length / 8)
  
  if pdu_length == 0:
    return ''

  result = ''
  for i in range(7, 7 + data_size):
    ascii_code = int(packet[i], 2)
    character = chr(ascii_code)
    result += character
  
  return result

# BFSK调制前导码
def Modu_Preamble():
  # 生成0信号和1信号
  t = np.linspace(0, duration * channel, int(duration * sample_rate * channel))
  sig_0 = np.sin(2 * np.pi * frequency_0 * t)
  sig_1 = np.sin(2 * np.pi * frequency_1 * t)

  # preamble
  preamble = "01010101"
  # 生成将要发射的信号
  sig = []
  for i in range(len(preamble)):
      if preamble[i] == '0':
        sig = np.append(sig, sig_0)
      else:
        sig = np.append(sig, sig_1)

  return sig