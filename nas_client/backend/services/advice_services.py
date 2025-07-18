# backend/services/audio_service.py
import requests
import pyttsx4
from flask import current_app

class AudioService:
    def __init__(self):
        # 初始化朗读引擎
        self.engine = pyttsx4.init()
        self.engine.setProperty('rate', 250)
        self.engine.setProperty('voice', self.engine.getProperty('voices')[0].id)

        self.API_KEY = "app-cl9P96oW9cqIlzEuzshctcaC"  # 替换为你的 Dify API Key
        self.USER_ID = "example-user"

    def speak(self, text):
        print(f"\n正在朗读：{text}\n")
        self.engine.say(text)
        self.engine.runAndWait()

    def upload_file(self, file_path, file_type, mime_type):
        url = "https://api.dify.ai/v1/files/upload"
        headers = {
            "Authorization": f"Bearer {self.API_KEY}",
        }

        with open(file_path, 'rb') as f:
            files = {'file': (file_path, f, mime_type)}
            data = {"user": self.USER_ID, "type": file_type}

            print(f"Uploading {file_path} ...")
            res = requests.post(url, headers=headers, files=files, data=data)
            if res.status_code == 201:
                file_id = res.json().get("id")
                print(f"Uploaded {file_path}, file_id = {file_id}")
                return file_id
            else:
                print(f"Upload failed for {file_path}: {res.status_code} - {res.text}")
                return None

    def run_workflow(self, sound_file_id, weight_file_id):
        url = "https://api.dify.ai/v1/workflows/run"
        headers = {
            "Authorization": f"Bearer {self.API_KEY}",
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
            "response_mode": "blocking",
            "user": self.USER_ID
        }

        print("Running workflow...")
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code == 200:
            print("Workflow run successful.")
            return res.json()
        else:
            print(f"Workflow run failed: {res.status_code} - {res.text}")
            return None
