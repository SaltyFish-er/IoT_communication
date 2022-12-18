import numpy as np
import wave
import struct

from scipy import signal


# 参数配置
sample_rate = 48000
duration = 0.025
volume = 1
sample_width = 2
channel = 1

def generate_chrip(f0, f1):
    t0 = np.linspace(0, 2 * duration * channel, 2 * int(duration * sample_rate * channel))
    sig = signal.chirp(t0, f0=f0, f1=f1, t1=2*duration, method='linear')
    return sig

def save_sig_as_wav(sig, file_name):
    # 保存信号波形为.wav文件
    wav_file = wave.open(file_name, 'wb')
    wav_file.setnchannels(channel)
    wav_file.setframerate(sample_rate)
    wav_file.setsampwidth(sample_width)
    for i in sig:
        # wave 只能以int形式保存帧，因此必须*1000以保证信息正常，在解调时重新配置就好了
        value = struct.pack('<h', int(i*1000))
        wav_file.writeframesraw(value)
    wav_file.close()

def get_sig_from_wav(fileName):
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