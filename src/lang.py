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
import utils
import os.path
import impostazioni
from impostazioni import set, get, save

class LangWindow (gtk.Window):
	def __init__ (self):
		gtk.Window.__init__ (self)

		self.set_title (_("Selezione Lingua"))
		self.set_size_request (320, 170)
		
		utils.set_icon (self)
		
		self.connect ('delete-event', self._on_delete_event)

		mbox = gtk.VBox ()
		vbox = gtk.VBox ()

		mbox.set_border_width (4)
		vbox.set_border_width (4)

		self.it = it = gtk.RadioButton (None, _("Italiano"))
		self.en = en = gtk.RadioButton (it, _("Inglese"))
		self.fr = fr = gtk.RadioButton (it, _("Francese"))

		it_icon = gtk.Image (); en_icon = gtk.Image (); fr_icon = gtk.Image ()
		
		it_icon.set_from_file (os.path.join (utils.DPIXM_DIR, "it.xpm"))
		en_icon.set_from_file (os.path.join (utils.DPIXM_DIR, "en.xpm"))
		fr_icon.set_from_file (os.path.join (utils.DPIXM_DIR, "fr.xpm"))

		box = gtk.HBox ()
		box.pack_start (it_icon, False, False, 0)
		box.pack_start (it)
		vbox.pack_start (box, False, False, 0)

		box = gtk.HBox ()
		box.pack_start (en_icon, False, False, 0)
		box.pack_start (en)
		vbox.pack_start (box, False, False, 0)

		box = gtk.HBox ()
		box.pack_start (fr_icon, False, False, 0)
		box.pack_start (fr)
		vbox.pack_start (box, False, False, 0)

		frm = gtk.Frame (_("Seleziona Lingua:"))
		frm.add (vbox)

		mbox.pack_start (frm)

		bb = gtk.HButtonBox ()
		bb.set_layout (gtk.BUTTONBOX_END)

		btn = gtk.Button (stock=gtk.STOCK_CANCEL)
		btn.connect ('clicked', self._on_delete_event)
		bb.pack_start (btn)

		btn = gtk.Button (stock=gtk.STOCK_OK)
		btn.connect ('clicked', self._on_ok)
		bb.pack_start (btn)

		mbox.pack_start (bb, False, False, 0)

		self.add (mbox)

		if get("lang").lower () == "it":
			it.set_active (True)
		elif get("lang").lower () == "en":
			en.set_active (True)
		elif get("lang").lower () == "fr":
			fr.set_active (True)

		self.show_all ()
		
	def start (self):
		utils.c_info ("Starting %s" % self.__name__)
		
		menu = app.App.get_plugin_menu ()

		self.item = gtk.MenuItem (_("Lang"))
		self.item.connect ('activate', self.on_activated)
		self.item.show ()

		menu.append (self.item)
		
	def _on_delete_event (self, *w):
		self.hide ()
		del self
		app.App.p_window["lang"] = None
	
	def _on_ok (self, widget):
		if self.en.get_active ():
			set ("lang", "en")
		elif self.fr.get_active ():
			set ("lang", "fr")
		elif self.it.get_active ():
			set ("lang", "it")
		else:
			return

		save ()
		self.hide ()
		self._on_delete_event ()
