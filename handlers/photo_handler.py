from aiogram import types
from misc import dp, bot, TOKEN
from requests import get
from .detect import get_age, get_new_photo, name_of_age
from json import loads
from random import randint
import re
import asyncio
from os import listdir

players_array = dict()
all_files = dict()

age_dataset = open('dataset/age_set.txt').readlines()


@dp.message_handler(content_types=['photo'])
async def handle_photo(msg: types.Message):
    file_id = msg.photo[-1]['file_id']
    response = loads(get(f'https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}').text)

    if response['ok']:
        photo = get(f'https://api.telegram.org/file/bot{TOKEN}/{response["result"]["file_path"]}').content
        print(f'https://api.telegram.org/file/bot{TOKEN}/{response["result"]["file_path"]}')
        await bot.send_photo(msg.from_user.id, get_new_photo(photo), caption=get_age(photo))
    else:
        await send_photo(msg.from_user.id, 'dataset/witcher.png',
                         "Хмм, зараза... Что-то не так, возможно фотка слишком тяжелая")


@dp.message_handler(commands=['game'])
async def start_game(msg: types.Message):
    new_img_id = randint(1, 17)
    players_array[msg.from_user.id] = {'playing': True, 'prev_img': new_img_id}
    await msg.reply("Ну давайте немного поиграем:")
    await send_photo(msg.from_user.id, f'dataset/{new_img_id}.jpg', "Сколько лет Вы дадите этому человеку?")


@dp.message_handler(commands=['stop'])
async def stop(msg: types.Message):
    if msg.from_user.id in players_array:
        players_array[msg.from_user.id]['playing'] = False
        await msg.reply("Игра окончена")


@dp.message_handler(commands=['send_all'])
async def send_all(msg: types.Message):
    await msg.reply(r"Сам попросил ¯\_(ツ)_/¯")
    for file in sorted(listdir('dataset')):
        if file.endswith('jpg'):
            await send_photo(msg.from_user.id, f'dataset/{file}')

    print(len(all_files))


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
        await send_photo(msg.from_user.id, f"dataset/{prev_img_id}_process.jpg",
                         "А вот, что об этом думает наша нейросеть", 2)
        await send_photo(msg.from_user.id, f'dataset/{new_img_id}.jpg', "А сколько лет Вы дадите этому человеку?", 4)
    else:
        await bot.send_message(msg.from_user.id, "Извините, я Вас не понимаю\nПросто напомню, что есть команда /help")


def get_age_by_id(photo_id):
    return int(re.findall(r'\d{1,4}', age_dataset[photo_id - 1])[0])


async def send_photo(to, filename, caption="", sleep_time=0):
    await bot.send_chat_action(to, 'upload_photo')
    await asyncio.sleep(sleep_time)

    if filename in all_files:
        file_tusent = all_files[filename]
    else:
        file_tusent = open(filename, 'rb').read()

    sended_photo = await bot.send_photo(to, file_tusent, caption=caption)

    if filename not in all_files:
        all_files[filename] = sended_photo.photo[0].file_id
