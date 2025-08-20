# backend/services/audio_service.py

import queue
import sys

import numpy as np
import wavio
import sounddevice as sd
import os
import time

class AudioService:
    def __init__(self):
        self.recording = False
        self.frames = []
        self.start_time = 0
        self._stream = None
        self._recording_data = []
        self._q = queue.Queue()
        self.MIC_DEVICE_ID = None  # 动态查找设备ID
        self.SAMPLE_RATE = 44100  # 根据你麦克风支持的采样率设置
        self.CHANNELS = 1

    def start_recording(self):
        """开始从麦克风录制音频"""
        if self.recording:
            return False

        if self._stream is not None and self._stream.active:
            print("录音已在进行中，请先调用 stop_recording_and_save() 停止当前录音。")
            return False

        print("正在初始化麦克风并开始录音...")

        # 动态查找麦克风设备ID
        if self.MIC_DEVICE_ID is None:
            devices = sd.query_devices()
            found_mic_id = None
            for i, dev in enumerate(devices):
                if 'USB Audio' in dev['name'] and dev['max_input_channels'] > 0:
                    found_mic_id = i
                    print(f"找到USB麦克风：{dev['name']}, ID: {found_mic_id}")
                    break
                elif 'USB' in dev['name'] and dev['max_input_channels'] > 0:
                    if found_mic_id is None:
                        found_mic_id = i
                        print(f"找到备用USB麦克风：{dev['name']}, ID: {found_mic_id}")

            if found_mic_id is None:
                print("错误：未找到USB麦克风。请检查连接和驱动。")
                return False

            self.MIC_DEVICE_ID = found_mic_id
            print(f"将使用设备ID: {self.MIC_DEVICE_ID} 进行录音。")

        try:
            # 清空之前的录音数据
            self._recording_data = []
            # 清空队列
            while not self._q.empty():
                self._q.get_nowait()

            # 启动音频输入流
            self._stream = sd.InputStream(
                samplerate=self.SAMPLE_RATE,
                channels=self.CHANNELS,
                dtype='int16',
                callback=self._audio_callback,
                device=self.MIC_DEVICE_ID
            )
            self._stream.start()
            self.recording = True
            self.start_time = time.time()
            print("录音已开始。")
            return True
        except Exception as e:
            print(f"开始录音时发生未知错误: {e}")
            self._stream = None
            return False

    def _audio_callback(self, indata, frames, time_info, status):
        """sounddevice 的回调函数，当有音频数据时被调用"""
        if status:
            print(f"音频回调状态警告: {status}", file=sys.stderr)
        self._q.put(indata.copy())

    def stop_recording_and_save(self, filename="recordings/recording.wav"):
        """停止录音并保存录制好的音频到本地WAV文件"""
        if not self.recording or self._stream is None or not self._stream.active:
            return False

        print("正在停止录音并保存文件...")
        try:
            # 停止音频流
            self._stream.stop()
            self._stream.close()
            print("录音流已停止。")

            # 从队列中取出所有缓存的音频数据
            while not self._q.empty():
                self._recording_data.append(self._q.get())

            # 将所有音频数据拼接起来
            if self._recording_data:
                combined_audio = np.concatenate(self._recording_data, axis=0)

                # 确保目录存在
                output_dir = os.path.dirname(filename)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                # 使用 wavio 保存为 WAV 文件
                wavio.write(filename, combined_audio, self.SAMPLE_RATE, sampwidth=2)
                print(f"录音已保存到: {os.path.abspath(filename)}")
                return filename
            else:
                print("没有录制到任何音频数据。")
                return None
        except Exception as e:
            print(f"停止录音或保存文件时发生错误: {e}")
            return None
        finally:
            self._stream = None
            self._recording_data = []
            self.recording = False
            self.start_time = 0

    def get_recording_duration(self):
        """获取当前录音时长（秒）"""
        if self.start_time > 0 and self.recording:
            return time.time() - self.start_time
        return 0


# import wave
# import pyaudio
# import time
#
# class AudioService:
#     def __init__(self):
#         self.recording = False
#         self.audio = pyaudio.PyAudio()
#         self.stream = None
#         self.frames = []
#         self.start_time = 0
#
#     def start_recording(self):
#         if self.recording:
#             return False
#
#         self.frames = []
#         self.recording = True
#         self.start_time = time.time()
#
#         self.stream = self.audio.open(
#             format=pyaudio.paInt16,
#             channels=1,
#             rate=16000,
#             input=True,
#             frames_per_buffer=1024
#         )
#         return True
#
#     def stop_recording_and_save(self, filename):
#         if not self.recording:
#             return False
#
#         self.recording = False
#         self.stream.stop_stream()
#         self.stream.close()
#
#         wf = wave.open(filename, 'wb')
#         wf.setnchannels(1)
#         wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
#         wf.setframerate(16000)
#         wf.writeframes(b''.join(self.frames))
#         wf.close()
#         return True
#
#     def get_recording_duration(self):
#         if self.start_time > 0:
#             return time.time() - self.start_time
#         return 0
