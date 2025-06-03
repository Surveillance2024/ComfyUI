import random

class PromptGenerator:
    def __init__(self):
        self.emotions = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
        self.colors = {
            "angry": ["Red", "Dark red"],
            "disgust": ["Brown", "Dark yellow"],
            "fear": ["Red", "Black"],
            "happy": ["Yellow", "Bright green"],
            "sad": ["Gray", "Black"],
            "surprise": ["Yellow", "Bright green", "Bright pink"],
            "neutral": ["No color"]
        }
        self.seasons = ['spring', 'summer', 'fall', 'winter', 'unknown']
        self.timings = ['morning', 'evening', 'noon', 'night', 'unknown']

    def get_top_emotions(self, emotions_vec):
        emotion_percentages = [(self.emotions[i], emotions_vec[i]) for i in range(len(emotions_vec))]
        sorted_emotions = sorted(emotion_percentages, key=lambda x: x[1], reverse=True)
        return sorted_emotions[:3]

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
        top_emotions = self.get_top_emotions(emotions_vec)
        season_num, timing_num = self.choose_date(temperature)

        # Format the emotions and percentages for the prompt
        emotion_descriptions = ", ".join(
            [f"{int(percentage * 100)}% {emotion}" for emotion, percentage in top_emotions]
        )

        # Extract top three emotions for colors and season
        color1 = f"{int(top_emotions[0][1] * 100)}% {top_emotions[0][0]}"
        color2 = f"{int(top_emotions[1][1] * 100)}% {top_emotions[1][0]}"
        color3 = f"{int(top_emotions[2][1] * 100)}% {top_emotions[2][0]}"
        season = self.seasons[season_num]
        timing = self.timings[timing_num]

        if chinese:
            chinese_seasons = ['春天', '夏天', '秋天', '冬天', '季節皆可']
            chinese_timings = ['早上', '傍晚', '中午', '晚上', '時間皆可']
            chinese_emotions = ['生氣', '厭惡', '害怕', '快樂', '悲傷', '驚訝', '中性']

            # Translate emotions to Chinese
            chinese_top_emotions = [
                (chinese_emotions[self.emotions.index(emotion)], percentage)
                for emotion, percentage in top_emotions
            ]
            chinese_emotion_descriptions = ", ".join(
                [f"{int(percentage * 100)}% {emotion}" for emotion, percentage in chinese_top_emotions]
            )

            chinese_color1 = f"{int(chinese_top_emotions[0][1] * 100)} {chinese_top_emotions[0][0]}"
            chinese_color2 = f"{int(chinese_top_emotions[1][1] * 100)} {chinese_top_emotions[1][0]}"
            chinese_color3 = f"{int(chinese_top_emotions[2][1] * 100)} {chinese_top_emotions[2][0]}"
            chinese_season = chinese_seasons[season_num]
            chinese_timing = chinese_timings[timing_num]

            prompt = (
                f"生成一個魔法風格和神秘風格的場景, {temperature} 攝氏度, "
                f"情緒包含 {chinese_emotion_descriptions}, 背景為一個想像世界, "
                f"{chinese_color1} {chinese_color2} {chinese_color3} {chinese_season}, {chinese_timing}"
            )
            print(prompt)
        else:
            prompt = (
                f"generate a magical style and mysterious style, {temperature} degrees Celsius, "
                f"scene of mood contains {emotion_descriptions}, in the background of an imagination world, "
                f"combing {color1} and {color2} and {color3} colors, {season}, {timing}"
            )
        
        return prompt
