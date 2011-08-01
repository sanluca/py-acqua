#!/bin/sh

rm -f *.so *.o

gcc -c -fPIC `pkg-config --cflags gtk+-2.0 pygtk-2.0` -I/usr/local/include/python2.4 eggtrayicon.c
gcc -c -fPIC `pkg-config --cflags gtk+-2.0 pygtk-2.0` -I/usr/local/include/python2.4 trayicon.c
gcc -c -fPIC `pkg-config --cflags gtk+-2.0 pygtk-2.0` -I/usr/local/include/python2.4 trayiconmodule.c
gcc -shared -o trayicon.so -fPIC eggtrayicon.o trayicon.o trayiconmodule.o `pkg-config --libs gtk+-2.0`

# all'ultimo va linkato alle gtk
