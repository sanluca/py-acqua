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

import sys
	
try:
	import pygtk
	pygtk.require ('2.0')
except:
	print "!! PyGtk Not present"
	sys.exit (-1)

import os
os.environ['PATH'] += r";lib;etc;bin;"

if os.name == "nt":
	os.environ['MATPLOTLIBDATA'] = os.getcwd () + "\\matplotlibdata"
else:
	if os.environ.has_key ('PYTHONPATH'):
		os.environ['PYTHONPATH'] += r";eggmini"
	else:
		os.environ['PYTHONPATH'] = r";eggmini"

import locale
import gettext

try:
	# Richiediamo gtk2
	import gtk
	import gobject
except:
	print "You need to install GTKv2"
	sys.exit (-1)

try:
	#import pysqlite2 as sqlite
	from pysqlite2 import dbapi2 as sqlite
except:
	print "You need to install pysqlite"
	sys.exit (-1)

import utils
import app
import engine
import merger
import impostazioni
import backend
import tray
import alert

def main ():
	APP = 'acqua'
	if os.name == 'nt':
		DIR = os.path.join (utils.DHOME_DIR, "locale")
	else:
		DIR = os.path.join (utils.PROG_DIR, "locale")
	
	try:
		
		if impostazioni.get ("lang").lower () == "en":
			en = gettext.translation (APP, DIR, ["en"])
			en.install ()
			try:
				os.environ['LANG'] = "en_US"
				locale.setlocale (locale.LC_MESSAGES, "en_US")
			except: pass
		elif impostazioni.get ("lang").lower () == "fr":
			fr = gettext.translation (APP, DIR, ["fr"])
			fr.install ()
			try:
				os.environ['LANG'] = "fr_FR"
				locale.setlocale (locale.LC_MESSAGES, "fr_FR")
			except: pass
		else:
			# In teoria qui risulta inutile settare. Il linguaggio italiano e' di default senza gettext.
			os.environ['LANG'] = "it_IT"
			it = gettext.translation (APP, DIR, [])
			it.install ()

	except (IOError, locale.Error), e:
		print "(%s): WARNING **: %s" % (APP, e)
		__builtins__.__dict__["_"] = gettext.gettext
	
	path = os.path.join (utils.DATA_DIR, "db")
	db = backend.get_backend_class ()(path)
	
	if not db.get_schema_presents ():
		t = backend.ColumnType

		db.create_table (
			"vasca",
			[
				"id", "vasca", "date", "nome", "litri", "tipo", "filtro", "co",
				"illuminazione", "reattore", "schiumatoio", "riscaldamento", "note", "img"
			
			],
			[
				t.INTEGER, t.TEXT, t.DATE, t.TEXT, t.FLOAT, t.TEXT, t.TEXT, t.TEXT,
				t.TEXT, t.TEXT, t.TEXT, t.TEXT, t.VARCHAR + 500, t.TEXT
			]
		)

		db.create_table (
			"test",
			[
				"id", "date", "vasca", "ph", "kh", "gh", "no", "noo", "con",
				"amm", "fe", "ra", "fo", "calcio", "magnesio", "densita", "limiti"
			],
			[
				t.INTEGER, t.DATE, t.TEXT, t.FLOAT, t.FLOAT, t.FLOAT, t.FLOAT,
				t.FLOAT, t.FLOAT, t.FLOAT, t.FLOAT, t.FLOAT, t.FLOAT, t.FLOAT,
				t.FLOAT, t.FLOAT, t.TEXT
			]
		)

		db.create_table (
			"pesci",
			[
				"id", "date", "vasca", "quantita", "nome", "note", "img"
			],
			[
				t.INTEGER, t.DATE, t.FLOAT, t.NUMERIC, t.TEXT, t.VARCHAR + 500, t.TEXT
			]
		)

		db.create_table (
			"invertebrati",
			[
				"id", "date", "vasca", "quantita", "nome", "note", "img"
			],
			[
				t.INTEGER, t.DATE, t.FLOAT, t.NUMERIC, t.TEXT, t.VARCHAR + 500, t.TEXT
			]
		)

		db.create_table (
			"piante",
			[
				"id", "date", "vasca", "quantita", "nome", "note", "img"
			],
			[
				t.INTEGER, t.DATE, t.FLOAT, t.NUMERIC, t.TEXT, t.VARCHAR + 500, t.TEXT
			]
		)
		
		db.create_table (
			"fertilizzante",
			[
				"id", "date", "nome", "quantita", "giorni", "note"
			],
			[
				t.INTEGER, t.DATE, t.TEXT, t.FLOAT, t.NUMERIC, t.VARCHAR + 500
			]
		)
		
		db.create_table (
			"spesa",
			[
				"id", "vasca", "data", "tipologia", "nome", "quantita", "soldi",
				"note", "img"
			],
			[
				t.INTEGER, t.TEXT, t.DATE, t.TEXT, t.TEXT, t.NUMERIC, t.TEXT,
				t.VARCHAR + 500, t.TEXT 
			]
		)
		
		db.create_table (
			"filtro",
			[
				"id", "date", "giorni", "note"
			],
			[
				t.INTEGER, t.DATE, t.NUMERIC, t.VARCHAR + 500
			]
		)

		db.create_table (
			"manutenzione",
			[
				"id", "vasca", "data", "tipo", "nome", "quantita", "giorni", "note"
			],
			[
				t.INTEGER, t.TEXT, t.DATE, t.TEXT, t.TEXT, t.TEXT, t.DATE, t.VARCHAR + 500
			]
		)
		
		db.set_schema_presents (True)
	
	# L'update su ambiente windows dovrebbe essere fatto direttamente da qui
	# ma mi sa che e' meglio disabilitare l'update per windows
	#merger.check_for_updates () #Controlliamo se ci sono update da fare

	gobject.threads_init ()
	
	app.App = app.Gui()
	app.App.p_engine = engine.PluginEngine ()
	app.App.p_backend = db
	
	alert.alertManutenzione(db)

	tray.statusIcon.set_from_file(os.path.join (utils.DPIXM_DIR, "logopyacqua.jpg"))
	tray.statusIcon.set_tooltip("PyAcqua")
	tray.statusIcon.connect('popup-menu', tray.popup_menu_cb, tray.menu)
	tray.statusIcon.set_blinking(False)
	tray.statusIcon.set_visible(True)
	
	gtk.gdk.threads_enter ()
	app.App.main()
	gtk.gdk.threads_leave ()
	
	utils.c_info (_("Salvo le impostazioni prima di uscire"))
	impostazioni.save ()

if __name__ == "__main__":
	utils.prepare_enviroment ()
	main ()
