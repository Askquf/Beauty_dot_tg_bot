import telebot
import csv
from config import token, filename


bot = telebot.TeleBot(token)

def read_csv():
    with open(filename, encoding='UTF-8') as csv_file:
        data = list(csv.reader(csv_file, dialect=csv.excel))
        metro_dict = {}
        for item in data[1:]:
            salon = [item[0]] + item[2:len(item)]
            if item[1] not in metro_dict.keys():
                metro_dict.update({item[1]: [salon]})
            else:
                metro_dict[item[1]].append(salon)
        salon_types = data[0][6:]
    return salon_types, metro_dict

salon_types, data = read_csv()


@bot.message_handler()
def start_command(message):
    text = "Привет, <b>{}</b>! " \
           "Тут должен быть текст про то, что пользователю делать." \
           "Пожалуйста, выберите станцию метро".format(message.from_user.username)
    send = bot.send_message(message.from_user.id, text, parse_mode="HTML", reply_markup=get_menu(data.keys()))
    bot.register_next_step_handler(send, listen_metro)

def get_menu(params):
    menu = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for item in params:
        if isinstance(item, list):
            menu.add(*item)
        else:
            menu.add(item)
    menu.add('Заново')
    return menu

@bot.message_handler(func=lambda message: True)
def listen_metro(message):
    metro = message.text
    if metro in data.keys():
        send = bot.send_message(message.from_user.id, "Выберите тип салона красоты.", reply_markup=get_menu(salon_types))
        bot.register_next_step_handler(send, listen_type, metro)
    elif metro == 'Заново':
        bot.register_next_step_handler(message=bot.send_message(message.from_user.id, 'Хорошо, начинаем заново! Пожалуйста, выберите станцию метро.'), callback=listen_metro)
    else:
        bot.register_next_step_handler(message=bot.send_message(message.from_user.id,
                                                                'Метро не найдено, пожалуйста, выберите метро из списка.'),
                                       callback=listen_metro)


def listen_type(message, metro):
    salon_type = message.text
    result = []
    if salon_type in salon_types:
        index = salon_types.index(salon_type) + 5
        for item in data[metro]:
            if item[index] == '1':
                item_data = f'Название: {item[0]}\nВремя пути от метро: {item[1]}\n' \
                            f'Телефон: {item[2]}\nСайт: {item[3]}\n' \
                            f'Рейтинг: {item[4]}'
                result.append(item_data)
        if len(result) != 0:
            send = bot.send_message(message.from_user.id, '\n\n\n'.join(result))
            bot.send_message(message.from_user.id, 'Для нового запроса, выберите станцию метро', reply_markup=get_menu(data.keys()))
            bot.register_next_step_handler(send, listen_metro)
        else:
            send = bot.send_message(message.from_user.id, 'Для данного метро не найдены такие типы салона! Выберите другой тип или введите команду "заново", чтобы выбрать другую станцию метро.')
            bot.register_next_step_handler(send, listen_type, metro)
    elif salon_type == 'Заново':
        bot.register_next_step_handler(message=bot.send_message(message.from_user.id,
                                                                'Хорошо, начинаем заново! Пожалуйста, выберите станцию метро.', reply_markup=get_menu(data.keys())),
                                       callback=listen_metro)
    else:
        bot.register_next_step_handler(bot.send_message(message.from_user.id,
                                                                'Такой тип салона не найден, пожалуйста, выберите салон из списка.'),
                                       listen_type, metro)

def main():
    print("Бот запущен")
    bot.polling()


if __name__ == '__main__':
    main()
