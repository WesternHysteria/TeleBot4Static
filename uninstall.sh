#!/bin/sh

#Setting paths.
ABSOLUTE_FILENAME=`readlink -f "$0"`
CURRENT_FOLDER=`dirname "$ABSOLUTE_FILENAME"`
AUTORUN_PATH=/opt/etc/init.d/S99telebot4static

while :; do
  echo -e '\033[1;91mContinue uninstallation? y/n\033[0m'
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

#Remove TeleBot4Static service
if test -f $AUTORUN_PATH; then
  $AUTORUN_PATH stop
  rm $AUTORUN_PATH
fi

#Remove packages
#pip
answer=n; echo "Do you want remove 'pip and all pip packages'? y(yes)/n(no) (default: no)"; read answer
if [ "$answer" = "y" ]; then
  if which pip > /dev/null; then
	pip cache purge
    PIPPACKAGES=$(pip list | sed 1,2d | sed '/pip/d' | awk '{print $1}' | tr '\n' ' ')
    pip uninstall $(echo ${PIPPACKAGES}) -y
    opkg remove python3-pip
  fi
fi
#gcc
answer=n; echo "Do you want remove 'gcc'? y(yes)/n(no) (default: no)"; read answer
if [ "$answer" = "y" ]; then
  opkg remove gcc
fi
#python
answer=n; echo "Do you want remove 'python'? y(yes)/n(no) (default: no)"; read answer
if [ "$answer" = "y" ]; then
  opkg --force-removal-of-dependent-packages remove python3-pip python3-dev python3
fi

#Remove TeleBot4Static files
rm -r $CURRENT_FOLDER