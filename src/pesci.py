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
import dbwindow
import piante
import invertebrati
import spesa
import app

class Pesci (dbwindow.DBWindow):
	def __init__(self):
		self.piante = piante.Piante (self)
		self.invert = invertebrati.Invertebrati (self)
		self.spesa  = spesa.Spesa (self)
		
		lst = gtk.ListStore (int, str, str, int, str, str, gtk.gdk.Pixbuf, str)
		
		self.col_lst = [
			_('Id'),
			_('Data'),
			_('Vasca'),
			_('Quantita'),
			_('Nome'),
			_('Note'),
			_("Immagine")
		]
		
		dbwindow.DBWindow.__init__ (self, 2, 2, self.col_lst,
			[
				utils.DataButton (),
				utils.Combo (),
				utils.IntEntry (),
				gtk.Entry (),
				utils.NoteEntry (),
				utils.ImgEntry ()
			],
			lst,
			True
		)
		
		self.set_title (_("Pesci"))
		self.set_size_request (600, 400)
		
		utils.set_icon (self)
		
		self.piante.bind_context ()
		self.invert.bind_context ()
		self.spesa.bind_context ()
	
	def refresh_data (self, islocked):
		if islocked: return
		
		self.store.clear ()
		self.vars[1].clear_all ()
		
		for y in app.App.p_backend.select ("*", "vasca"):
			self.vars[1].append_text (y[3])
			self.filter_menu.append (gtk.CheckMenuItem (y[3]))
		
		for y in app.App.p_backend.select ("*", "pesci"):
			self.store.append ([y[0], y[1], y[2], y[3], y[4], y[5], utils.make_image(y[6]), y[6]])
	
	def post_delete_event (self):
		app.App.p_window["popolazione"] = None

	def after_refresh (self, it):
		if self.page == 0:
			mod, it = self.view.get_selection().get_selected()
		
			id = mod.get_value (it, 0)
		
			date = self.vars[0].get_text ()
			vasca = self.vars[1].get_text ()
			quantita = self.vars[2].get_text ()
			nome = self.vars[3].get_text ()
			note = self.vars[4].get_text ()
			img = self.vars[5].get_text ()
			
			app.App.p_backend.update (
				"pesci",
				[
					"date", "vasca", "quantita", "nome", "note", "img", "id"
				],
				[
					date, vasca, quantita, nome, note, img, id
				]
			)
			
			self.update_status (dbwindow.NotifyType.SAVE, _("Row aggiornata (ID: %d)") % id)
		
		elif self.page == 1:
			self.piante.after_refresh (it)
		elif self.page == 2:
			self.invert.after_refresh (it)
		elif self.page == 3:
			self.spesa.after_refresh (it)
	
	def add_entry (self, it):
		if self.page == 0:
			mod = self.store

			id = mod.get_value (it, 0)

			#for i in self.vars:
			#	print i.get_text ()
			
			app.App.p_backend.insert (
				"pesci",
				[
					id,
					self.vars[0].get_text (),
					self.vars[1].get_text (),
					self.vars[2].get_text (),
					self.vars[3].get_text (),
					self.vars[4].get_text (),
					self.vars[5].get_text ()
				]
			)
			
			self.update_status (dbwindow.NotifyType.ADD, _("Row aggiunta (ID: %d)") % id)
		elif self.page == 1:
			self.piante.add_entry (it)
		elif self.page == 2:
			self.invert.add_entry (it)
		elif self.page == 3:
			self.spesa.add_entry (it)
		
	def remove_id (self, id):
		if self.page == 0:
			app.App.p_backend.delete ("pesci", "id", id)
			self.update_status (dbwindow.NotifyType.DEL, _("Row rimossa (ID: %d)") % id)
		elif self.page == 1:
			self.piante.remove_id (id)
		elif self.page == 2:
			self.invert.remove_id (id)
		elif self.page == 3:
			self.spesa.remove_id (id)
	
	def decrement_id (self, id):
		if self.page == 0:
			app.App.p_backend.update ("pesci", ["id", "id"], [id - 1, id])
		elif self.page == 1:
			self.piante.decrement_id (id)
		elif self.page == 2:
			self.invert.decrement_id (id)
		elif self.page == 3:
			self.spesa.decrement_id (id)		
	
	def on_row_activated(self, tree, path, col):
		if self.page == 0:
			mod = self.view.get_model()
			it = mod.get_iter_from_string(str(path[0]))

			utils.InfoDialog(self, _("Riepilogo"), self.col_lst, self.vars, mod.get_value (it, 7))
		elif self.page == 1:
			self.piante.on_row_activated (tree, path, col)
		elif self.page == 2:
			self.invert.on_row_activated (tree, path, col)
		elif self.page == 3:
			self.spesa.on_row_activated (tree, path, col)
	
	def pack_before_button_box (self, hb):
		cmb = utils.Combo ()
		
		cmb.append_text (_("Pesci"))
		cmb.append_text (_("Piante"))
		cmb.append_text (_("Invertebrati"))
		cmb.append_text (_("Spesa"))
		
		cmb.set_active (0)
		
		cmb.connect ('changed', self._on_change_view)
		
		align = gtk.Alignment (0, 0.5)
		align.add (cmb)
		
		hb.pack_start (align, False, True, 0)
		
		cmb.show ()
		
	def _on_change_view (self, widget):
		id = widget.get_active ()
		self.page = id
	
	def filter_func (self, mod, iter):
		filters = list ()
		
		for i in self.filter_menu.get_children ():
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
