from .age_and_gender import *
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random

# https://python-scripts.com/predict-age-and-gender
data = AgeAndGender()
data.load_shape_predictor('handlers/models/shape_predictor_5_face_landmarks.dat')
data.load_dnn_gender_classifier('handlers/models/dnn_gender_classifier_v1.dat')
data.load_dnn_age_predictor('handlers/models/dnn_age_predictor_v1.dat')

FONT_BORDER = 1


def get_new_photo(photo):
    img = Image.open(BytesIO(photo)).convert("RGB")
    result = data.predict(img)

    font = ImageFont.truetype("handlers/Lemon.ttf", 26)
    ans = ""

    for i, info in enumerate(result):
        shape = [(info['face'][0], info['face'][1]), (info['face'][2], info['face'][3])]
        draw = ImageDraw.Draw(img)

        gender = 'Мужчина' if info['gender']['value'].title() == 'Male' else 'Женщина'
        gender_percent = int(info['gender']['confidence'])
        age = info['age']['value']
        age_name = name_of_age(age)
        age_percent = int(info['age']['confidence'])
        ans += f"{i + 1}) {gender} (~{gender_percent}%)\n     {age} {age_name}. (~{age_percent}%)\n"

        text_to_write = f"{gender} (~{gender_percent}%)\n{age} {age_name}. (~{age_percent}%)."
        x, y = info['face'][0] - 10, info['face'][3] + 10

        draw.text((x + FONT_BORDER, y + FONT_BORDER), text_to_write, fill='black', font=font, align='center')
        draw.text((x + FONT_BORDER, y - FONT_BORDER), text_to_write, fill='black', font=font, align='center')
        draw.text((x - FONT_BORDER, y + FONT_BORDER), text_to_write, fill='black', font=font, align='center')
        draw.text((x - FONT_BORDER, y - FONT_BORDER), text_to_write, fill='black', font=font, align='center')
        draw.text((x, y), text_to_write, fill='white', font=font, align='center')

        draw.rectangle(shape, outline="red", width=5)

    imgByteArr = BytesIO()
    img.save(imgByteArr, format='JPEG')
    return imgByteArr.getvalue(), ans or "Мы не смогли распознать Ваше лицо :( Пожалуйста, поробуйте еще раз"


def name_of_age(age):
    if age % 10 in (0, 5, 6, 7, 8, 9) or age in range(11, 21):
        return 'лет'
    elif age % 10 == 1:
        return 'год'
    else:
        return 'года'
