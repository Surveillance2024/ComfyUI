# Input：溫度, 情緒向量 < 4, 0, 0, 0, 1, 0, 0 >
import requests
import time
import random

def fetch_data():
    # Function to continuously fetch temperature data
    while True:
        url = "http://140.119.108.248:89/ComfyUI_Data/"
        response = requests.get(url)
        data = response.json()
        time.sleep(1)  # Fetch temperature every 1 second
        if data:
            temperature = data['temperature']
            emotions_vec = data['dominant_emotion']
            yield temperature, emotions_vec
            

def get_dominant_emotion(emotions_vec):
    # 找到最大值的索引
    max_index = emotions_vec.index(max(emotions_vec))

    # 用索引來查找對應的情緒
    emotions = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
    dominant_emotion = emotions[max_index]

    return dominant_emotion


# cloud_types_and_color
def choose_cloud_and_color(dominant_emotion):

    if(dominant_emotion == "angry"):
        cloud_type = "cumulus, "
        color = random.choice(["Red, ", "Dark red, "])

    elif(dominant_emotion == "disgust"):
        cloud_type = "stratus, "
        color = random.choice(["Grown, ", "Dark yellow, "])

    elif(dominant_emotion == "fear"):
        cloud_type = "cumulonimbus, "
        color = random.choice(["Red, ", "Black, "])

    elif(dominant_emotion == "happy"):
        cloud_type = random.choice(["cirrus, ", "cirrostratus, "])
        color = random.choice(["Yellow, ", "Bright green, "])

    elif(dominant_emotion == "sad"):
        cloud_type = random.choice(["altostratus, ", "nimbostratus, "])
        color = random.choice(["Gray, ", "Black, "])

    elif(dominant_emotion == "surprise"):
        cloud_type = random.choice(["cirroscumulus, ", "altocumulus, "])
        color = random.choice(["Yellow, ", "Bright Green, ", "Bright Pink, "])

    else:
        cloud_type = "stratocumulus"
        color = "No color, "

    return cloud_type, color

# cloud_types_and_color
def choose_cloud_and_color_chinese(dominant_emotion):

    if(dominant_emotion == "angry"):
        cloud_type = "積雲, "
        color = random.choice(["紅色, ", "暗紅色, "])

    elif(dominant_emotion == "disgust"):
        cloud_type = "層雲, "
        color = random.choice(["棕色, ", "深黃色, "])

    elif(dominant_emotion == "fear"):
        cloud_type = "積雨雲, "
        color = random.choice(["紅色, ", "黑色, "])

    elif(dominant_emotion == "happy"):
        cloud_type = random.choice(["捲雲, ", "卷積雲, "])
        color = random.choice(["深黃色, ", "亮綠色, "])

    elif(dominant_emotion == "sad"):
        cloud_type = random.choice(["高層雲, ", "雨層雲, "])
        color = random.choice(["灰色, ", "黑色, "])

    elif(dominant_emotion == "surprise"):
        cloud_type = random.choice(["卷積雲, ", "高積雲, "])
        color = random.choice(["黃色, ", "亮綠色, ", "亮粉色, "])

    else:
        cloud_type = "層積雲"
        color = "沒有顏色, "

    return cloud_type, color

# timing
season_list = ['spring ', 'summer ', 'fall ', 'winter ', 'unknown ']
timing_list = ['morning, ', 'evening, ','noon, ', 'night, ', 'unknown, ' ]

season_chinese = ['春天', '夏天', '秋天', '冬天', '季節皆可']
timing_chinese = ['早上, ', '傍晚, ', '中午, ', '晚上, ', '時間皆可, ']

def choose_date(temperature):
    season_num = 0
    timing_num = 0
    if 0 <= temperature < 10: 
        season_num = random.randint(0, 3)
        timing_num = 3
    elif 10 <= temperature < 20:
        season_num = random.randint(2, 3)
        timing_num = random.randint(0, 1)
    elif 20 <= temperature < 30:
        season_num = random.randint(0, 1)
        timing_num = random.randint(0, 1)
    elif 30 <= temperature <= 40:
        season_num = random.randint(0, 3)
        timing_num = 2
    else: 
        season_num = 4
        timing_num = 4

    return season_num, timing_num

def generate_prompt():

    for temperature, emotions_vec in fetch_data():
        # print(f"Temperature: {temperature}, Emotions: {emotions_vec}")
        temperature_str = str(temperature) #str
        dominant_emotion = get_dominant_emotion(emotions_vec)
        cloud_types, color = choose_cloud_and_color(dominant_emotion) # str
        season_num, timing_num = choose_date(temperature) 
        season = season_list[season_num] #str
        timing = timing_list[timing_num] #str

        prompt = "weather forecast, no people, only show the sky, fantasy style, " + temperature_str + " degrees Celsius, " + cloud_types + color + season + timing 

        print(prompt)

        # weather forecast, no people, only show the sky, fantasy style, 33 degrees Celsius, cirrus, Bright green, spring noon, 
        return prompt

def generate_chinese_prompt():

    for temperature, emotions_vec in fetch_data():
        # print(f"Temperature: {temperature}, Emotions: {emotions_vec}")
        temperature_str = str(temperature) #str
        dominant_emotion = get_dominant_emotion(emotions_vec)
        cloud_types, color = choose_cloud_and_color_chinese(dominant_emotion) # str
        season_num, timing_num = choose_date(temperature) 
        season = season_chinese[season_num] #str
        timing = timing_chinese[timing_num] #str

        prompt = "天氣預報, 沒有人物, 只顯示雲層, 奇幻風格, " + temperature_str + " 攝氏度, " + cloud_types + color + season + timing 

        print(prompt)

        # weather forecast, no people, only show the sky, fantasy style, 33 degrees Celsius, cirrus, Bright green, spring noon, 
        return prompt


# if __name__ == "__main__":
#     generate_prompt()
