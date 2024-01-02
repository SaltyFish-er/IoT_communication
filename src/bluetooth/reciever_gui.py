# -*- coding: utf-8 -*-
import utils
import FSK
from time import sleep
import tkinter as tk
import luyin as ly
import utils
import numpy as np
import wave
import matplotlib.pyplot as plt
from scipy import signal


# 第1步，建立窗口window
window = tk.Tk()  # 建立窗口window

rec = ly.Recorder() 

 
# 第2步，给窗口起名称
window.title('声波蓝牙接收端')  # 窗口名称
 
# 第3步，设定窗口的大小(长＊宽)
window.geometry("240x240")  # 窗口大小(长＊宽)
 
# 第4步，在图形化界面上设定一个文本框
textExample = tk.Text(window, height=10)  # 创建文本输入框
 
# 第5步，安置文本框
textExample.pack()  # 把Text放在window上面，显示Text这个控件
 

# 第7步，在图形化界面上设定一个button按钮（#command绑定获取文本框内容的方法）
start_recieve = tk.Button(window, height=1, width=10, text="开始接收", command=lambda:rec.start())  # command绑定获取文本框内容的方法
 
# 第8步，安置按钮
start_recieve.pack()  # 显示按钮


stop_recieve = tk.Button(window, height=1, width=10, text="停止接收", command=lambda:rec.stop())  # command绑定获取文本框内容的方法
 
# 第8步，安置按钮
stop_recieve.pack()  # 显示按钮

def analyze_message():
    t, sig = utils.get_signal_from_wav("ceshi.wav")
    sig1 = [0]*48000
    # 添加一段空白
    t1 = np.linspace(0,1,48001)
    t = t + 1
    t = np.append(t1[:-1], t)
    sig = np.append(sig1,sig)    
    #plt.plot(t, sig)
    #plt.show()

    # 前导码匹配
    preamble = utils.get_preamble_sig(6000,6500)
    cross_corr = np.correlate(sig, preamble, 'valid')

    #plt.plot(cross_corr)
    #plt.show()

    #match_pos = np.argmax(cross_corr)
    #print(match_pos) #开始匹配上的位置

    #extract_message(sig, match_pos+4800)

    index = 0
    match_list = []
    while index < len(cross_corr):
        if cross_corr[index] > 100000:
            temp = cross_corr[index:index+36000]
            match_pos = np.argmax(temp)
            match_pos = match_pos + index
            print(match_pos) #开始匹配上的位置
            match_list.append(match_pos)
            index = index + 3600
        else:
            index = index+1
    
    for match_pos in match_list:
        m = utils.extract_message(sig, match_pos+4800)
        if m == 0:
            print('抱歉，发生丢包')
        else:
            textExample.insert ("end", m )

start_analyze = tk.Button(window, height=1, width=10, text="开始分析", command=lambda:analyze_message())  # command绑定获取文本框内容的方法
 
# 第8步，安置按钮
start_analyze.pack()  # 显示按钮

def saveTXT():
    result = textExample.get("1.0", "end")  # 获取文本输入框的内容
    with open('test.txt','w',encoding='utf-8') as f:
        f.write(result)

save_txt = tk.Button(window, height=1, width=10, text="保存文本", command=lambda:saveTXT())  # command绑定获取文本框内容的方法
 
# 第8步，安置按钮
save_txt.pack()  # 显示按钮

# 第9步，
window.mainloop()