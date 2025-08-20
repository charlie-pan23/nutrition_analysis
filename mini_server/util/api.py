import io
import requests
import json

from mini_server.vo.user_daily_info import ComplexEncoder


def upload_json_file(info, user):


    upload_url = "https://api.dify.ai/v1/files/upload"
    headers = {
        "Authorization": "Bearer app-RPeZwxLBCbapZdwaNJTj6cOg",
    }
    file_like = io.BytesIO(json.dumps(info, cls=ComplexEncoder, indent=2).encode('utf-8'))
    print("Uploading JSON file...")
    files = {
        'file': ('file.json', file_like, 'application/json')
    }
    data = {
        "user": user,
        "type": "custom"
    }

    response = requests.post(upload_url, headers=headers, files=files, data=data)
    if response.status_code == 201:
        print("Upload successful.")
        return response.json().get("id")
    else:
        print(f"Upload failed: {response.status_code}, {response.text}")
        return None


def run_workflow_and_extract(file_id, user):
    print("file_id "+file_id)
    workflow_url = "https://api.dify.ai/v1/workflows/run"
    headers = {
        "Authorization": "Bearer app-RPeZwxLBCbapZdwaNJTj6cOg",
        "Content-Type": "application/json"
    }

    data = {
        "inputs": {
            "input": [{
                "transfer_method": "local_file",
                "upload_file_id": file_id,
                "type": "custom"
            }]
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
          

            outputs = result.get("data", {}).get("outputs", {})  # ✅ Fixed path
            doctor = outputs.get("doctor", "")
            food = outputs.get("meal", "")
            return doctor, food
        else:
            print(f"Workflow execution failed: {response.status_code}, {response.text}")
            return None, None
    except Exception as e:
        print(f"Workflow error: {str(e)}")
        return None, None

def test():
    file_path = {
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
        "current_time": "2025-08-20T14:43:04+08:00",
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
    # Replace with your actual file path
    user = "difyuser"

    file_id = upload_json_file(file_path, user)
    if file_id:
        doctor, food = run_workflow_and_extract(file_id, user)
        print("\n=== DOCTOR ===\n", doctor)
        print("\n=== FOOD ===\n", food)
        return doctor, food
    else:
        print("Upload failed. Cannot proceed to workflow.")
        return None, None

# === Run ===
if __name__ == "__main__":
    test()
