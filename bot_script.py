from telebot import TeleBot, types
from telebot import formatting
import subprocess
import os
import time
import psutil
from encrypt import *
from decrypt import *


# Tech bot information
token = '7155852399:AAEFVqqK-a8Ig4kyCz-S6g-_f06EusgIZ2Y'
bot = TeleBot(token)


# Keyboards
select_mode_keyboard = types.InlineKeyboardMarkup()
aes_file_btn = types.InlineKeyboardButton(text="Зашифровать файл📄", callback_data="encrypt_file")
aes_message_btn = types.InlineKeyboardButton(text="Зашифровать сообщение✉️", callback_data="encrypt_message")
select_mode_keyboard.add(aes_message_btn)
select_mode_keyboard.add(aes_file_btn)


# Global variables
excluded_alphabet = 'йцукенгшщзхъфывапролджэячсмитьбюёЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮЁ'
start_msg = (f'<b>AES bot</b>🤖 приветствует вас!\n'
             f'Я умею шифровать данные, используя алгоритм асимметричного шифрования AES.\n'
             f'На данный момент я работаю только с <b>английским</b> языком.\n'
             f'Я могу зашифровать ваше сообщение или файл с расширением <b>.txt</b>\n'
             f'Выберите, что вы хотите зашифровать:')
file_enc_msg = (f'Отправьте файл с расширением <b>.txt</b>\n'
                f'Размер файла не должен превышать <b>1мб</b>\n'
                f'Файл не должен содержать русских букв!')
message_enc_msg = (f'Напишите текст, который хотите зашифровать.\n'
                   f'Текст не должен содержать русских букв!')


@bot.message_handler(commands=['start'])
def start(m: types.Message):
    bot.send_message(m.chat.id, start_msg, reply_markup=select_mode_keyboard, parse_mode="html")


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: types.CallbackQuery):
    if call.message:
        if call.data == 'encrypt_message':
            msg = bot.send_message(call.message.chat.id, message_enc_msg, parse_mode="html")
            bot.register_next_step_handler(msg, encrypt_message)
        if call.data == 'encrypt_file':
            msg = bot.send_message(call.message.chat.id, file_enc_msg, parse_mode="html")
            bot.register_next_step_handler(msg, download_user_file)


@bot.message_handler(content_types=['document'])
def download_user_file(message: types.Message):
    file_name = message.document.file_name
    if not file_name.endswith('.txt'):
        msg = bot.send_message(message.chat.id, 'Некорректное расширение файла! Отправьте файл повторно❌')
        bot.register_next_step_handler(msg, download_user_file)
    elif message.document.file_size > 1024 * 1024 * 1024:
        msg = bot.send_message(message.chat.id, 'Файл слишком большой, попробуйте снова❌')
        bot.register_next_step_handler(msg, download_user_file)
    else:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('input.txt', 'wb') as in_file:
            in_file.write(downloaded_file)

        os.system("g++ -o main.exe main.cpp")

        f = open("input.txt").readline()

        memory_usage_before = psutil.Process(os.getpid()).memory_info().rss / 1024.0 / 1024.0

        subprocess.run(["main.exe", f], check=True)

        userInput = f
        key = random_key_generator()
        keySchedule = generate_keys(key)

        start_time = time.time()
        encrypted_data = encrypt_data(userInput, keySchedule)
        encryption_time = time.time() - start_time
        python_enc_time = f'Py | Encryption Time: {encryption_time:.6f} seconds'
        with open('python_text_files/py_enc.txt', 'w', encoding='utf-8') as py_enc_file:
            py_enc_file.write(encrypted_data[1])

        start_time = time.time()
        decrypted_data = decrypt_data(encrypted_data[0], len(userInput), keySchedule)
        decryption_time = time.time() - start_time
        python_dec_time = f'Py | Decryption Time: {decryption_time:.6f} seconds'
        with open('python_text_files/py_dec.txt', 'w', encoding='utf-8') as py_dec_file:
            py_dec_file.write(decrypted_data)

        memory_usage_after = psutil.Process(os.getpid()).memory_info().rss / 1024.0 / 1024.0
        memory_usage = memory_usage_after - memory_usage_before
        py_mem_usage = f'Py | Memory Usage: {memory_usage} MB'

        py_enc = open('python_text_files/py_enc.txt', 'rb')
        cpp_enc = open('cpp_text_files/cpp_enc.txt', 'rb')
        py_dec = open('python_text_files/py_dec.txt', 'rb')
        cpp_dec = open('cpp_text_files/cpp_dec.txt', 'rb')

        with open('cpp_text_files/cpp_enc_time.txt', 'r', encoding='utf-8') as cpp_enc_time_file:
            cpp_enc_time = '💻С++ | Encryption Time: ' + cpp_enc_time_file.read() + ' seconds'
        with open('cpp_text_files/cpp_dec_time.txt', 'r', encoding='utf-8') as cpp_dec_time_file:
            cpp_dec_time = '💻С++ | Decryption Time: ' + cpp_dec_time_file.read() + ' seconds'
        with open('cpp_text_files/cpp_mem_usage.txt', 'r', encoding='utf-8') as cpp_mem_usage_file:
            cpp_mem_usage = '💻С++ | Memory usage: ' + cpp_mem_usage_file.read()

        full_msg = cpp_mem_usage + '\n\n' + '🐍' + py_mem_usage

        bot.send_document(message.chat.id, py_enc, caption='🐍' + python_enc_time)
        bot.send_document(message.chat.id, cpp_enc, caption=cpp_enc_time)
        bot.send_document(message.chat.id, py_dec, caption='🐍' + python_dec_time)
        bot.send_document(message.chat.id, cpp_dec, caption=cpp_dec_time)
        bot.send_message(message.chat.id, full_msg)


def encrypt_message(m):
    flag = True
    for i in range(len(m.text)):
        if m.text[i] in excluded_alphabet:
            flag = False
            break
    if not flag:
        msg = bot.send_message(m.chat.id, 'Сообщение содержит русские буквы! Введите повторно❌')
        bot.register_next_step_handler(msg, encrypt_message)
    else:
        with open('input.txt', 'w', encoding='utf-8') as user_input:
            user_input.write(m.text)
        user_input.close()
        os.system("g++ -o main.exe main.cpp")

        f = open("input.txt").readline()

        memory_usage_before = psutil.Process(os.getpid()).memory_info().rss / 1024.0 / 1024.0

        subprocess.run(["main.exe", f], check=True)

        userInput = f
        key = random_key_generator()
        keySchedule = generate_keys(key)

        start_time = time.time()
        encrypted_data = encrypt_data(userInput, keySchedule)
        encryption_time = time.time() - start_time

        start_time = time.time()
        decrypted_data = decrypt_data(encrypted_data[0], len(userInput), keySchedule)
        decryption_time = time.time() - start_time

        memory_usage_after = psutil.Process(os.getpid()).memory_info().rss / 1024.0 / 1024.0
        memory_usage = memory_usage_after - memory_usage_before

        cpp_enc_time = open('cpp_text_files/cpp_enc_time.txt', 'r', encoding="utf-8").read()
        cpp_enc_data = open('cpp_text_files/cpp_enc.txt', 'r', encoding="utf-8", errors="ignore").read()
        cpp_dec_time = open('cpp_text_files/cpp_dec_time.txt', 'r', encoding="utf-8").read()
        cpp_dec_data = open('cpp_text_files/cpp_dec.txt', 'r', encoding="utf-8", errors="ignore").read()
        cpp_mem_usage = open('cpp_text_files/cpp_mem_usage.txt', 'r', encoding='utf-8').read()

        py_msg = (f'⏭️⏱️Py | Encryption Time: {encryption_time:.6f} seconds\n\n'
                  f'🐍Py | AES Encryption: {formatting.hcode(encrypted_data[1])}\n\n'
                  f'⏮️⏱️Py | Decryption Time: {decryption_time:.6f} seconds\n\n'
                  f'🐍Py | AES Decryption: {formatting.hcode(decrypted_data)}\n\n'
                  f'📈Py | Memory Usage: {memory_usage} MB')

        cpp_msg = (f'⏭️⏱️С++ | Encryption time: {cpp_enc_time} seconds\n\n'
                   f'💻С++ | AES Encryption: {formatting.hcode(cpp_enc_data)}\n\n'
                   f'⏮️⏱️С++ | Decryption Time: {cpp_dec_time} seconds\n\n'
                   f'💻С++ | AES Decryption: {formatting.hcode(cpp_dec_data)}\n\n'
                   f'📈С++ | Memory usage: {cpp_mem_usage} MB')

        bot.send_message(m.chat.id, py_msg, parse_mode='html')
        bot.send_message(m.chat.id, cpp_msg, parse_mode='html')


def main():
    if bot.polling(none_stop=True):
        print('Bot started successfully!')
    print('Application ended')


if __name__ == '__main__':
    main()
