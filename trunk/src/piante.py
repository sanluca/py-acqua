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
from dbwindow import BaseDBWindow, NotifyType
import app

class Piante (BaseDBWindow):
	def __init__(self, window_db):
		
		self.main_db = window_db
		self.col_lst = [
			_('Id'),
			_('Data'),
			_('Vasca'),
			_('Quantita'),
			_('Nome'),
			_('Note'),
			_("Immagine")
		]
	
	def bind_context (self):
		lst = gtk.ListStore (int, str, str, int, str, str, gtk.gdk.Pixbuf, str)
		
		self.context_id = self.main_db.create_context (2, 2, self.col_lst,
							[
								utils.DataButton (),
								utils.Combo (),
								utils.IntEntry (),
								gtk.Entry (),
								utils.NoteEntry (),
								utils.ImgEntry ()
							],
							
							lst,
							self,
							True
		)
	
	def refresh_data (self, islocked):
		if islocked: return
		
		self.main_db.store.clear ()
		self.main_db.vars[1].clear_all ()
		
		for y in app.App.p_backend.select ("*", "piante"):
			self.main_db.store.append([y[0], y[1], y[2], y[3], y[4], y[5], utils.make_image(y[6]), y[6]])
		
		for y in app.App.p_backend.select ("*", "vasca"):
			self.main_db.vars[1].append_text (y[3])
	
	def after_refresh (self, it):
		mod, it = self.main_db.view.get_selection().get_selected()
	
		id = mod.get_value (it, 0)
	
		date     = self.main_db.vars[0].get_text ()
		vasca    = self.main_db.vars[1].get_text ()
		quantita = self.main_db.vars[2].get_text ()
		nome     = self.main_db.vars[3].get_text ()
		note     = self.main_db.vars[4].get_text ()
		img      = self.main_db.vars[5].get_text ()
	
		app.App.p_backend.update (
			"piante",
			[
				"date", "vasca", "quantita", "nome", "note", "img", "id"
			],
			[
				date, vasca, quantita, nome, note, img, id
			]
		)
		
		self.main_db.update_status (NotifyType.SAVE, _("Row aggiornata (ID: %d)") % id)
	
	def add_entry (self, it):
		mod, id = self.main_db.view.get_selection ().get_selected ()
		mod = self.main_db.store
		
		id = mod.get_value (it, 0)
		
		app.App.p_backend.insert (
			"piante",
			[
				id,
				self.main_db.vars[0].get_text (),
				self.main_db.vars[1].get_text (),
				self.main_db.vars[2].get_text (),
				self.main_db.vars[3].get_text (),
				self.main_db.vars[4].get_text (),
				self.main_db.vars[5].get_text ()
				
			]
		)
		
		self.main_db.update_status (NotifyType.ADD, _("Row aggiunta (ID: %d)") % id)
	
	def remove_id (self, id):
		app.App.p_backend.delete ("piante", "id", id)
		self.main_db.update_status (NotifyType.DEL, _("Row rimossa (ID: %d)") % id)
		
	def decrement_id (self, id):
		app.App.p_backend.update ("pesci", ["id", "id"], [id - 1, id])
		
	def on_row_activated(self, tree, path, col):
		mod = self.main_db.view.get_model()
		it = mod.get_iter_from_string(str(path[0]))
		
		utils.InfoDialog(self.main_db, _("Riepilogo"), self.col_lst, self.main_db.vars, mod.get_value (it, 7))

	def filter_func (self, mod, iter):
		filters = list ()
		for i in self.main_db.filter_menu.get_children ():
			if i.active:
				filters.append (i.get_children ()[0].get_text ())
		
		if filters == []:
			return True

		utils.c_info ("Active filters: %s" % filters)
		val = mod.get_value (iter, 2)
		utils.c_info ("Value to be filtered: %s" % val)
		
		if not val:
			return True
		if val in filters:
			return True
		else:
			return False
