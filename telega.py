import telebot
from telebot import types
import json
import os
import webbrowser

bot = telebot.TeleBot('7657754229:AAFYrVvNUqqhUld1ceSa10yPL4y4egjJGlg')
CHARACTERS_FILE = 'characters.json'

# Классы и подклассы
CLASSES = {
    'Воин': {
        'subclasses': ['Чемпион', 'Боевой мастер', 'Мистический рыцарь'],
        'spellcaster': False
    },
    'Волшебник': {
        'subclasses': ['Школа воплощения', 'Школа некромантии', 'Школа иллюзий'],
        'spellcaster': True
    },
    'Плут': {
        'subclasses': ['Вор', 'Убийца', 'Мистический трюкач'],
        'spellcaster': False
    },
    'Жрец': {
        'subclasses': ['Жизни', 'Смерти', 'Грома'],
        'spellcaster': True
    }
}

# Заклинания и заговоры
SPELLS = {
    'Волшебник': {
        'cantrips': ['Огненный снаряд', 'Луч холода', 'Магическая рука'],
        'spells': ['Волшебная стрела', 'Огненный шар', 'Невидимость']
    },
    'Жрец': {
        'cantrips': ['Священное пламя', 'Слово силы', 'Лечение ран'],
        'spells': ['Наказующий удар', 'Воскрешение', 'Защита от зла и добра']
    }
}

# Расы и их бонусы
RACES = {
    'Человек': {
        'bonuses': {'strength': 1, 'dexterity': 1, 'constitution': 1, 'intelligence': 1, 'wisdom': 1, 'charisma': 1}},
    'Эльф': {'bonuses': {'dexterity': 2, 'wisdom': 1}},
    'Гном': {'bonuses': {'constitution': 2, 'wisdom': 1}},
    'Гоблин': {'bonuses': {'dexterity': 2, 'constitution': 1}},
    'Драконорождённый': {'bonuses': {'strength': 2, 'charisma': 1}},
    'Орк': {'bonuses': {'strength': 2, 'constitution': 1}}
}


def load_characters():
    if os.path.exists(CHARACTERS_FILE):
        with open(CHARACTERS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_characters(characters):
    with open(CHARACTERS_FILE, 'w') as f:
        json.dump(characters, f, indent=4)

@bot.message_handler(commands=['info'])
def site(message):
    markup = types.InlineKeyboardMarkup()
    bt1 = types.InlineKeyboardButton('перейти на сайт', url='https://dnd.su/index.php')
    markup.row(bt1)
    bot.reply_to(message, 'Львиную долю знаний черпаю я из сокровищницы сайта dnd.su. Если жажда приключений и тайн Dungeons & Dragons разгорается в вашем сердце, советую посетить этот портал мудрости, а затем погрузиться в глубины Книги Игрока или тома Мастера Подземелий.', reply_markup=markup)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Создать персонажа')
    btn2 = types.KeyboardButton('Найти персонажа')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Добро пожаловать в генератор персонажей D&D!", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text in ['Создать персонажа', 'Найти персонажа'])
def handle_action(message):
    if message.text == 'Создать персонажа':
        create_character(message)
    else:
        find_character(message)


def create_character(message):
    msg = bot.send_message(message.chat.id, "Введите имя вашего персонажа:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, process_name_step)


def process_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text

        characters = load_characters()
        if name in characters:
            bot.send_message(chat_id, "Персонаж с таким именем уже существует.")
            return create_character(message)

        user_data = {'name': name, 'level': 1}
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = [types.KeyboardButton(race) for race in RACES.keys()]
        markup.add(*buttons)

        msg = bot.send_message(chat_id, "Выберите расу персонажа:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_race_step, user_data)
    except Exception as e:
        bot.reply_to(message, f'Ошибка: {e}')


def process_race_step(message, user_data):
    try:
        chat_id = message.chat.id
        race = message.text

        if race not in RACES:
            bot.send_message(chat_id, "Пожалуйста, выберите расу из предложенных.")
            return create_character(message)

        user_data['race'] = race
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = [types.KeyboardButton(cls) for cls in CLASSES.keys()]
        markup.add(*buttons)

        msg = bot.send_message(chat_id, "Выберите класс персонажа:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_class_step, user_data)
    except Exception as e:
        bot.reply_to(message, f'Ошибка: {e}')


def process_class_step(message, user_data):
    try:
        chat_id = message.chat.id
        char_class = message.text

        if char_class not in CLASSES:
            bot.send_message(chat_id, "Пожалуйста, выберите класс из предложенных.")
            return process_race_step(message, user_data)

        user_data['class'] = char_class
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = [types.KeyboardButton(sub) for sub in CLASSES[char_class]['subclasses']]
        markup.add(*buttons)

        msg = bot.send_message(chat_id, f"Выберите подкласс для {char_class}:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_subclass_step, user_data)
    except Exception as e:
        bot.reply_to(message, f'Ошибка: {e}')


def process_subclass_step(message, user_data):
    try:
        chat_id = message.chat.id
        subclass = message.text

        if subclass not in CLASSES[user_data['class']]['subclasses']:
            bot.send_message(chat_id, "Пожалуйста, выберите подкласс из предложенных.")
            return process_class_step(message, user_data)

        user_data['subclass'] = subclass

        if CLASSES[user_data['class']]['spellcaster']:
            msg = bot.send_message(chat_id,
                                   "Распределите характеристики (15,14,13,12,10,8) по:\nСила, Ловкость, Телосложение, Интеллект, Мудрость, Харизма\n\nВведите через пробел, например: 15 14 13 12 10 8",
                                   reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(msg, process_stats_step, user_data)
        else:
            user_data['spells'] = []
            user_data['cantrips'] = []
            msg = bot.send_message(chat_id,
                                   "Распределите характеристики (15,14,13,12,10,8) по:\nСила, Ловкость, Телосложение, Интеллект, Мудрость, Харизма\n\nВведите через пробел, например: 15 14 13 12 10 8",
                                   reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(msg, process_stats_step, user_data)
    except Exception as e:
        bot.reply_to(message, f'Ошибка: {e}')


def process_stats_step(message, user_data):
    try:
        chat_id = message.chat.id
        stats = message.text.split()

        if len(stats) != 6 or not all(s.isdigit() for s in stats):
            bot.send_message(chat_id, "Пожалуйста, введите 6 чисел через пробел.")
            return process_subclass_step(message, user_data)

        stats = list(map(int, stats))
        required = [15, 14, 13, 12, 10, 8]
        flag = []
        for el in stats:
            if el not in required or len(stats) != len(required) or el in flag:
                bot.send_message(chat_id, "Используйте только числа: 15,14,13,12,10,8.")
                return process_subclass_step(message, user_data)
            else:
                flag.append(el)

        user_data['stats'] = {
            'strength': stats[0],
            'dexterity': stats[1],
            'constitution': stats[2],
            'intelligence': stats[3],
            'wisdom': stats[4],
            'charisma': stats[5]
        }

        # Добавляем расовые бонусы
        race_bonuses = RACES[user_data['race']]['bonuses']
        for stat, bonus in race_bonuses.items():
            user_data['stats'][stat] += bonus

        if CLASSES[user_data['class']]['spellcaster']:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            buttons = [types.KeyboardButton(spell) for spell in SPELLS[user_data['class']]['cantrips']]
            markup.add(*buttons)
            msg = bot.send_message(chat_id, "Выберите заговор:", reply_markup=markup)
            bot.register_next_step_handler(msg, process_cantrip_step, user_data)
        else:
            complete_character(message, user_data)
    except Exception as e:
        bot.reply_to(message, f'Ошибка: {e}')


def process_cantrip_step(message, user_data):
    try:
        chat_id = message.chat.id
        cantrip = message.text

        if cantrip not in SPELLS[user_data['class']]['cantrips']:
            bot.send_message(chat_id, "Пожалуйста, выберите заговор из предложенных.")
            return process_stats_step(message, user_data)

        user_data['cantrips'] = [cantrip]

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = [types.KeyboardButton(spell) for spell in SPELLS[user_data['class']]['spells']]
        markup.add(*buttons)
        msg = bot.send_message(chat_id, "Выберите заклинание 1-го уровня:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_spell_step, user_data)
    except Exception as e:
        bot.reply_to(message, f'Ошибка: {e}')


def process_spell_step(message, user_data):
    try:
        chat_id = message.chat.id
        spell = message.text

        if spell not in SPELLS[user_data['class']]['spells']:
            bot.send_message(chat_id, "Пожалуйста, выберите заклинание из предложенных.")
            return process_cantrip_step(message, user_data)

        user_data['spells'] = [spell]
        complete_character(message, user_data)
    except Exception as e:
        bot.reply_to(message, f'Ошибка: {e}')


def complete_character(message, user_data):
    try:
        chat_id = message.chat.id
        name = user_data['name']

        characters = load_characters()
        characters[name] = user_data
        save_characters(characters)

        character_info = format_character_info(user_data)
        bot.send_message(chat_id, f"Персонаж создан!\n\n{character_info}", reply_markup=main_menu())
    except Exception as e:
        bot.reply_to(message, f'Ошибка: {e}')


def format_character_info(character):
    info = (
        f"👤 Имя: {character['name']}\n"
        f"🏆 Уровень: {character['level']}\n"
        f"🧝 Раса: {character['race']}\n"
        f"⚔️ Класс: {character['class']} ({character['subclass']})\n\n"
        "📊 Характеристики:\n"
        f"💪 Сила: {character['stats']['strength']}\n"
        f"🏹 Ловкость: {character['stats']['dexterity']}\n"
        f"🛡️ Телосложение: {character['stats']['constitution']}\n"
        f"📚 Интеллект: {character['stats']['intelligence']}\n"
        f"🔮 Мудрость: {character['stats']['wisdom']}\n"
        f"🎭 Харизма: {character['stats']['charisma']}\n"
    )

    if 'cantrips' in character:
        info += f"\n🔮 Заговоры: {', '.join(character['cantrips'])}\n"
    if 'spells' in character:
        info += f"✨ Заклинания: {', '.join(character['spells'])}\n"

    return info


def find_character(message):
    msg = bot.send_message(message.chat.id, "Введите имя персонажа:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, process_find_character)


def process_find_character(message):
    try:
        chat_id = message.chat.id
        name = message.text

        characters = load_characters()
        if name in characters:
            character_info = format_character_info(characters[name])
            bot.send_message(chat_id, character_info, reply_markup=main_menu())
        else:
            bot.send_message(chat_id, "Персонаж не найден.", reply_markup=main_menu())
    except Exception as e:
        bot.reply_to(message, f'Ошибка: {e}')


def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Создать персонажа')
    btn2 = types.KeyboardButton('Найти персонажа')
    markup.add(btn1, btn2)
    return markup


if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()