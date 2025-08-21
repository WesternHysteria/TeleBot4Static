#Updating all packeges.
echo -e '\033[1;92m\nDo you want to update all packages? y/n\033[0m'
echo -e '\033[1;91mWARNING!!! This can take a very long time!\033[0m'
while :; do
  read yn
  case $yn in
    [yY] )
      opkg update && opkg upgrade
	  opkg install python3-dev
      opkg install gcc
      PIPOUTDATED=$(pip list --outdated | sed 1,2d | awk '{print $1}' | tr '\n' ' ')
      if [[ ! -z $PIPOUTDATED ]]; then pip install --upgrade $(echo $PIPOUTDATED); fi
      /opt/etc/init.d/S99telebot4static restart
      break ;;
    [nN] )
      break ;;
    * )
      echo -e "\033[1;91mPlease answer y(yes) or n(no).\033[0m";;
  esac
done

