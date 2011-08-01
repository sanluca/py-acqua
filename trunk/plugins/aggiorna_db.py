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
import impostazioni
import utils

class DbEntry (utils.FileEntry):
	def __init__ (self):
		utils.FileEntry.__init__ (self)

	def callback (self, widget):
		filter = gtk.FileFilter ()
		filter.set_name (_("PyAcqua Databases"))

		filter.add_pattern ("db")
		ret = utils.FileChooser (_("Seleziona Database"), None, filter, False).run ()

		if ret != None:
			self.set_text (ret)

class aggiorna_db(gtk.Window):
	__name__ = "AgDB"
	__desc__ = "Aggiornamento database"
	__ver__ = "0.0.1"
	__author__ = "PyAcqua team"
	__preferences__ = {}

	def __init__(self):
		gtk.Window.__init__ (self)
		self.create_gui ()
		self.set_title(_("AgDB Plugin"))
		#self.set_size_request (600, 400)
		utils.set_icon (self)

	def start (self):
		print ">> Starting", self.__name__
		
		print ">> AgDB.. showtips :", impostazioni.get("show_tips")
		
		if impostazioni.get("dummy_nervose_mode"):
			print prova
		
		menu = app.App.get_plugin_menu ()

		self.item = gtk.MenuItem ("AgDB Plugin")
		self.item.connect ('activate', self.on_activated)
		self.item.show ()

		menu.append (self.item)

	def stop (self):
		print "** Stopping", self.__name__

		self.item.hide ()
		self.item.destroy ()
	
	
	def on_activated(self, widget):
		self.show_all()
		print "clicked"
	
	def exit (self, *w):
		self.hide ()
	
	def create_gui (self):
		# Qui viene costruita la gui
		vbox = gtk.VBox()
		vbox.set_spacing(4)
		vbox.set_border_width(4)
		
		tbl = gtk.Table(2, 4)
		tbl.set_border_width(4)
		tbl.set_row_spacings(4)
		
		tbl.attach(utils.new_label(_('Inserisci')), 0, 1, 0, 1, xoptions=gtk.SHRINK)
		
		self.importa_db = DbEntry ()
		
		tbl.attach(self.importa_db, 2, 3, 0, 1, xoptions=gtk.SHRINK)
		
		bb = gtk.HButtonBox()
		bb.set_layout(gtk.BUTTONBOX_END)
		
		btn = gtk.Button(stock=gtk.STOCK_OK)
		btn.connect('clicked', self.updatedb)
		bb.pack_start(btn)
		
		btn = gtk.Button(stock=gtk.STOCK_CANCEL)
		btn.connect('clicked', self.exit)
		bb.pack_start(btn)
		
		tbl.attach (bb, 0, 2, 3, 4, ypadding=4)
		
		self.add (tbl)
	
	def updatedb (self):
		connessione=sqlite.connect (utils.DATA_DIR, "db")
		cursore=connessione.cursor ()

		def check (query):
			try:
				cursore.execute (query)
			except:
				print "Errore nella query (%s)" % query

		###################################
		# Versione 0.7
		
		check ("create table spesa(id integer, vasca TEXT, date DATE, tipologia TEXT, nome TEXT, quantita NUMERIC, prezzo TEXT, img TEXT)")
		check ("create table invertebrati(id integer, date DATE, vasca FLOAT, quantita NUMERIC, nome TEXT, img TEXT)")
		check ("alter table vasca add reattore TEXT")
		check ("alter table vasca add schiumatoio TEXT")
		check ("alter table vasca add riscaldamento TEXT")
		check ("alter table test add vasca FLOAT")
		check ("alter table test add calcio FLOAT")
		check ("alter table test add magnesio FLOAT")
		check ("alter table test add densita FLOAT")
		
		###################################
		# Versione 1.0

		check ("alter table vasca add note VARCHAR(500)")
		check ("create table spesa(id integer, vasca TEXT, date DATE, tipologia TEXT, nome TEXT, quantita NUMERIC, soldi TEXT, note VARCHAR(500), img TEXT)")
		check ("alter table pesci add note VARCHAR(500)")
		check ("alter table piante add note VARCHAR(500)")
		check ("alter table invertebrati add note VARCHAR(500)")
		check ("alter table fertilizzante add note VARCHAR(500)")
		check ("alter table filtro add note VARCHAR(500)")
		check ("create table manutenzione(id integer, vasca TEXT, data DATE, tipo TEXT, nome TEXT, quantita TEXT, giorni DATE, note VARCHAR(500)")
		connessione.commit ()
