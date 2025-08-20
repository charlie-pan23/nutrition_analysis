# local_audio_backend.py

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
import subprocess

from flask import Flask, jsonify, request
from flask_cors import CORS  # 导入 CORS，处理跨域请求

# --- Flask 应用初始化 ---
app = Flask(__name__)
# 启用 CORS：允许前端（例如 Vue 应用）从不同端口访问此后端
# 【树莓派部署时修改点】：生产环境请配置允许的源，例如：
# CORS(app, resources={r"/api/*": {"origins": "http://<您的前端IP地址或域名>"}})
CORS(app)

# --- 全局变量和配置 (录音部分) ---
MIC_DEVICE_ID = 2  # 初始设置为 None，将在 start_recording 时查找
# 【树莓派部署时修改点】：部署到树莓派时，如果USB麦克风ID不同，需要在这里修改
SAMPLE_RATE = 44100  # 采样率
CHANNELS = 1  # 单声道

_q = queue.Queue()  # 录音数据缓冲区
_stream = None  # sounddevice 音频流对象
_recording_data = []  # 存储录音数据的列表
_is_recording_flag = False  # 标记录音状态的布尔值

# 定义录音文件保存路径 (相对于本脚本的目录)
RECORDING_DIR = "./"
os.makedirs(RECORDING_DIR, exist_ok=True)  # 确保目录存在

# 【树莓派部署时修改点】：定义 weight.txt 文件的路径
# 这个文件可能由其他服务生成，或者是一个固定的模板文件。
# 请确保在树莓派上部署时，这个路径是正确的。

# --- Dify API 配置 ---
# 【树莓派部署时修改点】：请替换为您的 Dify API Key 和 User ID


# 初始化朗读引擎
# 【重要：请注意这里的缩进，所有这些行都应该从最左边开始，没有空格！】
engine = pyttsx4.init()
engine.setProperty('rate', 150)  # 建议将语速调低一点，对树莓派资源更友好

try:
    voices = engine.getProperty('voices')
    chinese_voice_id = None
    # 遍历所有声音，查找中文声音
    for voice in voices:
        # 根据 test_tts.py 的输出，中文声音的 languages 包含 b'\x05zh'
        # 或者其 name 包含 'Mandarin'
        if b'\x05zh' in voice.languages or 'mandarin' in voice.name.lower():
            chinese_voice_id = voice.id
            print(f"找到中文语音：{voice.name}, ID: {chinese_voice_id}")
            break

    if chinese_voice_id:
        engine.setProperty('voice', chinese_voice_id)
        print(f"已成功设置中文语音：{chinese_voice_id}")
    elif voices:
        # 如果没有找到明确的中文声音，但有其他声音，就用第一个默认声音
        engine.setProperty('voice', voices[0].id)
        print("警告: 未找到中文语音，使用默认声音。朗读中文可能效果不佳。")
    else:
        print("警告: 未找到任何语音引擎声音，朗读功能将受限或不可用。")
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


import requests
import json

# 定义 API 密钥
DIFY_API_KEY = "app-4CGlFRz50uL1E0zAcvz0GHKy"


# 上传 WAV 文件
def upload_wav_file(file_path, user):
    upload_url = "https://api.dify.ai/v1/files/upload"
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
    }

    try:
        print("Uploading WAV file...")
        with open(file_path, 'rb') as file:
            files = {
                'file': (file_path, file, 'audio/wav')  # 确保 MIME 类型为 'audio/wav'
            }
            data = {
                "user": user,
                "type": "audio"
            }

            response = requests.post(upload_url, headers=headers, files=files, data=data)
            print("Response Status Code:", response.status_code)
            print("Response Text:", response.text)

            if response.status_code == 201:
                print("WAV file upload successful.")
                return response.json().get("id")  # 返回文件 ID
            else:
                print(f"WAV file upload failed: {response.status_code}, {response.text}")
                return None
    except Exception as e:
        print(f"WAV file upload error: {str(e)}")
        return None


# 上传 JSON 文件
def upload_json_file(file_path, user):
    upload_url = "https://api.dify.ai/v1/files/upload"
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
    }

    try:
        print("Uploading JSON file...")
        with open(file_path, 'rb') as file:
            files = {
                'file': (file_path, file, 'application/json')
            }
            data = {
                "user": user,
                "type": "custom"
            }

            response = requests.post(upload_url, headers=headers, files=files, data=data)
            print("Response Status Code:", response.status_code)
            print("Response Text:", response.text)

            if response.status_code == 201:
                print("Upload successful.")
                return response.json().get("id")  # 返回文件 ID
            else:
                print(f"Upload failed: {response.status_code}, {response.text}")
                return None
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return None


# 执行工作流并提取输出
def run_workflow_and_extract(file_id, file_id2, user):
    workflow_url = "https://api.dify.ai/v1/workflows/run"
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "inputs": {
            "input": [{
                "transfer_method": "local_file",
                "upload_file_id": file_id,
                "type": "custom"
            }],
            "voice": {
                "transfer_method": "local_file",  # 上传方式
                "upload_file_id": file_id2,  # 文件 ID
                "type": "audio"  # 文件类型为音频
            }
        },
        "response_mode": "blocking",
        "user": user
    }

    try:
        print("Running workflow...")
        response = requests.post(workflow_url, headers=headers, json=data)
        if response.status_code == 200:
            print("Workflow executed successfully.")
            result = response.json()
            outputs = result.get("data", {}).get("outputs", {})  # 获取输出部分
            # 提取 URL
            output_url = outputs.get("output1", [{}])[0].get("url", "")
            if output_url:
                print("File URL:", output_url)
                download_file(output_url)  # 下载文件
            else:
                print("No valid output URL found.")
            return outputs
        else:
            print(f"Workflow execution failed: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Workflow error: {str(e)}")
        return None


# 下载文件
def download_file(file_url):
    try:
        response = requests.get(file_url, stream=True)
        response.raise_for_status()
        file_path = "output_audio.wav"  # 保存文件名
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"File saved to: {file_path}")
        return file_path
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        return None


# === Run ===

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
            workflow_output = process_audio_workflow_internal(saved_path)
            print(f"Workflow 输出: {workflow_output}")
            # 【树莓派部署时修改点】：如果前端需要实时结果，后端需要通过 WebSocket 或其他方式通知前端。
            # 目前这里只是简单打印到后端日志。
        else:
            print(f"停止录音失败: {save_message}")

    threading.Thread(target=run_stop_and_workflow_in_background).start()

    return jsonify({"status": "success", "message": "录音停止中，并在后台处理..."}), 200


# 主流程函数，供 Flask 路由调用
def process_audio_workflow_internal(sound_path):
    """
    封装录音后的文件处理和Dify工作流执行。
    :param sound_path: 录音文件的本地路径。
    :param weight_path: 重量文件的本地路径。
    :return: Workflow 的输出文本，或错误信息。
    """
    user = "difyuser"

    json_file_path = "personal_info.json"  # 替换为你实际的 JSON 文件路径

    # 保存个人信息字典到 JSON 文件
    personal_info = {
        "personal_info": {
            "height_cm": 175,
            "weight_kg": 68,
            "age": 30,
            "gender": "male",
            "preferences": ["low-carb", "high-protein"],
            "allergies": ["peanuts", "shellfish"],
            "chronic_conditions": ["hypertension"],
            "activity_level": "moderate"
        },
        "food_item": {
            "name": "tomato",
            "weight_g": 150,
            "energy_kcal": 27,
            "carbohydrates_g": 5.85,
            "fat_g": 0.3,
            "protein_g": 1.35
        },
        "current_time": "2025-07-14T14:43:04+08:00",
        "meal_type": "lunch",
        "daily_goals": {
            "energy_kcal": 2200,
            "carbohydrates_g": 250,
            "fat_g": 70,
            "protein_g": 150
        },
        "daily_intake": {
            "energy_kcal": 980,
            "carbohydrates_g": 105,
            "fat_g": 32,
            "protein_g": 65
        }
    }

    # 将个人信息字典保存到 JSON 文件
    with open(json_file_path, 'w') as json_file:
        json.dump(personal_info, json_file)

    # 上传文件
    file_id = upload_json_file(json_file_path, user)
    print(file_id)

    filename = os.path.basename(sound_path)
    #recordings下文件问题！！！！！！如何正确引入路径
    file_id2 = upload_wav_file(filename, user)
    print("======================================")
    print(filename)
    if file_id and file_id2:
        # 运行工作流并提取结果
        outputs = run_workflow_and_extract(file_id, file_id2, user)
    def convert_wav_with_ffmpeg(input_path, output_path):
        try:
            # 使用 ffmpeg 强制转换文件，并加上 -y 参数来自动覆盖已存在的文件
            command = ['ffmpeg', '-y', '-i', input_path, '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2',
                       output_path]
            subprocess.run(command, check=True)
            print(f"File converted and saved as {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error converting file with ffmpeg: {e}")
            return None




    # 文件路径
    input_wav_path = "output_audio.wav" # 原始文件路径
    output_wav_path = "converted_output.wav"  # 转换后的文件路径

    # 检查文件是否存在
    if os.path.exists(input_wav_path):
        # 使用 ffmpeg 转换文件
        convert_wav_with_ffmpeg(input_wav_path, output_wav_path)

        # 检查文件是否成功转换
        if os.path.exists(output_wav_path):
            print(f"Found {output_wav_path}, playing the file...")

            # 初始化 pygame 音频系统
            import pygame

            pygame.mixer.init()

            # 加载并播放 WAV 文件
            pygame.mixer.music.load(output_wav_path)
            pygame.mixer.music.play()

            # 等待音频播放完成
            # 等待音频播放完成
            while pygame.mixer.music.get_busy():  # 如果音频仍在播放
                pygame.time.Clock().tick(10)  # 每 10 毫秒检查一次
        else:
            print(f"{output_wav_path} not found after conversion.")
    else:
        print(f"{input_wav_path} not found in the current directory.")


if __name__ == "__main__":
    # 在本地开发时，Flask 默认运行在 5001 端口
    app.run(debug=True, port=5001)


        # 如果有医生建议和食物推荐结果，输出它们


    # 强制转换 WAV 文件为 PCM 格式



