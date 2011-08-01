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
from app import App

class Plugin(gtk.Window):
	
	def __init__(self):
		gtk.Window.__init__(self)
		self.set_title(_("Plug-in"))
		self.set_resizable(False)
		
		utils.set_icon (self)
		self.set_size_request(500, 150)
				
		box = gtk.VBox()
		
		self.store = gtk.ListStore(int, str, str, str, str)
		self.view = view = gtk.TreeView(self.store)
		lst = [_('Id'), _('Nome'), _('Descrizione'), _('Versione'), _('Autore')]
		
		render = gtk.CellRendererText()
		
		for i in lst:
			id = lst.index(i)
			col = gtk.TreeViewColumn(i, render, text = id)
			col.set_sort_column_id(id)
			col.set_clickable(True)
			col.set_resizable(True)
			view.append_column(col)
			
		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		
		sw.add(view)
		box.pack_start(sw)
		
		bb = gtk.HButtonBox()
		bb.set_layout(gtk.BUTTONBOX_END)
		
		btn = gtk.Button(stock=gtk.STOCK_ADD)
		btn.connect('clicked', self._on_add)
		bb.pack_start(btn)
		
		btn = gtk.Button(stock=gtk.STOCK_REMOVE)
		btn.connect('clicked', self._on_unload)
		bb.pack_start(btn)
		
		box.pack_start(bb, False, False, 0)
		
		self.connect ('delete-event', self._on_delete_event)
		
		self.add(box)
		self._fillstore()
		self.show_all()
	
	def _on_delete_event (self, widget, event):
		App.p_window["plugin"] = None
	
	def _on_unload(self, widget):
		mod, it = self.view.get_selection().get_selected()
		
		if it != None:
			id = mod.get_value (it, 0)
			plug = App.p_engine.array[id]
			
			plug.stop()
			App.p_engine.array.remove(plug)
			
			self.store.clear()
			self._fillstore()
		
	def _on_add(self, widget):
		filter = gtk.FileFilter()
		filter.set_name(_("PyAcqua Plugins"))
		filter.add_pattern("*.py")
		
		ret = utils.FileChooser(_("Seleziona un Plugin per PyAcqua"), self, filter).run()
		
		if ret != None:
			utils.copy_plugin (ret)
			
			name = os.path.basename (ret)[:-3]
			App.p_engine.load (os.path.join (os.path.abspath (os.getcwd ()), "Plugin"), name, name)
			
			self.store.clear ()
			self._fillstore ()
			
	def _fillstore(self):
		for i in App.p_engine.array:
			self.store.append([App.p_engine.array.index(i), i.__name__, i.__desc__, i.__ver__, i.__author__])
