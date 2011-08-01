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
import impostazioni
from pysqlite2 import dbapi2 as sqlite
from copy import copy

class Inserisci(gtk.ScrolledWindow):
	def __init__(self):
		gtk.ScrolledWindow.__init__(self)
		
		self.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		
		box = gtk.VBox()
		box.set_spacing(4)
		box.set_border_width(4)
		
		# Iniziamo con la tabella
		tbl = gtk.Table (5, 4, False)
		
		self.store = gtk.ListStore (str)
		self.view = gtk.TreeView (self.store)
		
		self.view.append_column ( gtk.TreeViewColumn (None, gtk.CellRendererText (), text=0) )
		self.view.set_headers_visible (False)
		
		self.view.get_selection ().connect ('changed', self._on_change_selection)
		
		sw = gtk.ScrolledWindow ()
		sw.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		sw.set_shadow_type (gtk.SHADOW_ETCHED_IN)
		
		sw.add (self.view)
				
		tbl.attach (sw, 0, 2, 0, 3)
		
		
		btn = gtk.Button (stock=gtk.STOCK_REMOVE)
		btn.connect ('clicked', self._on_del_collection)
		
		tbl.attach (btn, 3, 4, 0, 1)
		
		btn = gtk.Button (stock=gtk.STOCK_ADD)
		btn.connect ('clicked', self._on_add_collection)
		
		tbl.attach (btn, 3, 4, 1, 2)
		
		self.combo = utils.Combo ()
		
		self._populate_combo ()
		
		self.combo.set_active (0)
		
		tbl.attach (self.combo, 3, 4, 2, 3)
		
		tbl.attach (utils.new_label (_("Minimo")), 1, 2, 3, 4)
		tbl.attach (utils.new_label (_("Massimo")), 2, 3, 3, 4)
		tbl.attach (utils.new_label (_("Ideale")), 3, 4, 3, 4)
		
		labels = (
			 _('Ph'),
			 _('Kh'),
			 _('Gh'),
			 _('No2'),
			 _('No3'),
			 _('Conducibilita\''),
			 _('Ammoniaca'),
			 _('Ferro'),
			 _('Rame'),
			 _('Fosfati'),
			 _('Calcio'),
			 _('Magnesio'),
			 _('Densita\'')
		)
		
		self.widgets = []
		
		x = 4
		for i in labels:
			tbl.attach (utils.new_label (i), 0, 1, x, x+1)
			
			min_entry = utils.CheckedFloatEntry ()
			max_entry = utils.CheckedFloatEntry ()
			ide_entry = utils.CheckedFloatEntry ()
			
			tbl.attach (min_entry, 1, 2, x, x+1)
			tbl.attach (max_entry, 2, 3, x, x+1)
			tbl.attach (ide_entry, 3, 4, x, x+1)
			
			self.widgets.append ([min_entry, max_entry, ide_entry])
			
			x += 1
		
		box.pack_start(tbl)
		
		bb = gtk.HButtonBox()
		bb.set_layout(gtk.BUTTONBOX_END)
		bb.set_spacing(4)
		
		btn = gtk.Button(stock=gtk.STOCK_APPLY)
		btn.connect('clicked', self._on_apply_changes)
		btn.set_relief (gtk.RELIEF_NONE)
		bb.pack_start(btn)
		box.pack_start(bb, False, False, 0)
		
		
		self.add_with_viewport (box)
		self.show_all ()
	
	def _on_change_selection (self, selection):
		mod, it = selection.get_selected ()
		
		if it != None:
			collection = impostazioni.get_collection (mod.get_value (it, 0))
			
			if not collection: return
			
			keys = ('ph', 'kh', 'gh', 'no2', 'no3', 'con', 'am', 'fe', 'ra', 'fo', 'cal', 'mag', 'den')
			
			x = 0
			for i in keys:
				
				if collection.has_key (i):
					min, max, ideal = collection[i]
					self.widgets[x][0].set_text (min)
					self.widgets[x][1].set_text (max)
					self.widgets[x][2].set_text (ideal)
				
				x += 1
	
	def _populate_combo (self):
		self.combo.append_text (_("Nessuna base"))
		
		for i in impostazioni.get_names_of_collections ():
			self.combo.append_text (i)
			self.store.append ([i])
	
	def _on_del_collection (self, widget):
		mod, it = self.view.get_selection ().get_selected ()
		
		if it != None:
			impostazioni.delete_collection (mod.get_value (it, 0))
			self.store.remove (it)
			
	def _on_add_collection (self, widget):
		name = utils.InputDialog (None, _("Nome per la nuova collezione:")).run ()
		
		if impostazioni.get_collection (name) != None:
			utils.warning (_("Esiste gia' una collezione con lo stesso nome"))
			return
		elif name == None:
			utils.warning (_("Devi fornire un nome per la nuova collezione"))
			return
		else:
			keys = ('ph', 'kh', 'gh', 'no2', 'no3', 'con', 'am', 'fe', 'ra', 'fo', 'cal', 'mag', 'den')
			collection = {}
			
			if self.combo.get_active () == 0:
				# Nessun modello di base
				for i in keys:
					collection[i] = [None, None, None]
			else:
				base = impostazioni.get_collection (self.combo.get_active_text ())
				
				if not base:
					for i in keys:
						collection[i] = [None, None, None]
				else:
					collection = copy (base)
			
			# Aggiungiamo la nostra collection
			
			self.store.append ([name])
			impostazioni.add_collection (name, collection)
	
	def _on_apply_changes (self, widget):
		mod, it = self.view.get_selection ().get_selected ()
		
		if it != None:
			# Ora estrapoliamo i valori e applichiamo le modifiche
			
			collection = impostazioni.get_collection (mod.get_value (it, 0))
			
			if collection == None: return
			
			keys = ('ph', 'kh', 'gh', 'no2', 'no3', 'con', 'am', 'fe', 'ra', 'fo', 'cal', 'mag', 'den')
			
			x = 0
			for i in keys:
				min = self.widgets[x][0].get_text ()
				max = self.widgets[x][1].get_text ()
				ide = self.widgets[x][2].get_text ()
				
				collection [i] = [min, max, ide]
				
				x += 1
				
	def _on_delete_event(self, *w):
		# dovrebbe bastare
		impostazioni.save ()
		
		self.hide()
