#This is an example that uses the websockets api and the SaveImageWebsocket node to get images directly without
#them being saved to disk

import websocket #NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import json
import urllib.request
import urllib.parse
import numpy as np
from numpy.typing import NDArray
import random
import cv2
from concurrent.futures import ThreadPoolExecutor, wait
import sys
import os
import asyncio
from datetime import datetime
from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
import base64
from text_animate.lib import TextAnimate, EmotionDistribution
from text_animate.char.radical import string2radical

# 使用絕對匯入
# 將 Cloud_Image 設定為根目錄
script_dir = os.path.dirname(os.path.abspath(__file__))
cloud_image_dir = os.path.abspath(os.path.join(script_dir, '..', '..'))  # 獲取 Cloud_Image 資料夾的路徑
sys.path.append(cloud_image_dir)  # 添加 Cloud_Image 到 sys.path

from ECCV2022_RIFE.InterpolatorInterface import InterpolatorInterface

# from generate_prompt import generate_prompt, generate_chinese_prompt
from temperature import overlay_images, draw_only_number
# from temperature import draw_thermometer, overlay_images
from prompt_class import PromptGenerator

# 設定儲存路徑
output_dir = '../final_image'

temperature = 0
emotions_list : dict = {}

server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())

def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    current_node = ""
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['prompt_id'] == prompt_id:
                    if data['node'] is None:
                        break #Execution is done
                    else:
                        current_node = data['node']
        else:
            if current_node == 'save_image_websocket_node':
                images_output = output_images.get(current_node, [])
                images_output.append(out[8:])
                output_images[current_node] = images_output

    return output_images

# 讀取最新兩張圖片
def get_latest_images(directory, count=2):
    # 獲取資料夾中的所有文件，排除隱藏文件
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and not f.startswith('.')]
    
    if not files:
        return []  # 如果沒有圖片，返回空列表
    
    # 按照最後修改時間對文件排序
    files.sort(key=lambda f: os.path.getmtime(os.path.join(directory, f)), reverse=True)
    
    # 取得最新的兩張圖片的檔案名稱
    latest_images = files[:count]
    
    return latest_images  # 返回最新圖片的檔案名稱列表

def validate_image(path):
    try:
        from PIL import Image
        img = Image.open(path)
        img.verify()  # 檢查影像完整性
        return True
    except Exception as e:
        print(f"Image validation failed for {path}: {e}")
        return False


# 假設這是處理 ComfyUI 的函數
def process_comfyui():
    with open("workflow_api.json") as workflow_api:
        prompt = json.load(workflow_api)
    print("workflow_api open")

    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    print("ws.connect")

    interpolator = InterpolatorInterface() # Initialize image to video
    prompt_generator = PromptGenerator()

    # ComfyUI 製圖
    prompt_text = prompt_generator.generate_prompt(temperature, emotions_list, chinese=False)
    print(prompt_text)
    prompt["3"]["inputs"]["seed"] = random.randint(0,999999999999999)
    prompt["6"]["inputs"]["text"] = prompt_text        
    queue_prompt(prompt)['prompt_id']  # 將提示加入隊列（假設這個函數已經實現）
    print(prompt_text)

    # 設定 output 資料夾的路徑
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output'))
    # 讀取最新的兩張圖片檔案名稱
    latest_images = get_latest_images(output_dir)
    # print(latest_images[0])
    # 拼接字串
    image_path0 = "/Cloud_Image/ComfyUI/output/" + latest_images[0]
    image_path1 = "/Cloud_Image/ComfyUI/output/" + latest_images[1]

    # 當 latest_images 不是預期的情況時，指定預設圖片
    if len(latest_images) < 2:
        print("Latest images not found or not enough images. Using default images.")
        image_path0 = "/Cloud_Image/ComfyUI/output/ComfyUI_00003_.png"  # 預設圖片 1
        image_path1 = "/Cloud_Image/ComfyUI/output/ComfyUI_00004_.png"  # 預設圖片 2
    else:
        image_path0 = os.path.join(output_dir, latest_images[0])
        image_path1 = os.path.join(output_dir, latest_images[1])
    # 檢查指定的圖片是否存在
    if not os.path.exists(image_path0) or not os.path.exists(image_path1):
        raise FileNotFoundError(f"Image path(s) not found: {image_path0}, {image_path1}")

    # 確保圖片有效，並傳遞給 interpolator
    if validate_image(image_path0) and validate_image(image_path1):
        results = interpolator.generate(
            imgs=(image_path0, image_path1),
            exp=4
        )
    else:
        raise ValueError("Invalid images provided to interpolator.generate")

    # 如果有圖片，顯示或處理
    if latest_images:
        # image to video
        results = interpolator.generate(
            imgs=(image_path0, image_path1),
            exp=5,
            # output_dir="interpolate_out"
            # output_dir=os.path.join(comfyui_dir, "interpolate_out") 
        )

        return results

    print("process_comfyUI完成")

def process_radical():
    prompt_generator = PromptGenerator()
    prompt_chinese = prompt_generator.generate_prompt(temperature, emotions_list, chinese=True)
    radicals = string2radical(prompt_chinese)

    print("process_radical完成")
    return radicals


# def draw_temperature(frame):
#     global temperature
#     thermometer = draw_thermometer(temperature)
#     origin = frame.copy()
#     scale_factor = 1 / 3
#     new_height = int(origin.shape[0] * scale_factor)
#     new_width = int((new_height / thermometer.shape[0]) * thermometer.shape[1])
#     thermometer = cv2.resize(thermometer, (new_width, new_height))

#     x_offset = origin.shape[1] - thermometer.shape[1] - 10
#     y_offset = 10
#     combined_frame = overlay_images(origin, thermometer, x_offset, y_offset, alpha=0.7)

#     return combined_frame
def draw_temperature(frame):
    global temperature
    temp_overlay = draw_only_number(temperature)
    
    # Resize the overlay
    scale_factor = 0.8
    new_height = int(temp_overlay.shape[0] * scale_factor)
    new_width = int(temp_overlay.shape[1] * scale_factor)
    
    if new_width == 0 or new_height == 0:
        raise ValueError("Invalid dimensions after resizing.")
    
    temp_overlay = cv2.resize(temp_overlay, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    # Calculate position (top right corner)
    x_offset = frame.shape[1] - temp_overlay.shape[1] - 10
    y_offset = 10
    
    # Convert frame to float32 for calculations
    frame = frame.astype(np.float32)
    
    # Add temperature overlay
    frame = overlay_images(frame, temp_overlay, x_offset, y_offset, alpha=0.7)
    
    # Convert back to uint8
    frame = np.clip(frame, 0, 255).astype(np.uint8)
    
    return frame

def emotions_mapping(lists):
    emotions = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
    mapping = dict(zip(emotions, lists))
    return mapping

#############################################
# New version of ComfyUI image generation AP
app = FastAPI()

@app.post("/process-data/")
async def get_data(data: dict):
    global temperature, emotions_list
    """
    接收 Server1 的溫度和情緒數據，回傳處理結果。
    """
    try:
        temperature = data.get("temperature", 0)
        emotions_list = data.get("emotions_vec", [])
        print(f"Received Temperature: {temperature}")
        print(f"Received Emotions List: {emotions_list}")

        # 處理圖片並獲取9張 Base64 編碼的圖片
        images_base64_list = main()

        # 將圖片列表以 JSON 格式回傳
        return JSONResponse(content={"images": images_base64_list})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

#############################################


def main():
    global latest_full_frame, emotions_list
    ta = TextAnimate()
    output_images = []  # 用來存放產生的圖片

    try:
        # 使用 ThreadPoolExecutor 處理圖片生成
        with ThreadPoolExecutor(max_workers=4) as general_executor:
            future_radicals = general_executor.submit(process_radical)
            future_comfyui = general_executor.submit(process_comfyui)

            radicals = future_radicals.result()
            bgs = future_comfyui.result()

            EmotionDis = emotions_mapping(emotions_list)

            for i in range(17):  # 假設你需要處理9張圖片
                temp_frame = draw_temperature(bgs[i])
                if len(temp_frame.shape) == 2:
                    temp_frame = np.repeat(temp_frame[..., None], 4, axis=-1)
                    temp_frame[..., 3] = 255
                elif len(temp_frame.shape) == 3 and temp_frame.shape[2] == 3:
                    temp_frame = np.concatenate(
                        (temp_frame, np.full((*temp_frame.shape[:2], 1), 255, dtype=np.uint8)),
                        axis=-1,
                    )

                img = ta.draw(temp_frame, EmotionDistribution(**EmotionDis), radicals)
                img = cv2.cvtColor(img.result(), cv2.COLOR_BGRA2BGR)
                print(type(img))
                print(img.shape if hasattr(img, "shape") else "Invalid image format")


                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                filename = f"{timestamp}.png"
                output_path = os.path.join(output_dir, filename)

                # cv2.imwrite(output_path, img)
                success = cv2.imwrite(output_path, img)
                if not success:
                    raise IOError(f"Failed to write image to {output_path}")

                with open(output_path, "rb") as image_file:
                    image_data = image_file.read()
                    image_base64 = base64.b64encode(image_data).decode("utf-8")
                    output_images.append(image_base64)

        return output_images

    except Exception as e:
        print(f"Error in main: {str(e)}")
        raise




if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
