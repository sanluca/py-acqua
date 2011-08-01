#!/usr/bin/env python
# -*- coding: iso-8859-15 -*- 
#Copyright (C) 2005, 2008 Py-Acqua
#http://www.pyacqua.net
#email: info@pyacqua.net  
#
#   
#Py-Acqua is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#Py-Acqua is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Py-Acqua; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import app
import gtk
import os
import gobject

def quit_cb(widget, data = None):
	if data:
		data.set_visible(False)
	gtk.main_quit()
 
def popup_menu_cb(widget, button, time, data = None):
	if button == 3:
		menu.popup (None, None, None, button, time)
		menu.show_all ()
 
def app_show(widget, data = None):
	app.App.show ()	
def app_hide(widget, data = None):
	app.App.hide()
	
statusIcon = gtk.StatusIcon()	
menu = gtk.Menu()
menuItem = gtk.ImageMenuItem("Mostra PyAcqua")
menuItem.connect('activate', app_show, statusIcon)
menu.append(menuItem)
menuItem = gtk.ImageMenuItem("Nascondi PyAcqua")
menuItem.connect('activate', app_hide, statusIcon)
menu.append(menuItem)
menuItem = gtk.ImageMenuItem(gtk.STOCK_QUIT)
menuItem.connect('activate', quit_cb, statusIcon)
menu.append(menuItem)