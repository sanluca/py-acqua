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
import os
import ConfigParser
import app
import utils
from pysqlite2 import dbapi2 as sqlite


DSCHEDE_DIR = os.path.join (utils.HOME_DIR, "schede")
print "DSCHEDE at: %s" % DSCHEDE_DIR

# creiamo la dir ~/.pyacqua/schede dove conterrà il database delle schede
if not os.path.exists (DSCHEDE_DIR):
	os.mkdir (DSCHEDE_DIR)
	print "creo la dir"
else: 
	print "gia presente"

# ora creiamo il database se non esiste
db_schede = os.path.join (DSCHEDE_DIR, "database_schede")
if not os.path.exists (db_schede):
	connessione=sqlite.connect(db_schede)
	cursore=connessione.cursor()
	cursore.execute("create table pesci_dolce(id integer, vasca TEXT)")
	cursore.execute("create table piante_dolce(id integer, date DATE)")
	cursore.execute("create table invertebrati_dolce(id integer, date DATE)")
	cursore.execute("create table pesci_marino(id integer, date DATE)")
	cursore.execute("create table piante_marino(id integer, date DATE)")
	cursore.execute("create table invertebrati_marino(id integer,date DATE)")
	connessione.commit()
else:
	print "il database_schede esiste gia"
		
class database(gtk.Window):
	__name__ = "Database"
	__desc__ = "Plugin per Database"
	__ver__ = "0.0.1"
	__author__ = "PyAcqua team"
	__preferences__ = {}

	def __init__(self):
		gtk.Window.__init__ (self)
		self.create_gui ()
		self.set_title(_("Database"))
		self.set_size_request (600, 400)
		utils.set_icon (self)

	def start (self):
		print ">> Starting", self.__name__
		
		menu = app.App.get_plugin_menu ()

		self.item = gtk.MenuItem ("Database")
		self.item.connect ('activate', self.on_activated)
		self.item.show ()
		
		menu.append (self.item)
	def create_gui (self):
	
		box = gtk.VBox()
		#box.set_spacing(4)
		#box.set_border_width(4)
		
		# I due frame
		f1 = gtk.Frame(_('Menu')); f2 = gtk.Frame(_('Tipo'))
		
		# Pacchiamoli...
		box.pack_start(f1, False, False, 0)
		box.pack_start(f2, False, False, 0)
		
		
		
		## creo il combo per il tipo del database
		self.cmb = utils.Combo ()
		self.cmb.append_text (_("Pesci Dolce"))
		self.cmb.append_text (_("Piante Dolce"))
		self.cmb.append_text (_("Invertebrati Dolce"))
		self.cmb.append_text (_("Pesci Marino"))
		self.cmb.append_text (_("Piante Marino"))
		self.cmb.append_text (_("Invertebrati Marino"))
		self.cmb.set_active (0)
		self.cmb.connect ('changed', self._on_change_view)
		
		#creo la prima tabella che contiene il combo
		tbl = gtk.Table(1, 2)
		tbl.set_border_width(5)
		
		tbl.attach(self.cmb, 0, 1, 0, 1, yoptions=gtk.SHRINK)
		
		#creo i notebook
		self.notebook = gtk.Notebook()
		#self.notebook.set_show_tabs(False)
		#self.notebook.set_show_border(False)

		## inizio a creare il primo tab che conterra i pesci dolce
		
		tbl1 = gtk.Table(2, 8)
		
		tbl1.attach(utils.new_label(_("Nome 1:")), 0, 1, 0, 1)
		self.nome_pesci_dolce = gtk.Entry()
		tbl1.attach(self.nome_pesci_dolce, 1, 2, 0, 1)
		
		box1 = gtk.VBox()
		box1.pack_start(tbl1, False, False, 0)
		self.notebook.append_page(box1, None)
		
		## secondo tab per la tabella piante dolce
		tbl2 = gtk.Table(2,8)
		tbl2.attach(utils.new_label(_("Nome 2:")), 0, 1, 0, 1)
		self.nome_piante_dolce = gtk.Entry()
		tbl2.attach(self.nome_piante_dolce, 1, 2, 0, 1)
		
		box2 = gtk.VBox()
		box2.pack_start(tbl2, False, False, 0)
		self.notebook.append_page(box2, None)
		
		## terzo tab tabella invertebrati dolce
		tbl3 = gtk.Table(2,8)
		tbl3.attach(utils.new_label(_("Nome 3:")), 0, 1, 0, 1)
		self.nome_piante_dolce = gtk.Entry()
		tbl3.attach(self.nome_piante_dolce, 1, 2, 0, 1)
		
		box3 = gtk.VBox()
		box3.pack_start(tbl3, False, False, 0)
		self.notebook.append_page(box3, None)
		
		## quarto tab tabella pesci marino
		tbl4 = gtk.Table(2,8)
		tbl4.attach(utils.new_label(_("Nome 4:")), 0, 1, 0, 1)
		self.nome_piante_dolce = gtk.Entry()
		tbl4.attach(self.nome_piante_dolce, 1, 2, 0, 1)
		
		box4 = gtk.VBox()
		box4.pack_start(tbl4, False, False, 0)
		self.notebook.append_page(box4, None)
		
		## quinto tab piante marino
		tbl5 = gtk.Table(2,8)
		tbl5.attach(utils.new_label(_("Nome 5:")), 0, 1, 0, 1)
		self.nome_piante_dolce = gtk.Entry()
		tbl5.attach(self.nome_piante_dolce, 1, 2, 0, 1)
		
		box5 = gtk.VBox()
		box5.pack_start(tbl5, False, False, 0)
		self.notebook.append_page(box5, None)
		
		## sesto tab invertebrati marino
		tbl6 = gtk.Table(2,8)
		tbl6.attach(utils.new_label(_("Nome 6:")), 0, 1, 0, 1)
		self.nome_piante_dolce = gtk.Entry()
		tbl6.attach(self.nome_piante_dolce, 1, 2, 0, 1)
		
		box6 = gtk.VBox()
		box6.pack_start(tbl6, False, False, 0)
		self.notebook.append_page(box6, None)
		
		#unisco il tutto......
		f1.add(tbl)
		f2.add(self.notebook)
		
		self.connect ('delete_event', self.exit)
		
		self.add(box)
		
	def _on_change_view(self, widget):
		self.notebook.set_current_page(self.cmb.get_active())
		
	def stop (self):
		print "** Stopping", self.__name__

		self.item.hide ()
		self.item.destroy ()
	
	def on_activated(self, widget):
		self.show_all()
		
	def exit(self, *w):
		self.hide()
		return True # Per non distruggere il contenuto
