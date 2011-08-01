#!/usr/bin/env python
# -*- coding: iso-8859-15 -*- 
#Copyright (C) 2005, 2007 Py-Acqua
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



import gtk
import app
import utils

class calcolatrice(gtk.Window):
	__name__ = "Calcolatrice"
	__desc__ = "Plugin per Py-Acqua"
	__ver__ = "0.0.1"
	__author__ = "PyAcqua team"
	__preferences__ = {}

	def __init__(self):
		gtk.Window.__init__ (self)
		self.create_gui ()
		self.set_title(_("PyCalc"))
		self.set_size_request (400, 200)
		utils.set_icon (self)

	def start (self):
		print ">> Starting", self.__name__
		
		menu = app.App.get_plugin_menu ()

		self.item = gtk.MenuItem ("Calcolatrice")
		self.item.connect ('activate', self.on_activated)
		self.item.show ()

		menu.append (self.item)
		
	def create_gui (self):
		# Qui viene costruita la gui
		box = gtk.VBox()
		box.set_spacing(4)
		box.set_border_width(4)
		
		tbl = gtk.Table(4, 6)
		tbl.set_border_width(5)

		self.risultato = gtk.Entry ()
		tbl.attach(self.risultato, 0, 1, 0, 1, yoptions=gtk.SHRINK)
		
		self.ce = gtk.Button('CE')
		#self.sempre.connect("clicked", self.prova1)
		tbl.attach(self.ce, 0, 1, 1, 2, xoptions=gtk.SHRINK)
		
		self.sette = gtk.Button('7')
		tbl.attach(self.sette, 0, 1, 2, 3, xoptions=gtk.SHRINK)
		
		self.otto = gtk.Button('8')
		tbl.attach(self.otto, 1, 2, 2, 3, xoptions=gtk.SHRINK)
		
		self.nove = gtk.Button('9')
		tbl.attach(self.nove, 2, 3, 2, 3, xoptions=gtk.SHRINK)
		
		self.diviso = gtk.Button('/')
		tbl.attach(self.diviso, 3, 4, 2, 3, xoptions=gtk.SHRINK)
		
		self.quattro = gtk.Button('4')
		tbl.attach(self.quattro, 0, 1, 3, 4, xoptions=gtk.SHRINK)
		
		self.cinque = gtk.Button('5')
		tbl.attach(self.cinque, 1, 2, 3, 4, xoptions=gtk.SHRINK)
		
		self.sei = gtk.Button('6')
		tbl.attach(self.sei, 2, 3, 3, 4, xoptions=gtk.SHRINK)
		
		self.per = gtk.Button('X')
		tbl.attach(self.per, 3, 4, 3, 4, xoptions=gtk.SHRINK)
		
		self.uno = gtk.Button('1')
		tbl.attach(self.uno, 0, 1, 4, 5, xoptions=gtk.SHRINK)
		
		self.due = gtk.Button('2')
		tbl.attach(self.due, 1, 2, 4, 5, xoptions=gtk.SHRINK)
		
		self.tre = gtk.Button('3')
		tbl.attach(self.tre, 2, 3, 4, 5, xoptions=gtk.SHRINK)
		
		self.meno = gtk.Button('-')
		tbl.attach(self.meno, 3, 4, 4, 5, xoptions=gtk.SHRINK)
		
		self.zero = gtk.Button('0')
		tbl.attach(self.zero, 0, 1, 5, 6, xoptions=gtk.SHRINK)
		
		self.virgola = gtk.Button(',')
		tbl.attach(self.virgola, 1, 2, 5, 6, xoptions=gtk.SHRINK)
		
		self.uguale = gtk.Button('=')
		tbl.attach(self.uguale, 2, 3, 5, 6, xoptions=gtk.SHRINK)
		
		self.piu = gtk.Button('+')
		tbl.attach(self.piu, 3, 4, 5, 6, xoptions=gtk.SHRINK)
		
		box.pack_start(tbl)
		self.add(box)
		
		self.connect ('delete_event', self.exit)
		
		self.number = 0
	
	def on_num_pressed (self, widget):
		self.number = self.number * 10
		self.number += int (widget.get_label ())
		self.risultato.set_text (self.risultato.get_text () + widget.get_label ())

	def stop (self):
		print "** Stopping", self.__name__

		self.item.hide ()
		self.item.destroy ()
	
	def on_activated(self, widget):
		self.show_all()
		
	def exit(self, *w):
		self.hide()
		return True # Per non distruggere il contenuto
