import random

class PromptGenerator:
    def __init__(self):
        self.emotions = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
        self.cloud_types_and_colors = {
            "angry": (["cumulus"], ["Red", "Dark red"]),
            "disgust": (["stratus"], ["Brown", "Dark yellow"]),
            "fear": (["cumulonimbus"], ["Red", "Black"]),
            "happy": (["cirrus", "cirrostratus"], ["Yellow", "Bright green"]),
            "sad": (["altostratus", "nimbostratus"], ["Gray", "Black"]),
            "surprise": (["cirroscumulus", "altocumulus"], ["Yellow", "Bright green", "Bright pink"]),
            "neutral": (["stratocumulus"], ["No color"])
        }
        self.cloud_types_and_colors_chinese = {
            "angry": (["積雲"], ["紅色", "暗紅色"]),
            "disgust": (["層雲"], ["棕色", "深黃色"]),
            "fear": (["積雨雲"], ["紅色", "黑色"]),
            "happy": (["捲雲", "卷積雲"], ["深黃色", "亮綠色"]),
            "sad": (["高層雲", "雨層雲"], ["灰色", "黑色"]),
            "surprise": (["卷積雲", "高積雲"], ["黃色", "亮綠色", "亮粉色"]),
            "neutral": (["層積雲"], ["沒有顏色"])
        }
        self.seasons = ['spring', 'summer', 'fall', 'winter', 'unknown']
        self.timings = ['morning', 'evening', 'noon', 'night', 'unknown']
        self.seasons_chinese = ['春天', '夏天', '秋天', '冬天', '季節皆可']
        self.timings_chinese = ['早上', '傍晚', '中午', '晚上', '時間皆可']

    def get_dominant_emotion(self, emotions_vec):
        max_index = emotions_vec.index(max(emotions_vec))
        return self.emotions[max_index]

    def choose_cloud_and_color(self, dominant_emotion, chinese=False):
        if chinese:
            cloud_types, colors = self.cloud_types_and_colors_chinese[dominant_emotion]
        else:
            cloud_types, colors = self.cloud_types_and_colors[dominant_emotion]

        return random.choice(cloud_types), random.choice(colors)

    def choose_date(self, temperature):
        if 0 <= temperature < 10:
            return random.randint(0, 3), 3
        elif 10 <= temperature < 20:
            return random.randint(2, 3), random.randint(0, 1)
        elif 20 <= temperature < 30:
            return random.randint(0, 1), random.randint(0, 1)
        elif 30 <= temperature <= 40:
            return random.randint(0, 3), 2
        else:
            return 4, 4

    def generate_prompt(self, temperature, emotions_vec, chinese=False):
        dominant_emotion = self.get_dominant_emotion(emotions_vec)
        cloud_type, color = self.choose_cloud_and_color(dominant_emotion, chinese)
        season_num, timing_num = self.choose_date(temperature)

        if chinese:
            season = self.seasons_chinese[season_num]
            timing = self.timings_chinese[timing_num]
            prompt = (
                f"天氣預報, 沒有人物, 只顯示雲層, {temperature} 攝氏度, "
                f"{cloud_type}, {color}, {season}, {timing}"
            )
        else:
            season = self.seasons[season_num]
            timing = self.timings[timing_num]
            prompt = (
                f"weather forecast, no people, only show the sky, "
                f"{temperature} degrees Celsius, {cloud_type}, {color}, {season} {timing}"
            )
        return prompt
