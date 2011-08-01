#
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
import gobject
import utils
import dbwindow
import pango
import manutenzione
import spesa
import app

class Vasca (dbwindow.DBWindow):
	def __init__ (self):
		
		self.manutenzione = manutenzione.Manutenzione (self)
		# id integer, vasca TEXT, date DATE, nome TEXT, litri TEXT, tipo TEXT, filtro TEXT, co TEXT, illuminazione TEXT, reattore TEXT, schiumatoio TEXT, riscaldamento TEXT, img TEXT
		lst = gtk.ListStore (int, str, str, str, float, str, str, str, str, str, str, str, str, gtk.gdk.Pixbuf, str)

		tmp = utils.Combo ([_("Dolce"), _("Dolce Tropicale"), _("Marino"), _("Marino Mediterraneo"), _("Paludario"), _("Salmastro")])
		tmp.connect ('changed', self._aggiorna)

		self.col_lst = [_('Id'), _('Vasca'), _('Data'), _('Nome'), _('Litri'),
			_('Modello Acquario'), _('Tipo Filtro'),
			_('Impianto Co2'), _('Illuminazione'), 
			_('Reattore di calcio'), _('Schiumatoio'), _('Riscaldamento Refrigerazione'), _("Note"), _("Immagine")]
		
		dbwindow.DBWindow.__init__ (self, 2, 5, self.col_lst,
				[tmp, utils.DataButton (), gtk.Entry (), utils.FloatEntry (),
				 gtk.Entry (), gtk.Entry (), gtk.Entry (), gtk.Entry (), gtk.Entry (),
				 gtk.Entry (), gtk.Entry (), utils.NoteEntry (), utils.ImgEntry ()], lst, True)
		
		self.view.get_column (12).get_cell_renderers ()[0].set_property ('ellipsize-set', True)
		self.view.get_column (12).get_cell_renderers ()[0].set_property ('ellipsize', pango.ELLIPSIZE_END)
		self.view.get_column (12).set_min_width (140)
		
		self.set_title (_("Vasche"))
		self.set_size_request (700, 500)
		
		utils.set_icon (self)
		
		self.manutenzione.bind_context ()
	
	def refresh_data (self, islocked):
		if islocked: return
		
		self.store.clear ()
		
		for y in app.App.p_backend.select ("*", "vasca"):
			self.store.append([y[0], y[1], y[2], y[3], y[4],
				y[5], y[6], y[7], y[8], y[9], y[10], y[11], y[12], utils.make_image(y[13]), y[13]])
		
		def unz (txt):
			self.filter_menu.append (gtk.CheckMenuItem (txt))
		
		unz (_("Dolce"))
		unz (_("Dolce Tropicale"))
		unz (_("Marino"))
		unz (_("Marino Mediterraneo"))
		unz (_("Paludario"))
		unz (_("Salmastro"))
		
	def filter_func (self, mod, iter):
		filters = []
		
		for i in self.filter_menu.get_children ():
			if i.active:
				filters.append (i.get_children ()[0].get_text ())
		
		if filters == []:
			return True
		
		utils.c_info ("Active filter: %s" % filters)
		val = mod.get_value (iter, 1)
		utils.c_info ("Value to be filtered: %s" % val)
		
		if not val:
			return True
		
		if val in filters:
			return True
		else:
			return False
	
	def post_delete_event (self):
		app.App.p_window["vasca"] = None
		
	def _aggiorna(self, widget):
		id = self.vars[0].get_active()

		for i in self.vars:
			self._reactivate (i)
		
		if id == 0 or id == 1: # Dolce || Dolce Tropicale
			# Reattore di calcio e Schiumatoio disabilitati
			self._deactivate (8, _("Assente"))
			self._deactivate (9, _("Assente"))
		elif id == 2 or id == 3: # Marino || Marino Mediterraneo
			pass
		elif id == 4 or id == 5: # Paludario
			self._deactivate (8, _("Assente"))
			self._deactivate (9, _("Assente"))
	
	def _reactivate (self, widget):
		ret = widget.get_data ('old-value')

		if ret != None:
			widget.set_text (ret)

		widget.set_property ('sensitive', True)

	def _deactivate (self, id, txt=None):
		self.vars[id].set_property ('sensitive', False)
		
		if txt != None:
			self.vars[id].set_data ('old-value', self.vars[id].get_text ())
			self.vars[id].set_text (txt)

	def after_refresh (self, it):
		if self.page == 0:
			mod, it = self.view.get_selection ().get_selected ()
			
			id = mod.get_value (it, 0)
			
			text  = self.vars[0].get_text ()
			date  = self.vars[1].get_text ()
			name  = self.vars[2].get_text ()
			litri = self.vars[3].get_text ()
			tacq  = self.vars[4].get_text ()
			tflt  = self.vars[5].get_text ()
			ico2  = self.vars[6].get_text ()
			illu  = self.vars[7].get_text ()
			reat  = self.vars[8].get_text ()
			schiu = self.vars[9].get_text ()
			risca = self.vars[10].get_text ()
			note  = self.vars[11].get_text ()
			img   = self.vars[12].get_text ()
			
			app.App.p_backend.update (
				"vasca",
				[
					"vasca", "date", "nome", "litri", "tipo", "filtro", "co", "illuminazione",
					"reattore", "schiumatoio", "riscaldamento", "note", "img", "id"
				],
				[
					text, date, name, litri, tacq, tflt, ico2, illu, reat, schiu, risca, note, img, id
				]
			)
	
			#utils.cmd ("update vasca set vasca='%(text)s', date='%(date)s', nome='%(name)s', litri='%(litri)s', tipo='%(tacq)s', filtro='%(tflt)s', co='%(ico2)s', illuminazione='%(illu)s', reattore='%(reat)s', schiumatoio='%(schiu)s', riscaldamento='%(risca)s', note='%(note)s', img='%(img)s' where id = %(id)s" % vars())
			
			self.update_status (dbwindow.NotifyType.SAVE, _("Row aggiornata (ID: %d)") % id)
			
		elif self.page == 1:
			self.manutenzione.after_refresh (it)
	
	def add_entry (self, it):
		if self.page == 0:
			mod, id = self.view.get_selection ().get_selected ()
			mod = self.store
	
			id = mod.get_value (it, 0)
	
			app.App.p_backend.insert (
				"vasca",
				[
					id,
					self.vars[0].get_text (),
					self.vars[1].get_text (),
					self.vars[2].get_text (),
					self.vars[3].get_text (),
					self.vars[4].get_text (),
					self.vars[5].get_text (),
					self.vars[6].get_text (),
					self.vars[7].get_text (),
					self.vars[8].get_text (),
					self.vars[9].get_text (),
					self.vars[10].get_text (),
					self.vars[11].get_text (),
					self.vars[12].get_text ()
				]
			)
			
			self.update_status (dbwindow.NotifyType.ADD, _("Row aggiunta (ID: %d)") % id)
		
		elif self.page == 1:
			self.manutenzione.add_entry (it)
	
	def remove_id (self, id):
		if self.page == 0:
			app.App.p_backend.delete ("vasca", "id", id)
			#utils.cmd ('delete from vasca where id=%d' % id)
			self.update_status (dbwindow.NotifyType.DEL, _("Row rimossa (ID: %d)") % id)
			
		elif self.page == 1:
			self.manutenzione.remove_id (id)
	
	def decrement_id (self, id):
		if self.page == 0:
			app.App.p_backend.update ("vasca", ["id", "id"], [id - 1, id])
			#utils.cmd ("update vasca set id=%d where id=%d" % (id - 1, id))
			
		elif self.page == 1:
			self.manutenzione.decrement_id (id)
	
	def on_row_activated(self, tree, path, col):
		if self.page == 0:
			mod = self.view.get_model()
			it = mod.get_iter_from_string(str(path[0]))
	
			utils.InfoDialog(self, _("Riepilogo"), self.col_lst, self.vars, mod.get_value (it, 14))
		
		elif self.page == 1:
			self.manutenzione.on_row_activated (tree, path, col)
	
	def _on_change_view (self, widget):
		id = widget.get_active ()
		
		self.page = id
		
	def pack_before_button_box (self, hb):
		cmb = utils.Combo ()
		
		cmb.append_text (_("Modifica Vasche"))
		cmb.append_text (_("Manutenzione"))
		
		cmb.set_active (0)
		
		cmb.connect ('changed', self._on_change_view)
		
		align = gtk.Alignment (0, 0.5)
		align.add (cmb)
		
		hb.pack_start (align, False, True, 0)
		
		cmb.show ()
