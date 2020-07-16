from age_and_gender import *
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random

letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'

# https://python-scripts.com/predict-age-and-gender
data = AgeAndGender()
data.load_shape_predictor('handlers/models/shape_predictor_5_face_landmarks.dat')
data.load_dnn_gender_classifier('handlers/models/dnn_gender_classifier_v1.dat')
data.load_dnn_age_predictor('handlers/models/dnn_age_predictor_v1.dat')


def get_random_string(length=10):
    return ''.join(random.choice(letters) for _ in range(length))


def get_new_photo(photo):
    img = Image.open(BytesIO(photo)).convert("RGB")
    result = data.predict(img)

    font = ImageFont.truetype("handlers/Lemon.ttf", 20)

    for info in result:
        shape = [(info['face'][0], info['face'][1]), (info['face'][2], info['face'][3])]
        draw = ImageDraw.Draw(img)

        if info['gender']['value'].title() == 'Male':
            gender = 'Мужчина'
        else:
            gender = 'Женщина'
        gender_percent = int(info['gender']['confidence'])
        age = info['age']['value']
        if age % 10 in (0, 5, 6, 7, 8, 9):
            age_name = 'лет'
        elif age % 10 == 1:
            age_name = 'год'
        else:
            age_name = 'года'

        age_percent = int(info['age']['confidence'])

        draw.text(
            (info['face'][0] - 10, info['face'][3] + 10),
            f"{gender} (~{gender_percent}%)\n{age} {age_name}. (~{age_percent}%).",
            fill='white', font=font, align='center'
        )

        draw.rectangle(shape, outline="red", width=5)

    imgByteArr = BytesIO()
    img.save(imgByteArr, format='JPEG')
    return imgByteArr.getvalue()


def get_age(photo):
    img = Image.open(BytesIO(photo)).convert("RGB")
    result = data.predict(img)
    ans = ""

    for i, info in enumerate(result):
        gender = 'Мужчина' if info['gender']['value'].title() == 'Male' else 'Женщина'
        gender_percent = int(info['gender']['confidence'])
        age = info['age']['value']
        age_name = name_of_age(age)
        age_percent = int(info['age']['confidence'])

        ans += f"{i + 1}) {gender} (~{gender_percent}%)\n     {age} {age_name}. (~{age_percent}%)\n"

    if ans != "":
        return ans
    return "Мы не смогли распознать Ваше лицо :( Пожалуйста, поробуйте еще раз"


def name_of_age(age):
    if age % 10 in (0, 5, 6, 7, 8, 9):
        return 'лет'
    elif age % 10 == 1:
        return 'год'
    else:
        return 'года'
