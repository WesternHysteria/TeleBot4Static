# TeleBot4Static
Telegram-бот работающий с пакетом [Bird4Static](https://github.com/DennoN-RUS/Bird4Static) и позволяющий управлять списками маршрутизации в режиме чата.

Предполагается что пакет Bird4Static установлен в каталог /opt/root/Bird4Static и работает в режиме "Только пользовательские файлы", пакет IPset4Static в среде Entware и протокол IPv6 на роутере не используются. Работа в других режимах не проверялась.

Для использования Telegram-бота потребуется создать канал для путём обращения к [@BotFather](https://t.me/BotFather) и определить ID или имена пользователей Telegram, которые будут иметь доступ к вашему Telegram-боту.
## Установка
В среде Entware на вашем роутере выполнить следующие команды:
```
opkg install git git-http
cd /opt/root/
git clone https://github.com/WesternHysteria/TeleBot4Static.git
chmod +x TeleBot4Static/*.sh TeleBot4Static/*.py
TeleBot4Static/install.sh
```
и ответить на заданные вопросы. Подробное описание и инструкция об установке находятся [тут]([https://habr.com](https://habr.com/ru/articles/939310/)).
