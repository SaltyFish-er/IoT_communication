import wave
import os
import sys
import time
import requests
import matplotlib.pyplot as plt

from threading import Thread
from pyaudio import *
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel
from PyQt5.QtGui import QIcon, QFont


from beepbeep import *
# 参数配置
sample_rate = 48000
duration = 0.025
volume = 1
sample_width = 2
channel = 1
chunk = 1024

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
        print("Welcome to Distance Client!")
        print("=========Start Measurement=========")
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
        # 生成chrip音频
        if not os.path.exists('./media/chrip.wav'):
            sig = generate_chrip(frequency_0, frequency_1)
            save_sig_as_wav(sig, 'media/chrip.wav')
        # 播放 chrip 信号
        self.play()
        time.sleep(1)
        # 设置录音停止
        self.pause_flag = True
        # 确定录音已经完成
        while self.record_flag is False:
            time.sleep(0.2)
        # 解析录音结果
        self.analysis() 
        # 发送时间差到 http_server
        print("=========Send Time Delta Client to Http Server=========")
        time_delta_client = (self.time_send - self.time_receive)/sample_rate
        url = 'http://43.143.205.209:8000/iot_set?msg='+str(time_delta_client)
        requests.get(url=url)
        # 更新控件状态
        self.start_btn.setEnabled(True)
        print("=========End Measurement=========")

    def record(self):
        print("=========Bgein Recoding=========")
        # 清除原录音
        my_path = './media/record.wav'
        if os.path.exists(my_path):
            os.remove(my_path)
        # 创建 record.wav
        wf = wave.open(my_path, 'wb')  # 创建一个音频文件
        wf.setnchannels(channel)  # 设置声道数
        wf.setsampwidth(sample_width)  # 设置采样宽度
        wf.setframerate(sample_rate)  # 设置采样率
        # 定义回调函数
        def callback(in_data, frame_count, time_info, status):
            wf.writeframes(in_data)
            return (in_data, paContinue) 

        # 创建PyAudio对象
        pa = PyAudio()
        # 打开声卡，设置采样深度、声道数、采样率、模式、采样点缓存
        stream = pa.open(format=paInt16, channels=channel, rate=sample_rate, 
                         input=True, frames_per_buffer=chunk, stream_callback=callback)
        # 读取采样数据
        stream.start_stream()
        while self.pause_flag is False:
            time.sleep(0.1)
        # 停止声卡
        stream.stop_stream()
        # 关闭声卡
        stream.close()
        # 关闭 wav
        wf.close()
        # 终止pyaudio
        pa.terminate()

        # 录音完成
        self.record_flag = True

        print("=========Finish Recording=========")

    def play(self):
        print("=========Begin Playing Chirp Signal=========")
        wf = wave.open('media/chrip.wav', 'rb')
        def callback(in_data, frame_count, time_info, status):
            data = wf.readframes(frame_count)
            return (data, paContinue)
        pa = PyAudio()
        stream = pa.open(format=get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True,
                        stream_callback=callback)
        stream.start_stream()
        while stream.is_active():
            time.sleep(0.2)
        stream.stop_stream()
        stream.close()
        wf.close()
        pa.terminate()
        print("=========End Playing=========")

    def analysis(self):
        print("=========Analysis Record File in Client=========")
        t, sig = get_sig_from_wav('./media/record.wav')
        # 前导码匹配
        preamble = generate_chrip(6500,7000)
        cross_corr = np.correlate(sig, preamble, 'valid')
        begin = 0
        end = begin
        end_loop_flag = False
        matched_list = []
        while end_loop_flag is False:
            print("Finding Heap...")
            for j, value in enumerate(cross_corr[begin:]):
                if value > 10000:
                    begin += j
                    break
                if j == len(cross_corr[begin:]) - 1:
                    end_loop_flag = True
            window_length = int(duration * 10 * sample_rate)
            end = begin + window_length
            #print("find one heap!")
            #print("begin, end: ", begin, end)
            match = max(cross_corr[begin:end])
            match_index = list(cross_corr).index(match)
            #print("matched!")
            #print("matched_index_value: ", match_index, match)
            if len(matched_list) < 2:
                dict1 = {}
                dict1['index'] = match_index
                dict1['value'] = match
                matched_list.append(dict1)
            else:
                if match > matched_list[0]['value'] or match > matched_list[1]['value']:
                    if matched_list[1]['value'] > matched_list[0]['value']:
                        matched_list[0]['value'] = match
                        matched_list[0]['index'] = match_index
                    else:
                        matched_list[1]['value'] = match
                        matched_list[1]['index'] = match_index
            begin = end
        # 计算时间差
        if len(matched_list) < 2:
            print("ERROR: cannot find two heap")
            return
        if matched_list[0]['index'] > matched_list[1]['index']:
                self.time_send = matched_list[0]['index']
                self.time_receive = matched_list[1]['index']
        else:
                self.time_send = matched_list[1]['index']
                self.time_receive = matched_list[0]['index']
        print("matched_list:", matched_list)
        print("time_send: ",  self.time_send)
        print("time_receive: ",  self.time_receive)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Server()
    sys.exit(app.exec_())