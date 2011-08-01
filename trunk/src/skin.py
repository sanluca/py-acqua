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
import os
import utils
from impostazioni import set, save

class Skin (gtk.Window):
	def __init__ (self):
		gtk.Window.__init__ (self)
		self.set_title (_("Skin"))
		
		utils.set_icon (self)
		
		self.set_resizable (False)
		
		self.path = utils.SKIN_DIR
		
		self.box = gtk.VBox ()
		self.box.set_spacing (4)
		self.box.set_border_width (4)

		# Hbox per contenere una scrolled e un image
		hbox = gtk.HBox ()
		
		# Una Scrolled Window per contenere
		# la Treeview

		sw = gtk.ScrolledWindow ()
		sw.set_shadow_type (gtk.SHADOW_ETCHED_IN)
		sw.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		
		# Due colonne una per il nome dello skin
		# l'altra per il percorso al file main.png
		
		self.list = list = gtk.ListStore (str, str)
		self.view = view = gtk.TreeView (list)
		
		view.append_column (gtk.TreeViewColumn(_("Skin"), gtk.CellRendererText (), text=0))
		view.get_selection ().connect ('changed', self._on_selection_changed)

		sw.add (view)

		# Creiamo self.image
		
		self.image = gtk.Image ()
		
		# Pacchiamo
		
		hbox.pack_start (sw, False, False, 0)
		hbox.pack_start (self.image)

		self.box.pack_start (hbox)

		self._reload ()

		bb = gtk.HButtonBox ()
		bb.set_layout (gtk.BUTTONBOX_END)
		bb.set_spacing (5)
		
		btn = gtk.Button (stock=gtk.STOCK_OK)
		btn.connect ('clicked', self._on_skin_ok)
		bb.pack_start (btn)
		
		btn = gtk.Button (stock=gtk.STOCK_DELETE)
		btn.connect ('clicked', self._on_delete)
		bb.pack_start (btn)
		
		btn = gtk.Button (stock=gtk.STOCK_CLOSE)
		btn.connect ('clicked', self._on_delete_event)
		bb.pack_start (btn)
		
		btn = gtk.Button (stock=gtk.STOCK_ADD)
		btn.connect ('clicked', self._insert_skin)
		bb.pack_start (btn)
		self.box.pack_start (bb, False, False, 0)
		
		self.connect ('delete-event', self._on_delete_event)
		
		self.add (self.box)
		self.show_all ()
	
	def _on_delete_event (self, widget, event):
		app.App.p_window["skin"] = None
	
	def _reload (self):
		
		# Carichiamo gli skin personali

		def go ():
			for file in os.listdir (path):
				current = os.path.join (path, file)
				
				if os.path.isdir (current):
					self._add_skin (current, self.list)

		path = utils.SKIN_DIR
		go ()

		path = utils.DSKIN_DIR
		go ()

		# FIXME: set the selection on the current skin
		
	def _add_skin (self, path, list):
		back = os.path.join (path, "main.png")
		
		if os.path.exists (back):
			list.append ([os.path.basename (path), back])
	
	def _on_selection_changed (self, selection):
		mod, it = selection.get_selected ()
		
		if it != None:
			self._update_image (mod.get_value (it, 1))
	
	def _update_image (self, path):
		self.image.set_from_file(path)
		
	def _on_delete_event (self, *w):
		self.hide ()
		
	def _insert_skin (self, widget):
		id = utils.FileChooser ( _("Seleziona Immagine"), self).run ()

		if id != None:
			name = utils.InputDialog (self, _("Inserisci il nome per il nuovo skin")).run ()			
			utils.create_skin (name, id)

		self.list.clear ()
		self._reload ()
		
	def _on_skin_ok (self, widget):
		mod, it = self.view.get_selection ().get_selected ()
		
		if it != None:
			set ("skin", mod.get_value (it, 0))
			save ()
			utils.info (_("Devi riavviare per far si che tutte le modifiche siano applicate."))
			self._on_delete_event ()

	def _on_delete (self, widget):
		mod, it = self.view.get_selection ().get_selected ()
		
		file = mod.get_value (it, 1)
		dir, nome = os.path.split (file)
		
		os.remove (os.path.join (dir, nome))
		os.removedirs (dir)

		# Rimuoviamo dalla store
		self.list.clear ()
		self._reload ()
