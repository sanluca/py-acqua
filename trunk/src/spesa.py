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

#create table spese(id integer, vasca TEXT, date DATE, tipologia TEXT, quantita NUMERIC, nome TEXT,soldi TEXT, note VARCHAR(500), img TEXT)")

import gtk
import utils
import impostazioni
from dbwindow import BaseDBWindow, NotifyType
import app

class Spesa(BaseDBWindow):
	def __init__(self, window_db):
		self.main_db = window_db
		self.col_lst = [
				_('Id'),
				_('Vasca'),
				_('Data'),
				_('Tipo'),
				_('Nome'),
				_('Quantita'),
				_('Prezzo'),
				_('Note'),
				_('Immagine')]
	
	def bind_context (self):
		lst = gtk.ListStore (int, str, str, str, str, str, str, str, gtk.gdk.Pixbuf, str)
		
		self.context_id = self.main_db.create_context (1, 7, self.col_lst,
									 [utils.Combo (),
									  utils.DataButton (),
									  utils.Combo ([
									  	_("Vasca"), _("Pesci"),
									  	_("Piante"), _("Fertilizzante"),
									  	_("Invertebrati"), _("Varie")
									  ]),
									  gtk.Entry (),
									  utils.IntEntry (),
									  gtk.Entry (),
									  utils.NoteEntry (),
									  utils.ImgEntry ()], lst, self, True)
	
	def refresh_data (self, islocked):
		if islocked: return
		
		self.main_db.store.clear ()
		self.main_db.vars[0].clear_all ()
		
		if self.main_db.filter_menu:
			tmp = self.main_db.filter_menu
			self.main_db.filter_menu = gtk.Menu ()
			del tmp
		else:
			self.main_db.filter_menu = gtk.Menu ()
		
		for y in app.App.p_backend.select ("*", "vasca"):
			self.main_db.vars[0].append_text (y[3])
			self.main_db.filter_menu.append (gtk.CheckMenuItem (y[3]))
			
		for y in app.App.p_backend.select ("*", "spesa"):
			self.main_db.store.append ([y[0], y[1], y[2], y[3], y[4], y[5], y[6], y[7], utils.make_image(y[8]), y[8]])
	
	def filter_func (self, mod, iter):
		filters = list ()

		for i in self.main_db.filter_menu.get_children ():
			if i.active:
				filters.append (i.get_children ()[0].get_text ())
		
		if filters == []:
			return True

		utils.c_info ("Active filters: %s" % filters)
		val = mod.get_value (iter, 1)
		utils.c_info ("Value to be filtered: %s" % val)
		
		if not val:
			return True
		
		if val in filters:
			return True
		else:
			return False
		
	def after_selection_changed (self, mod, it):
		pass

	def on_row_activated (self, tree, path, col):
		mod = self.main_db.view.get_model()
		it = mod.get_iter_from_string(str(path[0]))
	
		utils.InfoDialog (self.main_db, _("Riepilogo"), self.col_lst, self.main_db.vars, mod.get_value (it, 9))
		
	def after_refresh (self, it):
		# Implementata dalla sovraclasse
		mod, it = self.main_db.view.get_selection ().get_selected ()
			
		id = mod.get_value (it, 0)
			
		vasca  = self.main_db.vars[0].get_text ()
		data  = self.main_db.vars[1].get_text ()
		tipo  = self.main_db.vars[2].get_text ()
		nome = self.main_db.vars[3].get_text ()
		quantita  = self.main_db.vars[4].get_text ()
		prezzo  = self.main_db.vars[5].get_text ()
		note  = self.main_db.vars[6].get_text ()
		img  = self.main_db.vars[7].get_text ()
	
		#utils.cmd ("update manutenzione set vasca='%(vasca)s', data='%(data)s', tipo='%(tipo)s', nome='%(nome)s', quantita='%(quantita)s', prezzo='%(prezzo)s', note='%(note)s', img='%(img)s' where id = %(id)s" % vars())
		
		app.App.p_backend.update (
				"spesa",
				[
					"vasca", "data", "tipologia", "nome", "quantita", "soldi", "note", "img", "id"
				],
				[
					vasca, data, tipo, nome, quantita, prezzo, note, img, id
				]
			)
			
		self.main_db.update_status (NotifyType.SAVE, _("Row aggiornata (ID: %d)") % id)
				
	def add_entry (self, it):
		# Aggiunge la entry nel database
		mod, id = self.main_db.view.get_selection ().get_selected ()
		mod = self.main_db.store
	
		id = mod.get_value (it, 0)
	
			#for i in self.vars:
			#	print i.get_text ()
		#utils.cmd ('insert into spesa values(?,?,?,?,?,?,?,?,?)',
				   
		app.App.p_backend.insert (
				"spesa",
				[
					id,
					self.main_db.vars[0].get_text (),
					self.main_db.vars[1].get_text (),
					self.main_db.vars[2].get_text (),
					self.main_db.vars[3].get_text (),
					self.main_db.vars[4].get_text (),
					self.main_db.vars[5].get_text (),
					self.main_db.vars[6].get_text (),
					self.main_db.vars[7].get_text ()
				]
			)
		
			
		self.main_db.update_status (NotifyType.ADD, _("Row aggiunta (ID: %d)") % id)
	
	def remove_id (self, id):
		# Passa l'id da rimuovere nel database
		#utils.cmd ('delete from spesa where id=%d' % id)
		app.App.p_backend.delete ("spesa", "id", id)
		self.main_db.update_status (NotifyType.DEL, _("Row rimossa (ID: %d)") % id)
		
	def decrement_id (self, id):
		# cur.execute("update vasca set id=%d where id=%d" % (id-1, id))
		app.App.p_backend.update ("spesa", ["id", "id"], [id - 1, id])
		#utils.cmd ("update spesa set id=%d where id=%d" % (id - 1, id))
		
	def pack_before_button_box (self, hb):
		pass
