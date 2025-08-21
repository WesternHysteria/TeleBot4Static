#!/bin/sh

VERSION="v1.0.0"

#Setting paths.
ABSOLUTE_FILENAME=`readlink -f "$0"`
CURRENT_FOLDER=`dirname "$ABSOLUTE_FILENAME"`
TELEBOT_PATH=$CURRENT_FOLDER/telebot4static.py
CONFIG_PATH=$CURRENT_FOLDER/telebot4static_config.py
AUTORUN_PATH=/opt/etc/init.d/S99telebot4static

while :; do
  if test -f $CONFIG_PATH; then echo -e '\033[1;91m\nExisting configuration files will be overwritten!\033[0m'; fi
  echo -e '\033[1;92mContinue installation? y/n\033[0m'
  read yn
  case $yn in
    [Yy] )
      break
    ;;
    [Nn] )
      exit 0
    ;;
    * )
      echo -e '\033[1;91mPlease answer y(yes) or n(no).\033[0m'
    ;;
  esac
done
yn=""

if test -e $CURRENT_FOLDER/.git; then rm -r $CURRENT_FOLDER/.git; fi
if test -e $CURRENT_FOLDER/__pycache__; then rm -r $CURRENT_FOLDER/__pycache__; fi

#Setting variables.
while :; do
  echo -e '\033[1;92m\nEnter Telegram-bot token:\033[0m'
  read TOKEN
    if echo $TOKEN | grep -iE "^[[:digit:]]+:\S+$" >/dev/null; then
      break
    else
      echo -e '\033[1;91mIncorrect token!\033[0m'
    fi
done


#Adding user IDs.
while :; do
  echo -e '\033[1;92m\nDo you want to add user IDs to the configuration file? y/n\033[0m'
  read yn
  case $yn in
    [Yy] )
      echo -e '\033[1;92m\nEnter user IDs one at a time. To finish adding, enter a \033[1;93mblank line.\033[0m'
      while :; do
        read ID
        if [[ -z $ID ]]; then break; fi
          if echo $ID | grep -iE "^[[:digit:]]+$" >/dev/null; then
            if [[ -z $USERIDS ]]; then
              USERIDS='"'$ID'"'
            else
              USERIDS=$USERIDS',"'$ID'"'
            fi
          else
            echo -e '\033[1;91mIncorrect user ID!\033[0m'
          fi
      done
      break
    ;;
    [Nn] )
      break
    ;;
    * )
      echo -e '\033[1;91mPlease answer y(yes) or n(no).\033[0m'
    ;;
  esac
done
if [[ -z $USERIDS ]]; then
  USERIDS='""'
else
  echo -e "\033[1;93mThese user IDs will be added to the configuration file: $USERIDS\033[0m"
fi
yn=""

#Adding usernames.
while :; do
  echo -e '\033[1;92m\nDo you want to add usernames to the configuration file? y/n\033[0m'
  read yn
  case $yn in
    [Yy] )
      echo -e '\033[1;92m\nEnter usernames \033[1;93mwithout @ symbol \033[1;92mone at a time. To finish adding, enter a \033[1;93mblank line.\033[0m'
      while :; do
        read NAME
        if [[ -z $NAME ]]; then break; fi
        if echo $NAME | grep -iE "^[a-zA-Z0-9_]+$" >/dev/null; then
          if [[ -z $USERNAMES ]]; then
            USERNAMES='"'$NAME'"'
          else
            USERNAMES=$USERNAMES',"'$NAME'"'
          fi
        else
          echo -e '\033[1;91mIncorrect username!\033[0m'
        fi
      done
      break
    ;;
    [Nn] )
      break
    ;;
    * )
      echo -e '\033[1;91mPlease answer y(yes) or n(no).\033[0m'
    ;;
  esac
done
if [[ -z $USERNAMES ]]; then
  USERNAMES='""'
else
  echo -e "\033[1;93mThese usernames will be added to the configuration file: $USERNAMES\033[0m"
fi

#Install packages.
opkg update && opkg install python3 python3-pip
pip install --upgrade pip certifi charset-normalizer idna requests setuptools urllib3 pkgconfig pyTelegramBotAPI==4.27

#Create configuration file.
echo -e '#!/opt/bin/python3' > $CONFIG_PATH
echo -e '\n#Telegram bot token.' >> $CONFIG_PATH
echo -e "token = "'("'$TOKEN'")' >> $CONFIG_PATH
echo -e '\n#Access allowed.' >> $CONFIG_PATH
echo -e 'userIDs = ['$USERIDS']' >> $CONFIG_PATH
echo -e 'usernames = ['$USERNAMES']' >> $CONFIG_PATH
echo -e '\n#Error log.' >> $CONFIG_PATH
echo -e 'logenabled = False' >> $CONFIG_PATH
echo -e 'logfile = "errors.log"' >> $CONFIG_PATH
echo -e '\n#Autorun file.' >> $CONFIG_PATH
echo -e 'autorunfile = "'$AUTORUN_PATH'"' >> $CONFIG_PATH
echo -e '\n#Bird4Static file paths.' >> $CONFIG_PATH
echo -e 'detectdoublevpn = "/opt/etc/bird4-force-vpn2.list"' >> $CONFIG_PATH
echo -e 'addroutes = "/opt/root/Bird4Static/scripts/add-bird4_routes.sh"' >> $CONFIG_PATH
echo -e 'isplist = "/opt/root/Bird4Static/lists/user-isp.list"' >> $CONFIG_PATH
echo -e 'vpnlist = "/opt/root/Bird4Static/lists/user-vpn.list"' >> $CONFIG_PATH
echo -e 'vpn1list = "/opt/root/Bird4Static/lists/user-vpn1.list"' >> $CONFIG_PATH
echo -e 'vpn2list = "/opt/root/Bird4Static/lists/user-vpn2.list"' >> $CONFIG_PATH

#Create autorun file.
echo '#!/bin/sh' > $AUTORUN_PATH
echo -e "\nENABLED=yes" >> $AUTORUN_PATH
echo 'PROCS=python3' >> $AUTORUN_PATH
echo "ARGS=$TELEBOT_PATH" >> $AUTORUN_PATH
echo 'PREARGS=""' >> $AUTORUN_PATH
echo 'DESC="TeleBot4Static"' >> $AUTORUN_PATH
echo 'PATH=/opt/sbin:/opt/bin:/opt/usr/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin' >> $AUTORUN_PATH
echo -e "\n. /opt/etc/init.d/rc.func" >> $AUTORUN_PATH
chmod +x $AUTORUN_PATH
$AUTORUN_PATH restart

#Run update script.
$CURRENT_FOLDER/update.sh
