import wave
import os
import sys
import time
import requests

from threading import Thread
from pyaudio import PyAudio, paInt16
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel
from PyQt5.QtGui import QIcon, QFont
from playsound import playsound

from beepbeep import *
# 参数配置
sample_rate = 48000
duration = 0.025
volume = 1
sample_width = 2
channel = 1

frequency_0 = 6500
frequency_1 = 7000

class Server(QWidget):

    def __init__(self):
        super().__init__()
        # 定义时间戳
        self.time_send = 0
        self.time_record = 0
        self.time_receive = 0
        # 录音停止标志
        self.pause_flag = False
        # 录音完成标志
        self.record_flag = False
        # 初始化UI
        self.initUI()


    def initUI(self):

        self.setGeometry(600, 300, 600, 400)
        self.setWindowTitle('Measure(client)')
        self.setWindowIcon(QIcon('icon/icon.jpg'))  
        # 服务端提示
        self.type_lbl = QLabel(self)
        font = QFont()
        font.setFamily('Arial')
        font.setPointSize(22)
        self.type_lbl.setFont(font)
        self.type_lbl.move(10,10)
        self.type_lbl.setText('client')      
        # 开始控件
        self.start_btn = QPushButton('开始测距', self)
        self.start_btn.resize(self.start_btn.sizeHint())
        self.start_btn.move(150,250)
        self.start_btn.clicked.connect(self.start_measure)
        # 结束控件
        self.end_btn = QPushButton('完成测距', self)
        self.end_btn.resize(self.end_btn.sizeHint())
        self.end_btn.move(350,250)
        self.end_btn.setEnabled(False)
        self.end_btn.clicked.connect(self.end_measure)

        self.show()

    def start_measure(self):
        # 更新控件状态
        self.start_btn.setEnabled(False)
        self.end_btn.setEnabled(True)
        # 开始录音
        self.pause_flag = False
        self.record_flag = False
        t_record = Thread(target=self.record)
        t_record.start()

    def end_measure(self):
        self.start_btn.setEnabled(False)
        self.end_btn.setEnabled(False)
        
        # 设置录音停止
        self.pause_flag = True
        # 确定录音已经完成
        while self.record_flag is False:
            pass
        # 解析录音结果
        self.analysis() 
        # 生成chrip音频并读取到data
        if not os.path.exists('./media/chrip.wav'):
            sig = generate_chrip(frequency_0, frequency_1)
            save_sig_as_wav(sig, 'media/chrip.wav')
        # 发送chrip信号并记录时间
        self.time_send = time.time()
        playsound('./media/chrip.wav')
        # 发送时间差到 http_server
        time_delta_client = self.time_send - self.time_receive
        url = 'http://43.143.205.209:8000/iot_set?msg='+str(time_delta_client)
        requests.get(url=url)
        # 更新控件状态
        self.start_btn.setEnabled(True)

    def record(self):
        if os.path.exists('./media/record.wav'):
            os.remove('./media/record.wav')
        # 创建PyAudio对象
        pa = PyAudio()
        # 打开声卡，设置采样深度、声道数、采样率、模式、采样点缓存
        stream = pa.open(format=paInt16, channels=channel, rate=sample_rate, 
                         input=True, frames_per_buffer=1024)
        # 记录开始录音的时间
        self.time_record = time.time()
        # 存储采样数据
        record_buf = []
        while self.pause_flag is False:
            audio_data = stream.read(1024)  # 读出声卡缓冲区的音频数据
            record_buf.append(audio_data)  # 将读出的音频数据追加到record_buf列表
        # 停止声卡
        stream.stop_stream()
        # 关闭声卡
        stream.close()
        # 终止pyaudio
        pa.terminate()
        
        # 存储文件为wav
        my_path = './media/record.wav'
        wf = wave.open(my_path, 'wb')  # 创建一个音频文件
        wf.setnchannels(channel)  # 设置声道数
        wf.setsampwidth(sample_width)  # 设置采样宽度
        wf.setframerate(sample_rate)  # 设置采样率
        # 将数据写入创建的音频文件
        wf.writeframes("".encode().join(record_buf))
        # 写完后将文件关闭
        wf.close()

        # 录音完成
        self.record_flag = True

    def analysis(self):
        t, sig = get_sig_from_wav('./media/record.wav')
        # 前导码匹配
        preamble = generate_chrip(6500,7000)
        cross_corr = np.correlate(sig, preamble, 'valid')
        begin = 0
        for i, value in enumerate(cross_corr):
            if value > 1000:
                begin = i
                break
        match = max(cross_corr[begin:])
        match_index = list(cross_corr).index(match)
        # 计算时间差
        self.time_receive = self.time_record + match_index/sample_rate
        print('end analysis')

        

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Server()
    sys.exit(app.exec_())