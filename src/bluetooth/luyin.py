# -*- coding: utf-8 -*-
  
import pyaudio
import time
import threading
import wave
  
class Recorder():
  def __init__(self, chunk=2000, channels=1, rate=48000):
    self.CHUNK = chunk
    self.FORMAT = pyaudio.paInt16
    self.CHANNELS = channels
    self.RATE = rate
    self._running = True
    self._frames = []
  def start(self):
    threading._start_new_thread(self.__recording, ())
  def __recording(self):
    self._running = True
    self._frames = []
    p = pyaudio.PyAudio()
    stream = p.open(format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK)
    while(self._running):
      data = stream.read(self.CHUNK)
      self._frames.append(data)
  
    stream.stop_stream()
    stream.close()
    p.terminate()
  
  def stop(self):
    self._running = False
    filename = 'ceshi.wav'
    p = pyaudio.PyAudio()
    if not filename.endswith(".wav"):
      filename = filename + ".wav"
    wf = wave.open(filename, 'wb')
    wf.setnchannels(self.CHANNELS)
    wf.setsampwidth(p.get_sample_size(self.FORMAT))
    wf.setframerate(self.RATE)
    wf.writeframes(b''.join(self._frames))
    wf.close()
    print("Saved")
  