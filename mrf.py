import telebot
from telebot import types
import time
import os
from flask import Flask, request
import redis
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import requests
import schedule

scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

server = Flask(__name__)
API_TOKEN = '1395353835:AAG2S0pc3uUL2oGbnQLBycnECAj_SqZv4uI'
bot = telebot.TeleBot(API_TOKEN)
user_dict = {}
r = redis.from_url(
    "redis://h:p8dcd27beb1689f9ada4a3f8652a1c99fbf852394cdd2d38fb8ec2d6de60c5622@ec2-52-204-185-105.compute-1.amazonaws.com:20719")


@ server.route('/' + API_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates(
        [telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@ server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(
        url='https://guarded-reaches-36373.herokuapp.com/' + API_TOKEN)
    return "!", 200


class User:
    def __init__(self, platoon):
        self.platoon = platoon
        self.name = None


@ bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    msg = bot.reply_to(message, """\
Welcome to MRF's Recall Bot. \n
Enter passcode:
""")
    bot.register_next_step_handler(msg, process_passcode_step)


def process_passcode_step(message):
    try:
        passcode = message.text
        markup = types.ReplyKeyboardMarkup(
            row_width=1, one_time_keyboard=True)
        if passcode == 'abc':
            markup.add('38th', '39th', '40th')
            msg = bot.reply_to(
                message, "Enter your platoon: ", reply_markup=markup)
            user_id = message.chat.id
            user_name = message.chat.first_name
            bot.register_next_step_handler(msg, process_pre_platoon_step)
            r.set(user_name, user_id)
        else:
            markup.add('/start')
            msg = bot.reply_to(
                message, 'Incorrect passcode. Check with your PC/FS for the correct passcode. \n(passcode is case sensitive) \n\nPlease restart the bot by typing /start.', reply_markup=markup)
    except Exception as e:
        pass


def process_pre_platoon_step(message):
    try:
        chat_id = message.chat.id
        pre_platoon = message.text
        print('Users platoon: ' + pre_platoon)
        user = User(pre_platoon)
        user_dict[chat_id] = user
        user.pre_platoon = pre_platoon
        markup = types.ReplyKeyboardMarkup(
            row_width=1, one_time_keyboard=True)
        if pre_platoon == '38th':
            markup.add('abc', 'dec', 'cgd')
            msg = bot.reply_to(
                message, 'Enter your name: ', reply_markup=markup)
        elif pre_platoon == '39th':
            markup.add('Sailesh', 'Gi Suk', 'Kian Siang', 'Abilash', 'Firdaus', 'Jeng Yi', 'Shariff', 'Ray', 'Jian Hao', 'Baodo', 'Ilyas', 'Mazlan', 'Ji Hao', 'Prithiv', 'Balaji', 'Elden',
                       'Sadiq', 'Ismail', 'Beaumont', 'Teng Hee', 'Kim', 'Zahid', 'Ramlan', 'Harith', 'Hamidi', 'Santhosh', 'Wei Tao', 'Farhan', 'Enzo', 'Syazwan', 'Idris', 'Perumal', 'Ezuan', 'Danish')
            msg = bot.reply_to(
                message, 'Enter your name:', reply_markup=markup)
        elif pre_platoon == '40th':
            markup.add('Steven', 'Ethan', 'Rizwan', 'Anish', 'Kaiser', 'Zulfan', 'Qi Rui', 'Chen Jun', 'Josh', 'Asher', 'Simba', 'Abhi', 'Ming Ju', 'Sim Wei', 'Shinn', 'Kyaw Soe', 'Frederick', 'Ming Xuan',
                       'Cedric', 'Shannon', 'Min Hong', 'Darius', 'Sidharth', 'Jazz', 'Ranveer', 'Chao Ming', 'Abdiel', 'Royston', 'Kester', 'Wendell', 'Ryan', 'Paolo', 'Sibi', 'Benjamin', 'Ming Hui', 'William')
            msg = bot.reply_to(
                message, 'Enter your name:', reply_markup=markup)
        bot.register_next_step_handler(msg, process_nameing_step)
    except Exception as e:
        bot.reply_to(
            message, 'Invalid Input, please restart by typing \n/start')


def process_nameing_step(message):
    try:
        chat_id = message.chat.id
        nameing = message.text
        user = user_dict[chat_id]
        user.nameing = nameing
        markup = types.ReplyKeyboardMarkup(
            row_width=1, one_time_keyboard=True)
        markup.add('Yes', 'No')
        msg = bot.reply_to(message,  'Please verify that the following information is correct\n\nYour platoon is: ' + user.pre_platoon +
                           '\nYour name is: ' + user.nameing, reply_markup=markup)
        bot.register_next_step_handler(msg, process_verify_step)
    except Exception as e:
        pass


def process_verify_step(message):
    try:
        chat_id = message.chat.id
        verify = message.text
        user = user_dict[chat_id]
        user.verify = verify
        markup = types.ReplyKeyboardMarkup(
            row_width=1, one_time_keyboard=True)
        print(user.pre_platoon)
        print(user.nameing)
        if verify == 'Yes':
            bot.send_message(
                chat_id, 'You have successfully been registered into our database. \n\nDo not delete/stop this bot in case of a recall. \n\nHave a nice day.')
            if user.pre_platoon == "38th":
                sheet = client.open('sheets').get_worksheet(0)
                if user.nameing == "abc":
                    sheet.update_cell(2, 4, "yes")
                elif user.nameing == "dec":
                    sheet.update_cell(3, 4, "yes")
            elif user.pre_platoon == "39th":
                sheet = client.open('sheets').get_worksheet(1)
                if user.nameing == "simba":
                    sheet.update('B2:C2', [[user.time, user.location]])
            elif user.pre_platoon == "40th":
                sheet = client.open('sheets').get_worksheet(2)
                if user.nameing == 'Steven':
                    sheet.update_acell('D3', 'yes')
                elif user.nameing == 'Ethan':
                    sheet.update_acell('D4', 'yes')
                elif user.nameing == 'Rizwan':
                    sheet.update_acell('D7', 'yes')
                elif user.nameing == 'Anish':
                    sheet.update_acell('D8', 'yes')
                elif user.nameing == 'Kaiser':
                    sheet.update_acell('D9', 'yes')
                elif user.nameing == 'Zulfan':
                    sheet.update_acell('D10', 'yes')
                elif user.nameing == 'Qi Rui':
                    sheet.update_acell('D11', 'yes')
                elif user.nameing == 'Chen Jun':
                    sheet.update_acell('D12', 'yes')
                elif user.nameing == 'Josh':
                    sheet.update_acell('D13', 'yes')
                elif user.nameing == 'Asher':
                    sheet.update_acell('D14', 'yes')
                elif user.nameing == 'Simba':
                    sheet.update_acell('D15', 'yes')
                elif user.nameing == 'Abhi':
                    sheet.update_acell('D16', 'yes')
                elif user.nameing == 'Ming Jun':
                    sheet.update_acell('D19', 'yes')
                elif user.nameing == 'Sim Wei':
                    sheet.update_acell('D20', 'yes')
                elif user.nameing == 'Shinn':
                    sheet.update_acell('D21', 'yes')
                elif user.nameing == 'Kyaw Soe':
                    sheet.update_acell('D22', 'yes')
                elif user.nameing == 'Frederick':
                    sheet.update_acell('D23', 'yes')
                elif user.nameing == 'Ming Xuan':
                    sheet.update_acell('D24', 'yes')
                elif user.nameing == 'Cedric':
                    sheet.update_acell('D25', 'yes')
                elif user.nameing == 'Shannon':
                    sheet.update_acell('D26', 'yes')
                elif user.nameing == 'Min Hong':
                    sheet.update_acell('D29', 'yes')
                elif user.nameing == 'Darius':
                    sheet.update_acell('D30', 'yes')
                elif user.nameing == 'Jazz':
                    sheet.update_acell('D31', 'yes')
                elif user.nameing == 'Ranveer':
                    sheet.update_acell('D32', 'yes')
                elif user.nameing == 'Chao Ming':
                    sheet.update_acell('D33', 'yes')
                elif user.nameing == 'Abdiel':
                    sheet.update_acell('D36', 'yes')
                elif user.nameing == 'Royston':
                    sheet.update_acell('D37', 'yes')
                elif user.nameing == 'Kester':
                    sheet.update_acell('D38', 'yes')
                elif user.nameing == 'Wendell':
                    sheet.update_acell('D39', 'yes')
                elif user.nameing == 'Ryan':
                    sheet.update_acell('D40', 'yes')
                elif user.nameing == 'Paolo':
                    sheet.update_acell('D41', 'yes')
                elif user.nameing == 'Sibi':
                    sheet.update_acell('D42', 'yes')
                elif user.nameing == 'Benjamin':
                    sheet.update_acell('D43', 'yes')
                elif user.nameing == 'Ming Hui':
                    sheet.update_acell('D44', 'yes')
                elif user.nameing == 'William':
                    sheet.update_acell('D45', 'yes')
                elif user.nameing == '':
                    sheet.update_acell('D46', 'yes')
                else:
                    pass

        else:
            markup.add('/start')
            msg = bot.reply_to(
                message,  ' Please restart this form', reply_markup=markup)
    except Exception as e:
        bot.reply_to(
            message, 'Invalid Input, please restart by typing \n/start')


@ bot.message_handler(commands=['acknowledged', 'submitanother', 'restart'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    markup.add('38th', '39th', '40th')
    msg = bot.reply_to(message, """\
Please enter your details. \n
Enter your platoon:
""", reply_markup=markup)
    bot.register_next_step_handler(msg, process_platoon_step)


def process_platoon_step(message):
    try:
        chat_id = message.chat.id
        platoon = message.text
        print('Users platoon: ' + platoon)
        print(chat_id)
        user = User(platoon)
        user_dict[chat_id] = user
        markup = types.ReplyKeyboardMarkup(
            row_width=1, one_time_keyboard=True)
        if platoon == '38th':
            markup.add('abc', 'dec', 'cgd')
            msg = bot.reply_to(
                message, 'Enter your name:', reply_markup=markup)
        elif platoon == '39th':
            markup.add('Sailesh', 'Gi Suk', 'Kian Siang', 'Abilash', 'Firdaus', 'Jeng Yi', 'Shariff', 'Ray', 'Jian Hao', 'Baodo', 'Ilyas', 'Mazlan', 'Ji Hao', 'Prithiv', 'Balaji', 'Elden',
                       'Sadiq', 'Ismail', 'Beaumont', 'Teng Hee', 'Kim', 'Zahid', 'Ramlan', 'Harith', 'Hamidi', 'Santhosh', 'Wei Tao', 'Farhan', 'Enzo', 'Syazwan', 'Idris', 'Perumal', 'Ezuan', 'Danish')
            msg = bot.reply_to(
                message, 'Enter your name:', reply_markup=markup)
        elif platoon == '40th':
            markup.add('Steven', 'Ethan', 'Rizwan', 'Anish', 'Kaiser', 'Zulfan', 'Qi Rui', 'Chen Jun', 'Josh', 'Asher', 'Simba', 'Abhi', 'Ming Ju', 'Sim Wei', 'Shinn', 'Kyaw Soe', 'Frederick', 'Ming Xuan',
                       'Cedric', 'Shannon', 'Min Hong', 'Darius', 'Sidharth', 'Jazz', 'Ranveer', 'Chao Ming', 'Abdiel', 'Royston', 'Kester', 'Wendell', 'Ryan', 'Paolo', 'Sibi', 'Benjamin', 'Ming Hui', 'William')
            msg = bot.reply_to(
                message, 'Enter your name:', reply_markup=markup)
        else:
            pass
        bot.register_next_step_handler(msg, process_naming_step)
    except Exception as e:
        bot.reply_to(
            message, 'Invalid Input, please restart by typing /restart')


def process_naming_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        print('Users name: '+name)
        print(chat_id)
        user = user_dict[chat_id]
        user.name = name
        markup = types.ReplyKeyboardMarkup(
            row_width=1, one_time_keyboard=True)
        markup.add('Yes', 'No')
        msg = bot.reply_to(message,  ' Please verify that the following information is correct\n \n Your platoon is: ' + user.platoon +
                           '\n Your name is: ' + user.name, reply_markup=markup)
        r.set(name, chat_id)
        bot.register_next_step_handler(msg, process_verification_step)
    except Exception as e:
        bot.reply_to(
            message, 'Invalid Input, please restart by typing /restart')


def process_verification_step(message):
    try:
        chat_id = message.chat.id
        verification = message.text
        print('Details correrct?: ' + verification)
        print(chat_id)
        markup = types.ReplyKeyboardMarkup(
            row_width=2, one_time_keyboard=True)
        if verification == 'Yes':
            markup.add('0-10mins', '10-20mins', '20-30mins', '30-40mins',
                       '40-50mins', '50-60mins', '60-70mins', '70-80mins')
            msg = bot.reply_to(
                message,  ' What is ur ETA to Nee Soon Camp?', reply_markup=markup)
            bot.register_next_step_handler(msg, process_time_step)
        else:
            markup.add('/restart')
            msg = bot.reply_to(
                message,  ' Please restart this form', reply_markup=markup)
    except Exception as e:
        bot.reply_to(
            message, 'Invalid Input, please restart by typing /restart')


def process_time_step(message):
    try:
        chat_id = message.chat.id
        time = message.text
        print('Users ETA: ' + time)
        print(chat_id)
        user = user_dict[chat_id]
        user.time = time
        markup = types.ReplyKeyboardMarkup(
            row_width=1, one_time_keyboard=True)
        location_button = types.KeyboardButton(
            'Send location', request_location=True)
        markup.add(location_button)
        msg = bot.reply_to(
            message,  ' Please send your current location', reply_markup=markup)
        bot.register_next_step_handler(msg, process_location_step)

    except Exception as e:
        bot.reply_to(
            message, 'Invalid Input, please restart by typing /restart')


def process_location_step(message):
    try:
        chat_id = message.chat.id
        location = "{0},{1}".format(
            message.location.latitude, message.location.longitude)
        print(location)
        print(chat_id)
        user = user_dict[chat_id]
        user.location = "https://www.google.com/maps/place/"+location
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(
            row_width=1, one_time_keyboard=True)
        markup.add('/confirmed')
        msg = bot.reply_to(
            message,  'To confirm your details, please type /confirmed', reply_markup=markup)
        bot.register_next_step_handler(msg, process_sheets)
        bot.register_next_step_handler(msg, platoon40)

    except Exception as e:
        bot.reply_to(
            message, 'Invalid Input, please restart by typing /restart')


def process_sheets(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        markup = types.ReplyKeyboardMarkup(
            row_width=1, one_time_keyboard=True)
        markup.add("/submitanother")
        msg = bot.reply_to(
            message,  'Thank you. \n\nReport back to NEE SOON CAMP immediately, do not rush. Safety First. \n\nTo submit another from, type /submitanother', reply_markup=markup)
        if user.platoon == "38th":
            sheet = client.open('sheets').get_worksheet(0)
            if user.name == "abc":
                sheet.update('B2:C2', [[user.time, user.location]])
        elif user.platoon == "39th":
            platoon39(message)
        elif user.platoon == "40th":
            platoon40(message)

    except Exception as e:
        bot.reply_to(
            message, 'Invalid Input, please restart by typing /restart')


# send_recall

db_keys = r.keys(pattern="*")


def send_announcments(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        for keys in db_keys:
            keys_values = r.get(keys).decode("UTF-8")
            print(keys_values)
            send_text = 'https://api.telegram.org/bot' + API_TOKEN + \
                '/sendMessage?chat_id=' + keys_values + '&text=' + user.recallmsg
            print(send_text)
            response = requests.get(send_text)
            print(response.json())
            markup = types.ReplyKeyboardMarkup(
                row_width=1, one_time_keyboard=True)
            markup.add("/acknowledged")
            bot.send_message(
                keys_values, "To acknowledge, reply with \n/acknowledged", reply_markup=markup)
            time.sleep(1)
    except Exception as e:
        pass


__location__ = os.path.realpath(os.path.join(
    os.getcwd(), os.path.dirname(__file__)))

bot_message = open(os.path.join(__location__, "message_bot.txt"))

text_content = bot_message.read()


@ bot.message_handler(commands=['send_recall'])
def send_hi(message):
    msg = bot.reply_to(message, """\
Welcome to the admin side of MRF's recall bot. \n
Upon completion this will send a recall message to all troopers in the unit. Only authorized personnel can access this option \n
Enter password:
""")
    bot.register_next_step_handler(msg, process_password_step)


def process_password_step(message):
    try:
        chat_id = message.chat.id
        password = message.text
        user = User(password)
        user_dict[chat_id] = user
        markup = types.ReplyKeyboardMarkup(
            row_width=1, one_time_keyboard=True)
        if password == 'MRF@ADMIN':
            msg = bot.reply_to(
                message, 'Enter recall message: ', reply_markup=markup)
            bot.register_next_step_handler(msg, process_recallmsg)

        else:
            markup.add('/send_recall')
            msg = bot.reply_to(
                message, 'Incorrect passcode. Check with PC/FS for the correct passcode. \n(passcode is case sensitive) \n\nPlease restart the bot by typing \n /send_recall.', reply_markup=markup)

    except Exception as e:
        pass


def process_recallmsg(message):
    try:
        chat_id = message.chat.id
        recallmsg = message.text
        user = user_dict[chat_id]
        user.recallmsg = recallmsg
        markup = types.ReplyKeyboardMarkup(
            row_width=1, one_time_keyboard=True)
        markup.add('Yes', 'No')
        msg = bot.reply_to(
            message,  ' Please verify that the following information is correct\n \nRecall message is:\n' + user.recallmsg, reply_markup=markup)
        bot.register_next_step_handler(msg, process_verifyrecall_step)

    except Exception as e:
        pass


def process_verifyrecall_step(message):
    try:
        chat_id = message.chat.id
        verifyrecall = message.text
        user = user_dict[chat_id]
        user.verifyrecall = verifyrecall
        markup = types.ReplyKeyboardMarkup(
            row_width=2, one_time_keyboard=True)
        if verifyrecall == 'Yes':
            send_announcments(message)
            time.sleep(1)
            msg = bot.reply_to(
                message,  'Recall sent.', reply_markup=markup)
            msg = bot.send_message(
                chat_id, "A list of troopers ETA will also be sent to @ (MRF_recall_admin_side) group")
            send_list()
            schedule.every(2).minutes.do(send_list).tag('list40th')
            bot.send_message(
                '-307260384', 'This list of Troopers ETA will be updated and sent every 2 minutes.\n\nTo stop the sending of ETA list, go to @MRF_Recall_bot and type \n/stop_send_list.')
            while True:
                schedule.run_pending()
                time.sleep(1)

        else:
            markup.add('/send_recall')
            msg = bot.reply_to(
                message,  ' Please restart this form ', reply_markup=markup)
    except Exception as e:
        pass


def send_list():
    sheet = client.open('sheets').get_worksheet(2)
    val = sheet.get("A2:C37")
    valnew = "\n".join(map(str, val)).replace(
        '[', '').replace(']', '').replace("'", '')
    # if want each line 2 people, .replace('[', '   '])
    bot.send_message(
        '-307260384', '**40th ETA** \n(Name, ETA, Location) \n\n' + valnew)


@ bot.message_handler(commands=['send_list'])
def job(message):
    msg = bot.reply_to(
        message, "Troopers ETA list will be sent to: \n@ (MRF_recall_admin) group")
    send_list()


@ bot.message_handler(commands=['stop_send_list'])
def stop_send_list(message):
    msg = bot.reply_to(
        message, "ETA list has stopped sending to admin group. \n\nHave a nice day!")
    schedule.clear('list40th')


def platoon39(message):
    chat_id = message.chat.id
    sheet = client.open('sheets').get_worksheet(1)
    user = user_dict[chat_id]
    if user.name == "Sailesh":
        sheet.update('B3:C3', [[user.time, user.location]])
    elif user.name == "Gi Suk":
        sheet.update('B4:C4', [[user.time, user.location]])
    elif user.name == "Kian Siang":
        sheet.update('B7:C7', [[user.time, user.location]])
    elif user.name == "Abilash":
        sheet.update('B8:C8', [[user.time, user.location]])
    elif user.name == "Firdaus":
        sheet.update('B9:C9', [[user.time, user.location]])
    elif user.name == "Jeng Yi":
        sheet.update('B10:C10', [[user.time, user.location]])
    elif user.name == "Shariff":
        sheet.update('B11:C11', [[user.time, user.location]])
    elif user.name == "Ray":
        sheet.update('B12:C12', [[user.time, user.location]])
    elif user.name == "Jian Hao":
        sheet.update('B13:C13', [[user.time, user.location]])
    elif user.name == "Baodo":
        sheet.update('B14:C14', [[user.time, user.location]])
    elif user.name == "Ilyas":
        sheet.update('B15:C15', [[user.time, user.location]])
    elif user.name == "Mazlan":
        sheet.update('B16:C16', [[user.time, user.location]])
    elif user.name == "Ji Hao":
        sheet.update('B19:C19', [[user.time, user.location]])
    elif user.name == "Prithiv":
        sheet.update('B20:C20', [[user.time, user.location]])
    elif user.name == "Balaji":
        sheet.update('B21:C21', [[user.time, user.location]])
    elif user.name == "Elden":
        sheet.update('B22:C22', [[user.time, user.location]])
    elif user.name == "Sadiq":
        sheet.update('B23:C23', [[user.time, user.location]])
    elif user.name == "Ismail":
        sheet.update('B24:C24', [[user.time, user.location]])
    elif user.name == "Beaumont":
        sheet.update('B25:C25', [[user.time, user.location]])
    elif user.name == "Teng Hee":
        sheet.update('B26:C26', [[user.time, user.location]])
    elif user.name == "Kim":
        sheet.update('B29:C29', [[user.time, user.location]])
    elif user.name == "Zahid":
        sheet.update('B30:C30', [[user.time, user.location]])
    elif user.name == "Ramlan":
        sheet.update('B31:C31', [[user.time, user.location]])
    elif user.name == "Harith":
        sheet.update('B32:C32', [[user.time, user.location]])
    elif user.name == "Hamidi":
        sheet.update('B33:C33', [[user.time, user.location]])
    elif user.name == "Santhosh":
        sheet.update('B36:C36', [[user.time, user.location]])
    elif user.name == "Wei Tao":
        sheet.update('B37:C37', [[user.time, user.location]])
    elif user.name == "Farhan":
        sheet.update('B38:C38', [[user.time, user.location]])
    elif user.name == "Enzo":
        sheet.update('B39:C39', [[user.time, user.location]])
    elif user.name == "Syazwan":
        sheet.update('B40:C40', [[user.time, user.location]])
    elif user.name == "Idris":
        sheet.update('B41:C41', [[user.time, user.location]])
    elif user.name == "Perumal":
        sheet.update('B42:C42', [[user.time, user.location]])
    elif user.name == "Ezuan":
        sheet.update('B43:C42', [[user.time, user.location]])
    elif user.name == "Danish":
        sheet.update('B44:C44', [[user.time, user.location]])

    else:
        pass


def platoon40(message):
    chat_id = message.chat.id
    sheet = client.open('sheets').get_worksheet(2)
    user = user_dict[chat_id]
    if user.name == "Steven":
        sheet.update('B3:C3', [[user.time, user.location]])
    elif user.name == "Ethan":
        sheet.update('B4:C4', [[user.time, user.location]])
    elif user.name == "Rizwan":
        sheet.update('B7:C7', [[user.time, user.location]])
    elif user.name == "Anish":
        sheet.update('B8:C8', [[user.time, user.location]])
    elif user.name == "Kaiser":
        sheet.update('B9:C9', [[user.time, user.location]])
    elif user.name == "Zulfan":
        sheet.update('B10:C10', [[user.time, user.location]])
    elif user.name == "Qi Rui":
        sheet.update('B11:C11', [[user.time, user.location]])
    elif user.name == "Chen Jun":
        sheet.update('B12:C12', [[user.time, user.location]])
    elif user.name == "Josh":
        sheet.update('B13:C13', [[user.time, user.location]])
    elif user.name == "Asher":
        sheet.update('B14:C14', [[user.time, user.location]])
    elif user.name == "Simba":
        sheet.update('B15:C15', [[user.time, user.location]])
    elif user.name == "Abhi":
        sheet.update('B16:C16', [[user.time, user.location]])
    elif user.name == "Ming Jun":
        sheet.update('B19:C19', [[user.time, user.location]])
    elif user.name == "Sim Wei":
        sheet.update('B20:C20', [[user.time, user.location]])
    elif user.name == "Shinn":
        sheet.update('B21:C21', [[user.time, user.location]])
    elif user.name == "Kyaw Soe":
        sheet.update('B22:C22', [[user.time, user.location]])
    elif user.name == "Frederick":
        sheet.update('B23:C23', [[user.time, user.location]])
    elif user.name == "Ming Xuan":
        sheet.update('B24:C24', [[user.time, user.location]])
    elif user.name == "Cedric":
        sheet.update('B25:C25', [[user.time, user.location]])
    elif user.name == "Shannon":
        sheet.update('B26:C26', [[user.time, user.location]])
    elif user.name == "Min Hong":
        sheet.update('B29:C29', [[user.time, user.location]])
    elif user.name == "Darius":
        sheet.update('B30:C30', [[user.time, user.location]])
    elif user.name == "Sidharth":
        sheet.update('B31:C31', [[user.time, user.location]])
    elif user.name == "Jazz":
        sheet.update('B32:C32', [[user.time, user.location]])
    elif user.name == "Ranveer":
        sheet.update('B33:C33', [[user.time, user.location]])
    elif user.name == "Chao Ming":
        sheet.update('B36:C36', [[user.time, user.location]])
    elif user.name == "Abdiel":
        sheet.update('B37:C37', [[user.time, user.location]])
    elif user.name == "Royston":
        sheet.update('B38:C38', [[user.time, user.location]])
    elif user.name == "Kester":
        sheet.update('B39:C39', [[user.time, user.location]])
    elif user.name == "Wendell":
        sheet.update('B40:C40', [[user.time, user.location]])
    elif user.name == "Ryan":
        sheet.update('B41:C41', [[user.time, user.location]])
    elif user.name == "Paolo":
        sheet.update('B42:C42', [[user.time, user.location]])
    elif user.name == "Sibi":
        sheet.update('B43:C42', [[user.time, user.location]])
    elif user.name == "Benjamin":
        sheet.update('B44:C44', [[user.time, user.location]])
    elif user.name == "Ming Hui":
        sheet.update('B45:C45', [[user.time, user.location]])
    elif user.name == "William":
        sheet.update('B46:C46', [[user.time, user.location]])
    else:
        pass


# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
