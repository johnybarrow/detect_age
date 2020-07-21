from aiogram import types
from misc import dp, bot, TOKEN
from requests import get
from .detect import get_new_photo, name_of_age
from json import loads, dumps
from random import randint
import asyncio
from os import listdir, remove
import re

regex_link = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

all_files_json = 'handlers/all_files.json'
result_array_json = 'handlers/result_array.json'

players_array = dict()

try:
    all_files = loads(open(all_files_json).read())
except:
    all_files = dict()

try:
    result_array = loads(open(result_array_json).read())
except:
    result_array = {'faces_num': 0, 'faces_links': []}

print('all_files: ', all_files)
print('result_array: ', result_array)

MAX_FILES = 41
GAME_BORDER = 10

age_dataset = [i.strip().split(',') for i in open('dataset/age_set.csv').readlines()]


@dp.message_handler(content_types=['photo'])
async def handle_photo(msg: types.Message):
    await bot.send_chat_action(msg.from_user.id, 'typing')
    file_id = msg.photo[-1]['file_id']
    response = loads(get(f'https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}').text)

    if response['ok']:
        photo = get(f'https://api.telegram.org/file/bot{TOKEN}/{response["result"]["file_path"]}').content
        result_array['faces_num'] += 1
        result_array['faces_links'].append(
            f'https://api.telegram.org/file/bot{TOKEN}/{response["result"]["file_path"]}')
        print(f'https://api.telegram.org/file/bot{TOKEN}/{response["result"]["file_path"]}')
        new_photo_inf = get_new_photo(photo)
        await bot.send_photo(msg.from_user.id, new_photo_inf[0], caption=new_photo_inf[1])
    else:
        await send_photo(msg.from_user.id, 'dataset/witcher_process.jpg',
                         "Хмм, зараза... Что-то не так, возможно фотка слишком тяжелая")


@dp.message_handler(commands=['game'])
async def start_game(msg: types.Message):
    new_img_id = randint(1, MAX_FILES)
    players_array[msg.from_user.id] = {'playing': True, 'prev_img': new_img_id, 'score': 0, 'AI_score': 0,
                                       'was_id': [new_img_id]}
    if str(msg.from_user.id) not in result_array:
        result_array[str(msg.from_user.id)] = []

    await msg.reply("Ну давайте  поиграем:")
    print(f'dataset/{new_img_id}.jpg')
    await send_photo(msg.from_user.id, f'dataset/{new_img_id}.jpg', "Сколько лет Вы дадите этому человеку?")


@dp.message_handler(commands=['stop'])
async def stop_game(msg: types.Message):
    if msg.from_user.id in players_array:
        score, AI_score = players_array[msg.from_user.id]['score'], players_array[msg.from_user.id]['AI_score']

        if score == AI_score:
            frase = 'Ничья!\nСыграете еще? /game'
        elif score < AI_score:
            frase = 'Ух ты! Вы одолели ИИ?\nА еще раз сможете? /game'
        else:
            frase = 'Вы проиграли ИИ, ну а кто бы справился?\nПопробуйте еще раз /game'

        await bot.send_message(msg.from_user.id, f'Количество Ваших ошибок: {score} {name_of_age(score)}\n'
                                                 f'Ошибок ИИ: {AI_score}  {name_of_age(AI_score)}\n'
                                                 f'{frase}')

        result_array[str(msg.from_user.id)].append((score, AI_score))
        open(result_array_json, 'w').write(dumps(result_array))
        players_array[msg.from_user.id]['playing'] = False


@dp.message_handler(commands=['send_all'])
async def send_all(msg: types.Message):
    await msg.reply(r"Сам попросил ¯\_(ツ)_/¯")
    for file in sorted(listdir('dataset')):
        if file.endswith('jpg'):
            await send_photo(msg.from_user.id, f'dataset/{file}')

    await msg.reply(f'Это все! {len(all_files)}')
    open(all_files_json, 'w').write(dumps(all_files))
    print(len(all_files))


# @dp.message_handler(commands=['qq'])
# async def qq(msg: types.Message):
#     await msg.reply(r"Сам попросил ¯\_(ツ)_/¯")
#     for file in sorted(listdir('dataset')):
#         if 'process' in file and 'witcher' not in file:
#             remove(f'dataset/{file}')
#


@dp.message_handler(commands=['send_stat'])
async def send_stat(msg: types.Message):
    await bot.send_document(878744319, open('handlers/result_array.json', 'rb').read())


@dp.message_handler(commands=['check_all'])
async def check_all(msg: types.Message):
    await msg.reply(r"Проверяю все ...")
    all_files_in_check_all = sorted(listdir('dataset'))
    for i, file in enumerate(all_files_in_check_all):
        if file.split('.')[0] + '_process.jpg' not in all_files_in_check_all and \
                'process' not in file and file.endswith('jpg'):
            file = 'dataset/' + file
            open(file.split('.')[0] + '_process.jpg', 'wb').write(get_new_photo(open(file, 'rb').read())[0])
            await bot.send_message(msg.from_user.id, f'{i + 1}) {file}')
    await bot.send_message(msg.from_user.id, f'Все файлы оцифрованы')


@dp.message_handler(commands=['start'])
async def process_start_command(msg: types.Message):
    await bot.send_message(msg.from_user.id,
                           f"Привет, {msg.from_user.first_name}! Я могу *угадать возраст* человека по его фотографии!\n "
                           f"Я - \"слабый\" (не 💪) искусственный интелект, то есть предназначен для выполнения "
                           f"сторого одной задачи - "
                           f"_определение возраста_. Это означает, что я и другие подобные мне ИИ - `совершенно` "
                           f"безвредны, "
                           f"и мы точно *НЕ* сможем захватить мир _(Ну хотя бы потому, что мы не знем как 😄)_",
                           parse_mode=types.ParseMode.MARKDOWN)

    await bot.send_chat_action(msg.from_user.id, 'typing')
    await asyncio.sleep(8)

    await bot.send_message(msg.from_user.id,
                           f"Просто отправьте мне *фото человека* (например, Ваше 😄), а я, используя свою "
                           f"`нейросеть`, попробую угадать сколько ему _лет_?",
                           parse_mode=types.ParseMode.MARKDOWN)

    await bot.send_chat_action(msg.from_user.id, 'typing')
    await asyncio.sleep(4)

    await bot.send_message(msg.from_user.id,
                           f"Также Вы можете сразиться со мной в игре `\"Угадай сколько лет?\"`. Просто отправьте мне "
                           f"/game и впишите ответ в числовом формате, например: `27`",
                           parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(commands=['help'])
async def process_help_command(msg: types.Message):
    await msg.reply("/game - Начать игру\n/stop - Окончить игру\n"
                    "Чтобы я мог угадать возраст - просто пришлите мне фото нуного человека")


@dp.message_handler(commands=['dev'])
async def process_help_command(msg: types.Message):
    await msg.reply("/send_all - Отправить мне все файлы\n"
                    "/check_all - Обратать все возможные файлы\n"
                    "/send_stat - Прислать статистику игр")


@dp.message_handler()
async def number_end(msg: types.Message):
    if msg.text.strip().isdigit() and msg.from_user.id in players_array and players_array[msg.from_user.id]['playing']:
        age = int(msg.text.strip())
        real_age, AI_age = get_age_by_id(players_array[msg.from_user.id]['prev_img'])

        players_array[msg.from_user.id]['score'] += abs(real_age - age)
        players_array[msg.from_user.id]['AI_score'] += abs(AI_age - real_age)

        prev_img_id = players_array[msg.from_user.id]['prev_img']

        new_img_id = randint(1, MAX_FILES)
        while new_img_id in players_array[msg.from_user.id]['was_id']:
            new_img_id = randint(1, MAX_FILES)

        players_array[msg.from_user.id]['was_id'].append(new_img_id)
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

        # await bot.send_message(msg.from_user.id, f'Your delta: {abs(real_age - age)}')
        # await bot.send_message(msg.from_user.id, f'AI delta: {abs(AI_age - real_age)}')

        await send_photo(msg.from_user.id, f"dataset/{prev_img_id}_process.jpg",
                         "А вот, что об этом думает наша нейросеть", 2)

        if len(players_array[msg.from_user.id]['was_id']) == GAME_BORDER:
            await stop_game(msg)
        else:
            await send_photo(msg.from_user.id, f'dataset/{new_img_id}.jpg', "А сколько лет Вы дадите этому человеку?",
                             4)
    elif is_link(msg.text.strip()):
        await bot.send_chat_action(msg.from_user.id, 'typing')
        url = msg.text.strip()

        try:
            photo = get(url).content
            print(url)
            new_photo_inf = get_new_photo(photo)
            await bot.send_photo(msg.from_user.id, new_photo_inf[0], caption=new_photo_inf[1])
        except:
            await send_photo(msg.from_user.id, 'dataset/witcher_process.jpg',
                             "Ошибка! Возможно ссылка неверная")
    else:
        await bot.send_message(msg.from_user.id, "Извините, я Вас не понимаю\nПросто напомню, что есть команда /help")


def get_age_by_id(photo_id):
    return int(age_dataset[photo_id - 1][1]), int(age_dataset[photo_id - 1][2])


def is_link(link):
    return re.match(regex_link, link) is not None


async def send_photo(to, filename, caption="", sleep_time=0):
    await bot.send_chat_action(to, 'upload_photo')
    if sleep_time:
        await asyncio.sleep(sleep_time)

    file_tusent = all_files[filename] if filename in all_files else open(filename, 'rb').read()
    sended_photo = await bot.send_photo(to, file_tusent, caption=caption)

    if filename not in all_files:
        all_files[filename] = sended_photo.photo[0].file_id
