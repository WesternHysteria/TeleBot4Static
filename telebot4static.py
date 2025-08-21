#!/opt/bin/python3

import os
import re
import subprocess
import time
import telebot
from telebot import types
import telebot4static_config as config

# Определяем текущие рабочие пути.
scriptname = os.path.basename(__file__)
scriptpath = os.path.abspath(__file__)
scriptfolder = os.path.abspath(__file__).replace(scriptname, '')

# Читаем настройки из файла конфигурации
token = config.token
userIDs = config.userIDs
usernames = config.usernames
currentlist = config.vpnlist
autorunfile = config.autorunfile
addroutes = config.addroutes
logenabled = config.logenabled
logfile = config.logfile
detectdoublevpn = config.detectdoublevpn

if logenabled:
    # Загружаем и конфигурируем модуль логирования.
    import logging
    logging.basicConfig(filename = scriptfolder + logfile, format='%(asctime)s (%(module)s:%(lineno)d %(threadName)s) %(levelname)s - %(name)s: %(message)s', datefmt='%d.%m.%Y %H:%M:%S')
    # При запуске создаём новый файл журнала. Существующий журнал при этом затираем.
    fl = open(scriptfolder + logfile, "a")
    fl.close()

# Создаем глобальную переменную при помощи которой будем определять в каком из пунктов меню мы находимся.
menuitem = 0

# Создаем текст сообщения со списком возможных комманд.
helpstub = ("/start - начало работы с ботом и переход в главное меню;\
            \n/add - добавить адреса в список;\
            \n/del - удалить адреса из списка;\
            \n/apply - применить изменения;\
            \n/list - показать список;\
            \n/install - добавить бота в автозапуск;\
            \n/uninstall - удалить бота из автозапуска;")

# Определяем сколько у нас VPN-соединений в системе. Одно или два.
# В зависимости от количества изменяем сообщения и список команд.
if os.path.isfile(detectdoublevpn):
    doublevpn = True
    vpnnumbermessage = "У вас конфигурация с двумя VPN-соединениями."
    # Создаем текст сообщений выводимых при переключениии списков.
    currentlistmessage = "Сейчас вы работаете со списком сайтов открываемых через любой доступный VPN."
    helpstub += ("\n/editvpn - работать со списком сайтов открываемых через любой доступный VPN;\
                \n/editvpn1 - работать со списком сайтов открываемых только через VPN1;\
                \n/editvpn2 - работать со списком сайтов открываемых только через VPN2;")
else:
    doublevpn = False
    vpnnumbermessage = "У вас конфигурация с одним VPN-соединением."
    # Создаем текст сообщений выводимых при переключениии списков.
    currentlistmessage = "Сейчас вы работаете со списком сайтов открываемых через VPN."
    helpstub += ("\n/editvpn - работать со списком сайтов открываемых через VPN;")

helpstub += ("\n/editisp - работать со списком сайтов открываемых напрямую;")

if logenabled:
    helpstub += ("\n/showlog - вывести журнал ошибок;\
                 \n/clearlog - очистить журнал ошибок;")
    
helpstub += ("\n/commands - вывести список команд;\
            \n/help - вывести справку и список комманд.")

# Создаем текст сообщения которое будет отображаться при вводе неверного формата адреса.
addingstub = ('При ДОБАВЛЕНИИ адресов допускается указывать:\
              \n\
              \nDNS-имена:\
              \ndomain.net\
              \nsubdomain.domain.net\
              \n\
              \nIP-адреса и их диапазоны:\
              \n111.22.3.44\
              \n111.22.3.1 - 111.22.4.254\
              \n\
              \nCIDR-подсети и их диапазоны:\
              \n111.22.3.4/25\
              \n11.22.33.0/24 - 11.22.34.0/24\
              \n\
              \nАвтономные системы (ASN):\
              \nAS5361\
              \n\
              \nОднострочные комментарии начинающиеся с символа ; или # :\
              \n#<Это комментарий>\
              \n;И это комментарий\
              \n\
              \nЛюбые адреса могут быть добавлены с указанием позиции:\
              \n10: domain.net\
              \n25: 192.168.12.16/24\
              \n1: #<Проверка VPN>\
              \n\
              \nПри добавлении строки с указанием номера добавляемая строка помещается ПЕРЕД существующей строкой с таким-же номером.\
 Т.е. если вы укажете номера строк 2: и 3: то новые строки будут добавлены ПЕРЕД существующими строками с номерами 2 и 3.\
 Если же вы хотите добавить в список сразу несколько строк подряд, то указывайте для них ОДИН И ТОТ-ЖЕ номер строки. Т.е. 2: и 2: и еще раз 2:\
              \n\
              \nCIDR могут быть заданы либо в формате префикса, либо в формате сетевой маски во всех случаях (включая диапазоны).\
              \n\
              \nРегистр вводимого текста не важен. Пробелы и текст "https://" и "http://" удаляются автоматически.\
              \n\
              \nАдреса и комментарии перед добавлением проверяются на уникальность. Дубликаты не добавляются.\
              \n\
              \nСтроки состоящие только из символов # и ; (в любых комбинациях) считаются строками-разделителями и на уникальность не проверяются.')

removingstub = ('При УДАЛЕНИИ адресов допускается:\
                \n\
                \nУказывать строки целиком:\
                \ndomain.net\
                \n192.168.12.0/24 - 192.168.14.0/24\
                \n#<Строка с комментарием>\
                \n\
                \nУказывать номер строки:\
                \n12:\
                \n46:\
                \n\
                \nВ случае указания в одной строке одновременно и номера строки и имени, например: "23: domain.net", удаление производится по имени.\
                \n\
                \nСтроки-разделители состоящие из комбинаций # и ; удаляются только по номеру строки.')

# Определяем символ определяющий комментарии в списке.
commentsymbol1 = "#"
commentsymbol2 = ";"

# Создаем экземпляр бота.
bot = telebot.TeleBot(token)

#----------------------------------------------------Здесь начинается функция обработки сообщений пользователя------------------------------------------------
# Функция обрабатывающая сообщения от пользователя.
@bot.message_handler(content_types=["text"])
def handle_text(message):
    # Указываем что мы работаем с глобальными переменными.
    global menuitem
    global currentlist
    global currentlistmessage
    global vpnnumbermessage
    # Определяем имя пользователя и его ID.
    userid = message.from_user.id
    username = message.from_user.username
    # Проверяем включено ли имя пользователя или его ID в списки доступа. Если доступ есть, то работаем дальше.
    if (str(userid) in userIDs) or (username in usernames):

        if (message.text.strip() == "В главное меню") or (message.text.strip() == "/start"):
            # Создаем меню управления.       
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Добавить в список")
            item2 = types.KeyboardButton("Удалить из списка")
            item3 = types.KeyboardButton("Применить")
            item4 = types.KeyboardButton("Показать список")
            item5 = types.KeyboardButton("Команды")
            item6 = types.KeyboardButton("Помощь")
            markup.add(item4, item1, item2, item3, item5, item6)
            bot.send_message(message.chat.id, ("Вы находитесь в главном меню."\
                            "\n\n" + vpnnumbermessage+\
                            "\n\n" + currentlistmessage+\
                            "\n\nДля работы с ботом используйте пункты меню или команды управления.\
                            \n\n/help - вывести справку и список команд."), reply_markup=markup)
            # Задаём уровень пункта меню в котором мы находимся.
            menuitem = 0

        elif (message.text.strip() == "Добавить в список") or (message.text.strip() == "/add"):
            bot.send_message(message.chat.id, (vpnnumbermessage + "\n\n" + currentlistmessage + "\n\nВведите адреса для ДОБАВЛЕНИЯ в список. По одному адресу в строку.\n\n/help - вывести справку и список команд."))
            # Задаём уровень пункта меню в котором мы находимся.
            menuitem = 2
           
        elif (message.text.strip() == "Удалить из списка") or (message.text.strip() == "/del"):
            bot.send_message(message.chat.id, (vpnnumbermessage + "\n\n" + currentlistmessage + "\n\nВведите адреса для УДАЛЕНИЯ. По одному адресу в строку.\n\n/help - вывести справку и список команд."))
            # Задаём уровень пункта меню в котором мы находимся.
            menuitem = 3

        elif (message.text.strip() == "Применить") or (message.text.strip() == "/apply"):
            result = ""
            args = [addroutes]
            process = subprocess.Popen(args, stdout = subprocess.PIPE)
            data = process.communicate()
            for line in data:
                if line is not None:
                    outline = line.decode()
                    if (outline.replace(" ","") != "\n") and (outline.replace(" ","") != ""):
                        result += (outline + "\n")
            if result != "":
                bot.send_message(message.chat.id, ("Изменения применены."))
            else:
                bot.send_message(message.chat.id, ("Изменений не найдено."))
            menuitem = 0

        elif (message.text.strip() == "Показать список") or (message.text.strip() == "/list"):
            # Получили команду на вывод текущего списка.
            # Сначала вызываем функцию первичной обработки УЖЕ СУЩЕСТВУЮЩЕГО текущего списка.
            currentlist_array = prepare_current_list(currentlist)
            # Затем формируем список вывода и проверяем пустой он или нет.
            result = ""
            for index, outline in enumerate(currentlist_array, 1):
                result += str(index) + ": " + outline
            if result != "":
                for splited_output in split_text(result):
                    bot.send_message(message.chat.id, splited_output)
            else:
                bot.send_message(message.chat.id, ("Список пуст."))
            # Задаём уровень пункта меню в котором мы находимся.
            menuitem = 0

        elif (message.text.strip() == "/install"):
            autorunexist = False
            if os.path.isfile(autorunfile):
                autorunexist = True
            f = open(autorunfile, "w")
            f.write('#!/bin/sh\n\nENABLED=yes\nPROCS=python3\nARGS=' + scriptpath + '\nPREARGS=""\nDESC="TeleBot4Static"\nPATH=/opt/sbin:/opt/bin:/opt/usr/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\n\n. /opt/etc/init.d/rc.func\n')
            os.chmod(autorunfile, 0o755)
            f.close()
            if autorunexist:
                bot.send_message(message.chat.id, ("Telegram-бот был добавлен в автозагрузку ранее.\nСуществовавшая запись была ПЕРЕЗАПИСАНА."))
            else:
                bot.send_message(message.chat.id, ("Telegram-бот добавлен в автозагрузку."))
            menuitem = 0

        elif (message.text.strip() == "/uninstall"):
            if os.path.exists(autorunfile):
                os.remove(autorunfile)
                bot.send_message(message.chat.id, ("Telegram-бот удален из автозагрузки."))
            else:
                bot.send_message(message.chat.id, ("Telegram-бот не обнаружен в автозагрузке."))
            menuitem = 0

        elif (message.text.strip() == "/editvpn"):
            currentlist = config.vpnlist
            if doublevpn:
                currentlistmessage = "Сейчас вы работаете со списком сайтов открываемых через любой доступный VPN."
            else:
                currentlistmessage = "Сейчас вы работаете со списком сайтов открываемых через VPN."
            bot.send_message(message.chat.id, (currentlistmessage))
            menuitem = 0
            
        elif (message.text.strip() == "/editvpn1") and doublevpn:
            currentlist = config.vpn1list
            currentlistmessage = "Сейчас вы работаете со списком сайтов открываемых ТОЛЬКО через VPN1."
            bot.send_message(message.chat.id, (currentlistmessage))
            menuitem = 0
            
        elif (message.text.strip() == "/editvpn2") and doublevpn:
            currentlist = config.vpn2list
            currentlistmessage = "Сейчас вы работаете со списком сайтов открываемых ТОЛЬКО через VPN2."
            bot.send_message(message.chat.id, (currentlistmessage))
            menuitem = 0
        
        elif (message.text.strip() == "/editisp"):
            currentlist = config.isplist
            currentlistmessage = "Сейчас вы работаете со списком сайтов открываемых НАПРЯМУЮ."
            bot.send_message(message.chat.id, (currentlistmessage))
            menuitem = 0

        elif (message.text.strip() == "/showlog") and logenabled:
            # Открываем файл на чтение. Копируем содержимое файла в переменную. Закрываем файл.
            file = open(scriptfolder + logfile,"r")
            result = file.read()
            file.close
            # Проверяем что в файле содержится хоть что-то, кроме пробелов и символов переноса каретки.
            # Если ничего другого нету, то сообщаем что список пуст. Если есть - то выводим список.
            if (result.replace(" ","")).replace("\n","") == "":
                bot.send_message(message.chat.id, ("Журнал пуст."))
            else:
                for splited_output in split_text(result):
                    bot.send_message(message.chat.id, splited_output)
            # Задаём уровень пункта меню в котором мы находимся.
            menuitem = 0

        elif (message.text.strip()) == "/clearlog" and logenabled:
            # Открываем файл на запись, затирая существующий. Закрываем файл.
            file = open(scriptfolder + logfile,"w")
            file.close
            bot.send_message(message.chat.id, ("Журнал очищен."))

        elif (message.text.strip() == "Команды") or (message.text.strip() == "/commands"):
            bot.send_message(message.chat.id, (helpstub))
            menuitem = 0

        elif (message.text.strip() == "Помощь") or (message.text.strip() == "/help"):
            bot.send_message(message.chat.id, (helpstub))
            bot.send_message(message.chat.id, (addingstub))
            bot.send_message(message.chat.id, (removingstub))
            menuitem = 0

        elif (message.text.strip() != "Добавить в список") and (message.text.strip() != "/add") and (menuitem == 2):
            # Получили сообщение со списком адресов которые необходимо добавить в список. Начинаем его обработку.
            # Сначала вызываем функцию первичной обработки УЖЕ СУЩЕСТВУЮЩЕГО текущего списка.
            currentlist_array = prepare_current_list(currentlist)
            result = ""
            needsavefile = False
            # Объявляем пустой временный список, куда копируем содержимое основного списка до добавления новых элементов.
            # Это необходимо для правильного определения, в какое именно место будем добавлять ту или иную строку,
            # т.к. положение элементов в основном списке будет меняться.
            temp_array = []
            temp_array = currentlist_array.copy()
            temp_string = ""
            temp_index = 0
            # Получаем текст сообщения и преобразуем каждую строку в элемент массива.
            # Затем обрабатываем каждый элемент вновь созданного массива путём переачи в функцию,
            # которая отрезает лишнее и проверяет корректность формата строки.
            addresses_array = message.text.strip().split("\n")
            for source_string in addresses_array:
                processedstring = True
                newaddress, validstring, indexnumber = prepare_current_string(source_string)
                if newaddress != "":
                    # Проверив что строка соответствует заданному шаблону - начинаем её добавление в список.
                    if validstring == True:
                        # Проверяем не существует ли добавляемая строка в массиве из текущего списка.
                        for compareline in currentlist_array:
                            # Проверяем является ли текущая введенная строка разделителем. Т.е. состоящей только из символов # или ;
                            # Если не является, то проверяем была ли эта строка добавлена ранее.
                            # Если же это разделительная строка - то добавляем её безусловно и без поиска дубликатов.
                            if not re.fullmatch('^[#;]+$', newaddress):
                                # Если строка в массиве нашлась, то ставим флаг что её добавлять не надо.
                                if compareline.lower() == (newaddress.lower() + "\n"):
                                    processedstring = False
                        if processedstring == True:
                            # Если указан номер строки и этот номер находится в пределах списка, то добавляем строку с определением позиции.
                            if (indexnumber > 0) and (len(currentlist_array) >= indexnumber):
                                # Начинаем определение позиции для добавления.
                                # Берем копию СУЩЕСТВУЮЩЕГО списка и смотрим, что сейчас содержится в той строке, ПЕРЕД которой мы вставляем новую строку.
                                temp_string = temp_array[indexnumber - 1]
                                # Проверяем, является ли РАЗДЕЛИТЕЛЕМ строка ПЕРЕД которой мы добавляем новую строку.
                                # Если да, то для определения индекса для добавления используем метод подсчёта разделителей.
                                if re.fullmatch('^[#;]+$', temp_string.replace("\n","")):
                                    #bot.send_message(message.chat.id, ("Обнаружена строка-разделитель " + temp_string))
                                    temp_string_number1 = 0
                                    temp_separator_count1 = 0
                                    for item in temp_array:
                                        if re.fullmatch('^[#;]+$', item.replace("\n","")):
                                            temp_separator_count1 += 1
                                        if temp_string_number1 == (indexnumber - 1):
                                            break
                                        temp_string_number1 += 1
                                    #bot.send_message(message.chat.id, ("Номер строки в списке: " + str(temp_string_number1 + 1) + "\nКоличество разделителей: " + str(temp_separator_count1)))
                                    # Дойдя до заданной строки и посчитав количество разделителей ВКЛЮЧАЯ заданную строку,
                                    # начинаем определять место, куда поместить строку в ОБНОВЛЕННОМ списке.
                                    # Для этого перебираем ОБНОВЛЕННЫЙ список и считаем строки-разделители до тех пор,
                                    # пока их количество не сравняется с количеством в СУЩЕСТВУЮЩЕМ списке.
                                    temp_separator_count2 = 0
                                    temp_string_number2 = 0
                                    for item in currentlist_array:
                                        if re.fullmatch('^[#;]+$', item.replace("\n","")):
                                            temp_separator_count2 += 1
                                        if temp_separator_count2 == temp_separator_count1:
                                            break
                                        temp_string_number2 += 1
                                    #bot.send_message(message.chat.id, ("Позиция для размещения строки: " + str(temp_string_number2)))
                                    temp_index = temp_string_number2
                                # Если нет - то для определения индекса для добавления используем метод поиска строки.
                                else:
                                    # Получив содержимое строки, определяем её индекс в ОБНОВЛЁННОМ списке.
                                    temp_index = currentlist_array.index(temp_string)
                                    # Добавляем новую строку ПЕРЕД найденной строкой, по актуальному индексу.
                                currentlist_array.insert(temp_index, newaddress + "\n")
                            # Если нет - то добавляем в конец.
                            else:
                                currentlist_array.append(newaddress + "\n")
                            needsavefile = True
                            bot.send_message(message.chat.id, ("Адрес " + newaddress + " добавлен в список."))
                        else:
                            bot.send_message(message.chat.id, ("Адрес " + newaddress + " был добавлен ранее."))
                    else:
                        bot.send_message(message.chat.id, (newaddress + " - неверный формат адреса!"))
                elif indexnumber > 0:
                    bot.send_message(message.chat.id, (str(indexnumber) + ": - указан номер строки, но не указан адрес!"))    
            # Закончили обработку сообщения. Сохраняем изменения в файл.
            if needsavefile == True:
                for outline in currentlist_array:
                    result += outline
                file = open(currentlist,"w")
                file.write(result)
                file.close()
           
        elif (message.text.strip() != "Удалить из списка") and (message.text.strip()) != "/del" and (menuitem == 3):
            # Получили сообщение со списком адресов которые необходимо удалить из списка. Начинаем его обработку.
            # Сначала вызываем функцию первичной обработки УЖЕ СУЩЕСТВУЮЩЕГО текущего списка.
            currentlist_array = prepare_current_list(currentlist)
            result = ""
            needsavefile = False
            temp_array = []
            temp_indexarray = []
            # Получаем текст сообщения и преобразуем каждую строку в элемент массива.
            # Затем обрабатываем каждый элемент вновь созданного массива путём передачи в функцию,
            # которая отрезает лишнее и проверяет корректность формата строки.
            addresses_array = message.text.strip().split("\n")
            for source_string in addresses_array:
                processedstring = False
                removeaddress, validstring, indexnumber = prepare_current_string(source_string)
                # После того как были проведены первичные проверки и подготовка текста - сформируем список адресов для удаления.
                # При этом будем помнить что удалять мы можем как по полному адресу, так и номеру элемента в списке.
                # Проверяем каждую строку которую нам вернула функция. Если в строке был обнаружен адрес и он корректен, то проверяем его наличие в списке.
                if removeaddress != "":
                    if validstring == True:
                        for compareline in currentlist_array:
                            # Если строка в массиве нашлась, то помещаем эту строку в массив для удаления.
                            if not re.fullmatch('^[#;]+$', removeaddress):
                                if compareline.lower() == (removeaddress.lower() + "\n"):
                                    if temp_indexarray.count(currentlist_array.index(compareline)) == 0:
                                        temp_indexarray.append(currentlist_array.index(compareline))
                                   #if temp_array.count(compareline.replace("\n","")) == 0:
                                   #    temp_array.append(compareline.replace("\n",""))
                                        processedstring = True
                                        needsavefile = True
                        if processedstring == True:
                            bot.send_message(message.chat.id, ("Адрес " + removeaddress + " удалён из списка."))
                        elif (processedstring == False) and (re.fullmatch('^[#;]+$', removeaddress)):
                            bot.send_message(message.chat.id, ("Строка " + removeaddress + " является разделителем и может быть удалена только по номеру строки."))
                        else:
                            bot.send_message(message.chat.id, ("Адрес " + removeaddress + " не найден в списке."))
                    else:
                        bot.send_message(message.chat.id, (removeaddress + " - неверный формат адреса!"))
                elif indexnumber > 0:
                    if len(currentlist_array) >= (indexnumber):
                        indexnumber -= 1

                        removeaddress = (currentlist_array[indexnumber]).replace("\n","")
                        if temp_indexarray.count(indexnumber) == 0:
                            temp_indexarray.append(indexnumber)
                            #currentlist_array[indexnumber] = "!this_separator_must_be_removed!" + "\n"
                            needsavefile = True
                            bot.send_message(message.chat.id, ("Адрес " + removeaddress + " удалён из списка."))
                        else:
                            bot.send_message(message.chat.id, ("Адрес " + removeaddress + " не найден в списке."))
                    else:
                        bot.send_message(message.chat.id, (str(indexnumber) + ": - номер строки не найден в списке!"))
            # Закончили обработку сообщения. Сохраняем изменения.
            if needsavefile == True:
                # Сначала удаляем разделители, т.к. они удаляются по номеру строки.
                temp_indexarray.sort(reverse=True)
                for removingindex in temp_indexarray:
                    currentlist_array.pop(removingindex)
                for outline in currentlist_array:
                    result += outline
                file = open(currentlist,"w")
                file.write(result)
                file.close()

        else:
            bot.send_message(message.chat.id, (helpstub))
            menuitem = 0

    # Если ни имя пользователя, ни его ID в списках доступа не указано, то сообщаем пользователю об этом и выводим служебную информацию.
    else:
        if (username is not None):
            bot.send_message(message.chat.id, ("Я вас категорически приветствую!\nК сожалению, вам сюда нельзя!\nВаше имя: " + username + "\nВаш ID: " + str(userid) +\
                             "\nДля получения доступа сообщите эту информацию владельцу канала."))
        if (username is None):
            bot.send_message(message.chat.id, ("Я вас категорически приветствую!\nК сожалению, вам сюда нельзя!\nВаш ID: " + str(userid) +\
                             "\nДля получения доступа сообщите эту информацию владельцу канала."))

#----------------------------------------------------Здесь заканчивается функция обработки сообщений пользователя---------------------------------------------

#--------------------------------------------Здесь начинается функция считывания и обработки обработки текущего списка----------------------------------------
# Все переменные в этой функции - локальные. Т.е. работают только ВНУТРИ этой функции.
def prepare_current_list(filename):
    currentlist = filename
    currentlist_array = []
    # Открываем текущий список на чтение и читаем каждую его строку в массив.
    file = open(currentlist,"r")
    for inline in file:
        # Проверяем является ли текущая строка комментарием. Если нет - то производим дальнейшую обработку.
        if (inline.replace(" ","")[0] != commentsymbol1) and (inline.replace(" ","")[0] != commentsymbol2):
            # Сперва удаляем из текущей строки все пробелы.
            inline = inline.replace(" ","")
            # Если текущая строка списка это имя автономной системы, то переводим её в ВЕРХНИЙ регистр.
            if re.fullmatch(r'^AS\d+$', (inline.upper().replace("\n",""))):
                inline = inline.upper()
            # Если нет - то переводим строку в НИЖНИЙ регистр.
            else:
                inline = inline.lower()
        # Если строка - комментарий, то отрезаем все лишние пробелы перед символом определяющим комментарий.
        else:
            while (inline[0] != commentsymbol1) and (inline[0] != commentsymbol2):
                inline = inline.replace(" ", "", 1)
        # Проверяем что указанная строка не является состоящей только из символов переноса картетки и добавляем её в массив.
        if inline.replace("\n","") != "":
            if inline[-1] != "\n":
                inline += "\n"
            currentlist_array.append(inline)
     # Закрываем файл с текущим списоком.
    file.close()
    return currentlist_array
#----------------------------------------------Здесь заканчивается функция считывания и обработки текущего списка --------------------------------------------

#--------------------------------------------Здесь начинается функция обработки адресов для добавления/удаления из списка-------------------------------------
# Все переменные в этой функции - локальные. Т.е. работают только ВНУТРИ этой функции.
def prepare_current_string(current_string):
    indexnumber = -1
    address = ""
    # При помощи регулярного выражения проверяем есть ли в начале строки порядковый номер в формате "11: ".
    # И удаляем из текущей строки пробелы и текст "https://" и "http://".
    if re.match(r'^\d+\:', current_string):
        # Если есть, то делим строку на порядковый номер и последующий текст.
        index, address = re.split(r'\:', current_string, maxsplit = 1)
        indexnumber = int(index)
        if indexnumber == 0:
            indexnumber = 1
    else:
        address = current_string
    # Ставим флаги о том, прошла ли текущая строка проверку формата и будем ли мы добавлять текущую строку в список или нет.
    validstring = False
    # Проверяем что указанная строка не является состоящей только из символов переноса картетки.
    if address.replace("\n","") != "":
        if ((address.replace(" ","")[0]) != commentsymbol1) and ((address.replace(" ","")[0]) != commentsymbol2):
            address = address.replace(" ","").replace("https://","").replace("http://","")
            # Проверяем, является ли строка именем автономной системы (AS).
            if re.fullmatch(r'^AS\d+$', (address.upper().replace("\n",""))):
                # Если да - то переводим строку в ВЕРХНИЙ регистр.
                address = address.upper()
                validstring = True
            # Проверяем, является ли строка DNS-именем сайта, IP-адресом, диапазоном IP-адресов, CIDR или диапазоном CIDR.
            elif re.fullmatch(r'^[\w./-]+\.[\w./-]+', (address.lower().replace("\n",""))):
                # если да - то переводим строку в НИЖНИЙ регистр.
                address = address.lower()
                validstring = True
        else:
            while (address[0] != commentsymbol1) and (address[0] != commentsymbol2):
                address = address.replace(" ", "", 1)
            validstring = True
    return (address, validstring, int(indexnumber))
#------------------------------------------Здесь заканчивается функция обработки адресов для добавления/удаления из списка------------------------------------    

#---------------------------------------------Здесь начинается функция разделения большого списка на несколько сообщений--------------------------------------
# Все переменные в этой функции - локальные. Т.е. работают только ВНУТРИ этой функции.
def split_text(text: str, max_chars: int = 4096):
    # Создаём пустой объект типа "список", в который будем помещать наборы многострочных выводов.
    result = []
    # Получаем исходный текст и создаём из него объект типа "массив" путём разбиения списка по строкам.
    text_words = text.split('\n')
    # Создаем временную строковую переменную, которую делаем равной первому (индекс 0) элементу массива.
    temp = text_words[0]
    # Перебираем все объекты в массиве начиная с второго (индекс 1) и для каждого проделываем следующие действия:
    for word in text_words[1:]:
        # Проверяем какой будет длина временной строки, если к уже существующей строке добавить следующий элемент массива.
        # Если длина строки меньше максимального размер текстового сообщения в Telegram (на текущий момент 4096 символов),
        if len(temp + '\n' + word) < max_chars:
            # то добавляем элемент массива к текущей временной строке.
            temp += f'\n{word}'
        # Если же длина временной строки будет превышать максимально допустимый размер,
        else:
            # то записываем всю временную строку как очередной элемент существующего списка
            # и заменяем всю временную строку на значение которое не влезло, тем самым начиная формировать следующую строку.
            result.append(temp)
            temp = word
    # После окончания обработки массива, помещаем в существующий спискок всё то что не было подано в список в ходе предыдущего цикла.
    result.append(temp)
    # Подаём сформированный список на выход функции.
    # Не забываем что в получнном на выходе списке может быть несколько элементов,
    # поэтому для вывода всего содержимого будет требоваться циклический перебор всех элементов списка.
    return result
#---------------------------------------------Здесь заканчивается функция разделения большого списка на несколько сообщений------------------------------------

# Проверяем включено ли ведение лога и запускаем бота.
if logenabled:
    try:
        bot.infinity_polling()
    except Exception as err:
        logging.exception(err)
        time.sleep(20)
else:
    bot.infinity_polling()