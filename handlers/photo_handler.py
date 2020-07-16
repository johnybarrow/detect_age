from aiogram import types
from misc import dp, bot, TOKEN
from requests import get
from .detect import get_age, get_new_photo, name_of_age
from json import loads
from random import randint
import re

players_array = dict()

age_dataset = open('dataset/age_set.txt').readlines()


@dp.message_handler(content_types=['photo'])
async def handle_photo(message: types.Message):
    file_id = message.photo[-1]['file_id']
    response = loads(get(f'https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}').text)

    if response['ok']:
        photo = get(f'https://api.telegram.org/file/bot{TOKEN}/{response["result"]["file_path"]}').content
        print(f'https://api.telegram.org/file/bot{TOKEN}/{response["result"]["file_path"]}')
        await bot.send_photo(message.from_user.id, get_new_photo(photo), reply_to_message_id=message.message_id,
                             caption=get_age(photo))
    else:
        await bot.send_photo(message.from_user.id, open('dataset/witcher.png'), reply_to_message_id=message.message_id,
                             caption="Хмм, зараза... Что-то не так, возможно фотка слишком тяжелая")


@dp.message_handler(commands=['game'])
async def start_game(msg: types.Message):
    new_img_id = randint(1, 17)
    players_array[msg.from_user.id] = {'playing': True, 'prev_img': new_img_id}
    await msg.reply("Ну давайте немного поиграем:")
    await bot.send_photo(msg.from_user.id, open(f'dataset/{new_img_id}.jpg', 'rb').read(),
                         caption="Сколько лет Вы дадите этому человеку?")


@dp.message_handler(commands=['stop'])
async def stop(message: types.Message):
    players_array[message.from_user.id]['playing'] = False
    await message.reply("Игра окончена")


@dp.message_handler(commands=['start'])
async def process_help_command(msg: types.Message):
    await msg.reply(f"Привет, {msg.from_user.first_name}! С моей помощью ты узнаешь на сколько лет ты выглядишь!\n"
                    f"Меня создали с помощью я/п Python и нейронной сети, я являюсь проектом для конкурса \"Большая "
                    f"перемена\"")


@dp.message_handler(commands=['help'])
async def process_help_command(msg: types.Message):
    await msg.reply("/game - Начать игру\n/stop - Окончить игру")


@dp.message_handler()
async def number_end(msg: types.Message):
    if msg.text.strip().isdigit() and msg.from_user.id in players_array and players_array[msg.from_user.id]['playing']:
        age = int(msg.text.strip())
        real_age = get_age_by_id(players_array[msg.from_user.id]['prev_img'])
        prev_img_id = players_array[msg.from_user.id]['prev_img']

        new_img_id = randint(1, 17)
        players_array[msg.from_user.id]['prev_img'] = new_img_id

        shablon = f"Вы думали, что ему/ей {age} {name_of_age(age)}, а на самом деле {real_age} {name_of_age(real_age)}"

        if real_age == age:
            ans = f"В яблочко! Этому человеку {age} {name_of_age(age)}"
        elif abs(real_age - age) < 8:
            ans = "Вы почти правы! " + shablon
        elif abs(real_age - age) < 15:
            ans = "Далековато! " + shablon
        else:
            ans = "Совсем далеко! " + shablon

        await bot.send_message(msg.from_user.id, ans)
        await bot.send_photo(msg.from_user.id,
                             open(f"dataset/{prev_img_id}_process.jpg", 'rb').read(),
                             caption="А вот, что об этом думаешь наша нейросеть")
        await bot.send_photo(msg.from_user.id, open(f'dataset/{new_img_id}.jpg', 'rb').read(),
                             caption="А сколько лет Вы дадите этому человеку?")
    else:
        await bot.send_message(msg.from_user.id, "Извините, я Вас не понимаю\nПросто напомню, что есть команда /help")


def get_age_by_id(photo_id):
    return int(re.findall(r'\d{1,4}', age_dataset[photo_id - 1])[0])
