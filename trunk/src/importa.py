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

import gtk
import utils
import agdb
import os.path
from pysqlite2 import dbapi2 as sqlite

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
class DbEntryOut (utils.FileEntry):
	def __init__ (self):
		utils.FileEntry.__init__ (self)

	def callback (self, widget):
		filter = gtk.FileFilter ()
		filter.set_name (_("Tutti i file"))

		filter.add_pattern ("db")
		ret = utils.FileChooser (_("Salva Database come..."), None, filter, False, gtk.FILE_CHOOSER_ACTION_SAVE).run ()

		if ret != None:
			self.set_text (ret)

class Importa (gtk.Window):
	def __init__ (self):
		gtk.Window.__init__ (self)

		self.set_title (_("Importa/Esporta Database"))
		
		utils.set_icon (self)
		
		self.connect ('delete-event', self.exit)
	
		vbox = gtk.VBox()
		vbox.set_spacing(4)
		vbox.set_border_width(4)
		
		tbl = gtk.Table(2, 4)
		tbl.set_border_width(4)
		tbl.set_row_spacings(4)
		
		self.ver_sette = sette = gtk.RadioButton (None, _("Versione 0.8"))
		self.ver_otto = otto = gtk.RadioButton (sette, _("Versione attuale"))
		
		tbl.attach(utils.new_label(_("Importa:")), 0, 1, 0, 1, xpadding=8)
		
		tbl.attach(utils.new_label(_("Esporta:")), 0, 1, 1, 2, xpadding=8)
		
		self.importa_db = DbEntry ()
		self.esporta_db = DbEntryOut ()
		
		tbl.attach(self.importa_db, 1, 2, 0, 1)
		tbl.attach(self.esporta_db, 1, 2, 1, 2)

		frame = gtk.Frame ("Vecchia versione:")
		vbox = gtk.VBox(2, False)
		
		self.ver_sette = sette = gtk.RadioButton (None, _("Versione 0.8"))
		self.ver_otto = otto = gtk.RadioButton (sette, _("Versione attuale"))

		vbox.pack_start (sette, False, False, 0)
		vbox.pack_start (otto, False, False, 0)

		frame.add(vbox)

		tbl.attach(frame, 0, 2, 2, 3)

		bb = gtk.HButtonBox()
		bb.set_layout(gtk.BUTTONBOX_END)
		
		btn = gtk.Button(stock=gtk.STOCK_OK)
		btn.connect('clicked', self.on_ok)
		bb.pack_start(btn)
		
		btn = gtk.Button(stock=gtk.STOCK_CANCEL)
		btn.connect('clicked', self.on_cancel)
		bb.pack_start(btn)

		tbl.attach (bb, 0, 2, 3, 4, ypadding=4)

		self.add (tbl)
		self.set_resizable (False)

		self.show_all ()
		
	def on_ok (self, widget):
		in_db = self.importa_db.get_text ()
		out_db = self.esporta_db.get_text ()

		def msg (txt, buttons=gtk.BUTTONS_OK):
			a = gtk.MessageDialog(None, 0, gtk.MESSAGE_INFO, buttons, txt)
			r = a.run ()
			a.hide (); a.destroy ()

			return r
			
		if self.ver_sette.get_active():
			
			utils.debug ("sette")
			self.esporta_db.set_text("~/.pyacqua/Data/db")
			if in_db == "":
				msg (_("Seleziona un database da convertire"))
				
			#elif out_db == "":
			#	msg (_("Seleziona il file su cui salvare"))
			else:
				if os.path.exists(out_db):
					a = msg (_("Il file esiste. Sovrascrivere?"), gtk.BUTTONS_YES_NO)

					if a != gtk.RESPONSE_YES:
						return
					else:
						#self.esporta_db.set_text("~/.pyacqua/Data/db")
					# Procediamo alla conversione
					# marcare le sezione di codice per la conversione con try/except
					# onde evitare errori. Il file da convertire e' in_db
					# Quello su cui salvare out_db

						#if self.ver_sette.get_active():
						
					# per aggiornare il database
						# da inserire direttamente il file agdb.pyacqua
						try:
							agdb.dbupdate ()
						# da mettere un dialog per dare errore in caso di non successo 
						except:
							utils.debug ("error")
							pass
						# TODO: Conversione da versione 7
				else:
					pass
		elif self.ver_otto.get_active():
			
						#questo e la versione attuale deve solo sovrascrivere il file
						# TODO: Conversione da versione 8
			#self.importa_db.set_visible (False)
			#self.esporta_db.set_visible (False)
		
			
		
						
			try:
				agdb.dbupdate
				utils.debug ("update attuale riuscito")
			except:
				pass
				utils.debug ("errore update attuale")
						

	def on_cancel (self, widget):
		self.exit ()
	
	def exit (self, *w):
		self.hide ()
