# app_audio.py

import sounddevice as sd
import numpy as np
import wavio
import queue
import sys
import os
import time
import requests
import pyttsx4
import threading  # 用于在后台线程中运行耗时操作，避免阻塞前端请求

from flask import Flask, jsonify, request
from flask_cors import CORS  # 导入 CORS，处理跨域请求

# --- Flask 应用初始化 ---
app = Flask(__name__)
# 启用 CORS：允许前端（例如 Vue 应用）从不同端口访问此后端
# 【树莓派部署时修改点】：生产环境请配置允许的源，例如：
# CORS(app, resources={r"/api/*": {"origins": "http://<您的前端IP地址或域名>"}})
CORS(app)

# --- 全局变量和配置 (录音部分) ---
MIC_DEVICE_ID = 1  # 初始设置为 None，将在 start_recording 时查找
# 【树莓派部署时修改点】：部署到树莓派时，如果USB麦克风ID不同，需要在这里修改
SAMPLE_RATE = 44100  # 采样率
CHANNELS = 1  # 单声道

_q = queue.Queue()  # 录音数据缓冲区
_stream = None  # sounddevice 音频流对象
_recording_data = []  # 存储录音数据的列表
_is_recording_flag = False  # 标记录音状态的布尔值

# 定义录音文件保存路径 (相对于本脚本的目录)
RECORDING_DIR = "recordings"
os.makedirs(RECORDING_DIR, exist_ok=True)  # 确保目录存在

# 【树莓派部署时修改点】：定义 weight.txt 文件的路径
#               这个文件可能由其他服务生成，或者是一个固定的模板文件。
#               请确保在树莓派上部署时，这个路径是正确的。
WEIGHT_FILE_PATH = os.path.join("data", "weight.txt")  # 假设 weight.txt 放在 data 文件夹下

# --- Dify API 配置 ---
# 【树莓派部署时修改点】：请替换为您的 Dify API Key 和 User ID
DIFY_API_KEY = "app-cl9P96oW9cqIlzEuzshctcaC"  # <-- 请替换为您的真实 KEY
DIFY_USER_ID = "example-user"  # <-- 请替换为您的真实 USER ID

# 初始化朗读引擎
# 注意：pyttsx4 依赖系统上的 TTS 引擎 (如 Windows 的 SAPI5, Linux 的 espeak)
engine = pyttsx4.init()
engine.setProperty('rate', 250)  # 设置语速，可调节
# 尝试设置第一个可用的声音，如果系统没有声音，这行可能报错，可以注释掉
try:
    voices = engine.getProperty('voices')
    if voices:
        engine.setProperty('voice', voices[0].id)
    else:
        print("警告: 未找到语音引擎声音，朗读功能可能受限。")
except Exception as e:
    print(f"初始化语音引擎声音失败: {e}", file=sys.stderr)


# --- 音频回调函数 ---
def _audio_callback(indata, frames, time_info, status):
    """sounddevice 的回调函数，当有音频数据时被调用"""
    if status:
        print(f"音频回调状态警告: {status}", file=sys.stderr)
    _q.put(indata.copy())  # 将捕获到的音频数据放入队列


# --- 核心录音函数 ---
def start_recording_internal():
    """
    开始从麦克风录制音频。
    该函数会初始化麦克风并启动一个后台线程进行录音。
    """
    global _stream, MIC_DEVICE_ID, _recording_data, _is_recording_flag

    if _stream is not None and _stream.active:
        print("录音已在进行中，请先调用 stop_recording_and_save() 停止当前录音。", file=sys.stderr)
        return False, "录音已在进行中"

    print("正在初始化麦克风并开始录音...")

    # 动态查找麦克风设备ID
    if MIC_DEVICE_ID is None:
        devices = sd.query_devices()
        found_mic_id = None
        for i, dev in enumerate(devices):
            # 优先匹配包含 'USB Audio' 的设备
            if 'USB Audio' in dev['name'] and dev['max_input_channels'] > 0:
                found_mic_id = i
                print(f"找到USB麦克风：{dev['name']}, ID: {found_mic_id}")
                break
            # 备用匹配：包含 'USB' 且有输入通道的设备
            elif 'USB' in dev['name'] and dev['max_input_channels'] > 0:
                if found_mic_id is None:  # 如果还没找到更精确的，就用这个
                    found_mic_id = i
                    print(f"找到备用USB麦克风：{dev['name']}, ID: {found_mic_id}")

        if found_mic_id is None:
            print("错误：未找到USB麦克风。请检查连接和驱动。", file=sys.stderr)
            print("请运行 'python -m sounddevice' 查看所有设备及ID，手动设置 MIC_DEVICE_ID。", file=sys.stderr)
            return False, "未找到USB麦克风"

        MIC_DEVICE_ID = found_mic_id
        print(f"将使用设备ID: {MIC_DEVICE_ID} 进行录音。")

    try:
        _recording_data = []  # 清空之前的录音数据
        while not _q.empty():  # 清空队列
            _q.get_nowait()

        _stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS,
                                 dtype='int16', callback=_audio_callback,
                                 device=MIC_DEVICE_ID)
        _stream.start()
        _is_recording_flag = True
        print("录音已开始。")
        return True, "录音已开始"
    except sd.PortAudioError as e:
        print(f"错误：无法启动录音流。请检查麦克风连接和配置。错误信息: {e}", file=sys.stderr)
        _stream = None  # 确保流对象无效
        _is_recording_flag = False
        return False, f"无法启动录音流: {e}"
    except Exception as e:
        print(f"开始录音时发生未知错误: {e}", file=sys.stderr)
        _stream = None
        _is_recording_flag = False
        return False, f"未知错误: {e}"


def stop_recording_and_save_internal(output_filename="recording.wav"):
    """
    停止录音并保存录制好的音频到本地WAV文件。
    :param output_filename: 保存的WAV文件名。
    :return: 成功保存的文件路径，或 None 如果失败。
    """
    global _stream, _recording_data, _is_recording_flag

    if _stream is None or not _stream.active:
        print("没有正在进行的录音可以停止。", file=sys.stderr)
        return None, "没有正在进行的录音"

    print("正在停止录音并保存文件...")
    try:
        _stream.stop()
        _stream.close()
        print("录音流已停止。")

        while not _q.empty():
            _recording_data.append(_q.get())

        if _recording_data:
            combined_audio = np.concatenate(_recording_data, axis=0)

            output_dir = os.path.dirname(output_filename)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # wavio 需要浮点数，但这里 dtype='int16'，直接保存即可
            wavio.write(output_filename, combined_audio, SAMPLE_RATE, sampwidth=2)
            print(f"录音已保存到: {output_filename}")
            return os.path.abspath(output_filename), "录音已保存"
        else:
            print("没有录制到任何音频数据。", file=sys.stderr)
            return None, "没有录制到任何音频数据"
    except Exception as e:
        print(f"停止录音或保存文件时发生错误: {e}", file=sys.stderr)
        return None, f"保存文件失败: {e}"
    finally:
        _stream = None  # 重置流对象
        _recording_data = []  # 清空录音数据
        _is_recording_flag = False  # 确保录音状态标志被重置


def speak(text):
    """使用 pyttsx4 朗读文本"""
    try:
        print(f"\n🗣️ 正在朗读：{text}\n")
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"朗读失败: {e}", file=sys.stderr)


def upload_file(file_path, file_type, mime_type):
    """上传文件到 Dify 平台。"""
    url = "https://api.dify.ai/v1/files/upload"
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
    }

    try:
        with open(file_path, 'rb') as f:
            files = {
                'file': (os.path.basename(file_path), f, mime_type)
            }
            data = {
                "user": DIFY_USER_ID,
                "type": file_type
            }

            print(f"Uploading {file_path} ...")
            res = requests.post(url, headers=headers, files=files, data=data)
            res.raise_for_status()  # 检查HTTP错误
            if res.status_code == 201:
                file_id = res.json().get("id")
                print(f"Uploaded {file_path}, file_id = {file_id}")
                return file_id
            else:
                print(f"Upload failed for {file_path}: {res.status_code} - {res.text}")
                return None
    except requests.exceptions.RequestException as e:
        print(f"网络或API请求错误: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"上传文件时发生未知错误: {e}", file=sys.stderr)
        return None


def run_workflow(sound_file_id, weight_file_id):
    """在 Dify 平台运行指定的工作流。"""
    url = f"https://api.dify.ai/v1/workflows/run"
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": {
            "sound": {
                "transfer_method": "local_file",
                "upload_file_id": sound_file_id,
                "type": "audio"
            },
            "weight": {
                "transfer_method": "local_file",
                "upload_file_id": weight_file_id,
                "type": "document"
            }
        },
        "response_mode": "blocking",  # 阻塞模式，等待结果
        "user": DIFY_USER_ID
    }

    print("Running workflow...")
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)  # 设置超时
        res.raise_for_status()  # 检查HTTP错误
        print("Workflow run successful.")
        return res.json()
    except requests.exceptions.RequestException as e:
        print(f"Workflow run failed: 网络或API请求错误: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Workflow run failed: 未知错误: {e}", file=sys.stderr)
        return None


# --- Flask 路由 ---

@app.route('/api/audio/start_recording', methods=['POST'])
def start_recording_api():
    success, message = start_recording_internal()  # 调用内部录音函数
    if success:
        return jsonify({"status": "success", "message": message}), 200
    else:
        return jsonify({"status": "error", "message": message}), 500


@app.route('/api/audio/stop_recording', methods=['POST'])
def stop_recording_api():
    if not _is_recording_flag:  # 检查录音状态
        return jsonify({"status": "error", "message": "没有正在进行的录音"}), 400

    # 生成唯一的录音文件名
    timestamp = int(time.time())
    output_filename = os.path.join(RECORDING_DIR, f"recording_{timestamp}.wav")

    # 在单独的线程中执行停止录音和工作流，避免阻塞前端请求
    def run_stop_and_workflow_in_background():
        saved_path, save_message = stop_recording_and_save_internal(output_filename)
        if saved_path:
            print(f"录音文件已保存到: {saved_path}")
            # 执行 Dify 工作流
            workflow_output = process_audio_workflow_internal(saved_path, WEIGHT_FILE_PATH)
            print(f"Workflow 输出: {workflow_output}")
            # 【树莓派部署时修改点】：如果前端需要实时结果，后端需要通过 WebSocket 或其他方式通知前端。
            #               目前这里只是简单打印到后端日志。
        else:
            print(f"停止录音失败: {save_message}")

    threading.Thread(target=run_stop_and_workflow_in_background).start()

    return jsonify({"status": "success", "message": "录音停止中，并在后台处理..."}), 200


# 主流程函数，供 Flask 路由调用
def process_audio_workflow_internal(sound_path, weight_path):
    """
    封装录音后的文件处理和Dify工作流执行。
    :param sound_path: 录音文件的本地路径。
    :param weight_path: 重量文件的本地路径。
    :return: Workflow 的输出文本，或错误信息。
    """
    sound_id = upload_file(sound_path, "AUDIO", "audio/wav")
    # 【树莓派部署时修改点】：weight_path 的来源和 file_type/mime_type 需要根据实际情况调整
    #               如果 weight.txt 是一个动态生成的文件，需要确保它在调用时存在
    weight_id = upload_file(weight_path, "TXT", "text/plain")  # 假设是TXT类型

    if sound_id and weight_id:
        result = run_workflow(sound_id, weight_id)
        if result and "data" in result:
            outputs = result['data'].get('outputs', {})
            # 默认查找字段 output，如果不存在尝试其他常见字段
            output_text = outputs.get("output") or outputs.get("voice_text") or outputs.get("text")

            if output_text:
                print("识别结果：", output_text)
                speak(output_text)  # 朗读结果
                return output_text
            else:
                print("未找到有效输出字段")
                return "Workflow 未找到有效输出"
        else:
            print("Workflow 无有效输出")
            return "Workflow 运行失败或无有效输出"
    else:
        print("文件上传失败，无法运行 workflow")
        return "文件上传失败"


if __name__ == "__main__":
    # 在本地开发时，Flask 默认运行在 5000 端口
    app.run(debug=True, port=5001)
