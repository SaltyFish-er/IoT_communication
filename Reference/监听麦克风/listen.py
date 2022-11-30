import pyaudio
import wave
import numpy as np
from matplotlib import pyplot as plt
import scipy.fft
import scipy.stats as stats
import random

sample_rate = 64000
frequency_0 = 18000
frequency_1 = 21000
duration = 0.05
volume = 1

sample_width = 2
channel = 1



def Monitor():
    t = np.linspace(0, duration * channel, int(duration * sample_rate * channel))
    sig_1 = np.sin(2 * np.pi * frequency_1 * t)
    CHUNK = 2000
    sig_1 = sig_1[:CHUNK]
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 64000
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    last = np.zeros(128)
    base = last[:]

    print("Recording noise...")

    # 取噪声频谱
    for _ in range(100):
        frame = []
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.fromstring(data, dtype=np.short)
        frame += audio_data.tolist()
        spec = np.log10(0.00001+np.abs(scipy.fft.fft(frame)[:CHUNK//2]))
        spec = np.abs(spec)
        spec = np.average(np.array([spec[::2], spec[1::2]]), axis=0)
        spec = np.abs(spec)
        spec=spec[:128]
        LAM = 0.1
        spec = last * (1-LAM) + spec * LAM
        if random.randint(0,1)==0:
            plt.cla()
            plt.ylim((0, 8))
            plt.plot(np.arange(len(spec))*32, spec)
            plt.pause(0.001)
        base = spec
        last = spec[:]

    print("OK")

    while (True):
        frame = []
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.fromstring(data, dtype=np.short)
        frame = audio_data.tolist()
        spec = np.log10(0.00001+np.abs(scipy.fft.fft(frame)[:CHUNK//2]))
        
        spec = np.abs(spec)
        #spec = np.average(np.array([spec[::2], spec[1::2]]), axis=0)
        spec = np.abs(spec)
        spec=spec[:128] 
        LAM = 0.5
        spec = last * (1-LAM) + spec * LAM
        if random.randint(0,1)==0:
            plt.cla() #删除画图板上的图像
            plt.ylim((0, 8)) #设置y轴的范围
            plt.plot(np.arange(len(spec))*32, spec)
            plt.pause(0.001)
            #print('hello')
            #print(stats.pearsonr(sig_1, audio_data))
        last = spec

    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


if __name__ == '__main__':
    Monitor()