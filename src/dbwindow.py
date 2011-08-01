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

class NotifyType:
	SAVE = 0
	ADD  = 1
	DEL  = 2
	LOCK = 3

class BaseDBWindow (object):
	"""
	Questa classe fornisce tutti i metodi pubblici che si utilizzando in
	una class DBWindow.
	"""
	
	def after_selection_changed (self, mod, it):
		pass

	def on_row_activated (self, tree, path, col):
		pass
		
	def after_refresh (self, it):
		# Implementata dalla sovraclasse
		pass
				
	def add_entry (self, it):
		# Aggiunge la entry nel database
		pass
	
	def remove_id (self, id):
		# Passa l'id da rimuovere nel database
		pass
	def decrement_id (self, id):
		# cur.execute("update vasca set id=%d where id=%d" % (id-1, id))
		pass
	
	def pack_before_button_box (self, hb):
		pass
	
	#def filter_func (self, mod, iter):
	#	return True

	def custom_page (self, edt_frame):
		al = gtk.Alignment (0.2, xscale=1.0)
		al.add (edt_frame)
		return al
	
	def refresh_data (self, islocked=False):
		pass

class DBWindow (gtk.Window, BaseDBWindow):
	
	def _get_store (self):
		return self.stores [self.editing]
	
	def _get_view (self):
		return self.views [self.editing]
	
	def _get_last (self):
		return self.lasts [self.editing]
	
	def _get_vars (self):
		return self._vars [self.editing]
	
	def _get_page (self):
		return self.editing
	
	def _get_menu (self):
		return self.f_menus [self.editing]
	
	def _get_filt (self):
		return self.f_filters [self.editing]
	
	def _get_page_obj (self):
		return self.p_obj [self.editing]
	
	def _set_store (self, x):
		utils.c_warn ("_set_store () called ... why?")
		
	def _set_view (self, x):
		utils.c_warn ("_set_view () called ... why?")
		
	def _set_last (self, x):
		self.lasts[-1] = x
		
	def _set_vars (self, x):
		utils.c_warn ("_set_vars () called ... why?")
		
	def _set_page (self, x):
		self.editing = x
		self.nb_view.set_current_page (self.editing)

	def _set_menu (self, x):
		utils.c_warn ("_set_menu () called ... why?")

	def _set_filt (self, x):
		utils.c_warn ("_set_filt () called ... why?")
	
	def _set_page_obj (self, x):
		utils.c_warn ("_set_page_obj () called ... why?")
	
	store = property (_get_store, _set_store)
	view = property (_get_view, _set_view)
	last = property (_get_last, _set_last)
	vars = property (_get_vars, _set_vars)
	page = property (_get_page, _set_page)
	filter_menu = property (_get_menu, _set_menu)
	filter = property (_get_filt, _set_filt)
	page_obj = property (_get_page_obj, _set_page_obj)
	
	def __init__ (self):
		"""
		Costruttore da richiamare in caso in cui si debba creare una dbwindow
		con piu' di una treeview
		"""
		self._real_init ()
	
	def __init__ (self, n_row, n_col, cols, widgets, lst_store, different_renderer=False, use_filter=False):
		self._real_init ()
		self.create_context(n_row, n_col, cols, widgets, lst_store, self, different_renderer)		
		
	def _real_init (self):
		gtk.Window.__init__ (self)
		
		self.vpaned = gtk.VPaned ()
		self.t_vbox = gtk.VBox () # Quello sopra che contiene le treeview
		self.e_vbox = gtk.VBox () # Quello sotto per l'editing
		
		self.stores = []; self.views = []
		self.lasts = []; self._vars = []
		self.f_filters = []; self.f_menus = []
		self.p_obj = []
		
		self.editing = 0
		self.locked_page = -1
		
		self.nb_view = gtk.Notebook ()
		self.nb_edit = gtk.Notebook ()
		
		self.nb_view.connect ('switch-page', self._on_switch_page)
		
		#per nascondere i tab sulle varie finestre lato treeview
		self.nb_view.set_show_tabs (False)
		
		#per nascondere i tab sulle varie finestre lato modifica
		self.nb_edit.set_show_tabs (False)
		self.nb_edit.set_show_border (False)
		
		hb = gtk.HBox (2, False)
		self.button_box = self._prepare_button_box (hb)
		
		self.pack_before_button_box (hb)
				
		hb.pack_start (self.button_box)
		
		self.t_vbox.pack_start (self.nb_view)
		self.t_vbox.pack_start (hb, False, False, 0)
		
		self.e_vbox.pack_start (self.nb_edit)
		
		self._final_stage ()
	
	def _final_stage (self):		
		self.status = gtk.Statusbar ()
		self.image = gtk.Image ()

		hbox = gtk.HBox ()
		hbox.pack_start (self.image, False, False)
		hbox.pack_start (self.status)
		
		self.vpaned.pack1 (self.t_vbox, True, False)
		self.vpaned.pack2 (self.e_vbox, False, False) #L'ultima va a True se puo' essere coperto
		
		mbox = gtk.VBox ()
		mbox.pack_start (self.vpaned)
		mbox.pack_start (hbox, False, False, 0)
		
		self.add (mbox)
		self.show_all ()

		self.image.hide ()
		self.timeoutid = None

		self.connect ('delete-event', self._on_delete_event)
		
	def _prepare_button_box (self, container):
		"""
		Crea la button box
		"""
		
		bb = gtk.HButtonBox ()
		bb.set_layout (gtk.BUTTONBOX_END)

		btn = gtk.Button (stock=gtk.STOCK_ADD)
		btn.set_relief (gtk.RELIEF_NONE)
		btn.connect ('clicked', self._on_add)
		bb.pack_start (btn)

		btn = gtk.Button (stock=gtk.STOCK_REFRESH)
		btn.set_relief (gtk.RELIEF_NONE)
		btn.connect ('clicked', self._on_refresh)
		bb.pack_start (btn)

		btn = gtk.Button (stock=gtk.STOCK_REMOVE)
		btn.set_relief (gtk.RELIEF_NONE)
		btn.connect ('clicked', self._on_remove)
		bb.pack_start (btn)
		
		btn = utils.new_button (None, gtk.STOCK_DIALOG_AUTHENTICATION, True)
		btn.set_relief (gtk.RELIEF_NONE)
		btn.connect ('toggled', self._on_edit_mode, container, bb)
		bb.pack_start (btn)
		
		
		btn = utils.new_button (_("Filtro"), gtk.STOCK_APPLY)
		btn.set_relief (gtk.RELIEF_NONE)
		btn.connect ("clicked", self._on_filter_clicked)
		btn.connect ("button_press_event", self._on_popup)
		bb.pack_start (btn)
		
		return bb
	
	def _prepare_widgets (self, n_row, n_col, cols):
		"""
		Crea e alloca i widget per il controllo delle colonne in una tabella
		che viene ritornata
		"""
		
		e_tbl = gtk.Table (n_row, n_col)
		e_tbl.set_border_width (4)
		e_tbl.set_col_spacings (8)

		x, y = 0, 0

		for name in cols:
			# Se superiamo il limite ci spostiamo sull'altra colonna e resettiamo x
			
			idx = cols.index (name)
			tmp = self.vars[idx]

			#utils.debug ("Creating e_%s%d at %d %d %d %d" % (name[:5], self.editing, x, x+1, y, y+1))
			
			#self.__dict__ ["e_" + name [:5] + str (self.editing)] = tmp
			e_tbl.attach (tmp, x+1, x+2, y, y+1)

			e_tbl.attach (utils.new_label (name, x=0, y=0.5), x, x+1, y, y+1, yoptions=gtk.SHRINK)

			if idx == n_col:
				x += 2; y = 0
			else:
				y += 1
		
		return e_tbl
	
	def _prepare_columns (self, different_renderer, cols):
		"""
		Prepara e aggiunge alla treeview le colonne richieste
		"""
		
		if not different_renderer:
			renderer = gtk.CellRendererText ()
			pix_rend = gtk.CellRendererPixbuf()

		# i nomi sono in cols
		id = 0
		for name in cols:
			
			#utils.debug ("Adding %d" % id)
			
			if self.store.get_column_type (id) == gobject.TYPE_DOUBLE:
				
				if different_renderer:
					renderer = gtk.CellRendererText ()
				
				self.view.insert_column_with_data_func (-1, name, renderer, self._float_func, id)
				
			else:
				col = None

				if self.store.get_column_type (id).pytype == gtk.gdk.Pixbuf:
				
					if different_renderer:
						pix_rend = gtk.CellRendererPixbuf()
						
					col = gtk.TreeViewColumn (name, pix_rend, pixbuf=id)
					self.last -= 1
				else:
				
					if different_renderer:
						renderer = gtk.CellRendererText ()
					
					col = gtk.TreeViewColumn (name, renderer, text=id)
				
				col.set_sort_column_id (id + 1)
				col.set_clickable (True)
				col.set_resizable (True)
				
				self.view.append_column (col)
			
			id += 1
	
	def _on_switch_page (self, nb, page, page_num):
		self.nb_edit.set_current_page (page_num)
		self.editing = page_num
	
	def _on_delete_event (self, widget, event):
		if self.timeoutid != None:
			gobject.source_remove (self.timeoutid)
		
		self.post_delete_event ()
	
	def _float_func (self, col, cell, model, iter, id):
		value = model.get_value (iter, id)
		cell.set_property ("text", "%.2f" % value)
	
	def _data_func (self, col, cell, model, iter, id):
		value = model.get_value (iter, id)
		cell.set_property ("text", value)

	def _on_timeout(self):
		self.image.hide()
		self.status.pop(0)

		self.timeoutid = None
		
		return False
	
	def _on_selection_changed (self, treeselection):
		mod, it = treeselection.get_selected ()

		if it == None: return

		x = 0

		for i in self.vars:
			if self.store.get_column_type (self.vars.index (i) + 1).pytype == gtk.gdk.Pixbuf:
				#utils.debug ("image is %s" % mod.get_value (it, self.last + x))
				i.set_text( mod.get_value (it, self.last + x))
				x += 1
			else:
				i.set_text( mod.get_value (it, self.vars.index (i) + 1))

		self.after_selection_changed (mod, it)
	
	def _on_edit_mode (self, widget, hb, bb):
		if widget.get_active ():
			self.e_vbox.hide ()
			hb.hide_all ()
			bb.show ()
			widget.show_all ()
			hb.show ()
			
			self.update_status (NotifyType.LOCK, _("Modalita' sola Lettura: Abilitata"))
		else:
			self.e_vbox.show ()
			hb.show_all()
			
			self.update_status (NotifyType.LOCK, _("Modalita' sola Lettura: Disabilitata"))
	
	def _on_add (self, widget):
		self.lock ()
		
		mod = self.store
		it = mod.get_iter_first ()
		id = 0

		while it != None:
			tmp = int (self.store.get_value (it, 0))

			if tmp > id: id = tmp

			it = mod.iter_next (it)

		id += 1
		it = self.store.append ()

		# Settiamo il campo ID e gli altri campi
		self.store.set_value (it, 0, id)
		x = 0
		
		for tmp in self.vars:
			if self.store.get_column_type (self.vars.index (tmp) + 1).pytype == gtk.gdk.Pixbuf:

				#utils.debug ("col n %d => %s" % (self.last + x, tmp))\
				
				self.store.set_value (it, self.last + x, tmp.get_text ())

				self.store.set_value (it, self.vars.index (tmp) + 1, utils.make_image (tmp.get_text ()))

				x += 1
			else:
				self.store.set_value (it, self.vars.index (tmp) + 1, tmp.get_text ())

		self.add_entry (it)
		self.unlock ()

	def _on_refresh (self, widget):
		self.lock ()
		
		# Prendiamo l'iter e il modello dalla selezione
		mod, it = self.view.get_selection ().get_selected ()

		it = self.filter.convert_iter_to_child_iter (it)
		
		# Se esiste una selezione aggiorniamo la row
		# in base al contenuto delle entry
		
		if it != None:
			#id = int (self.store.get_value (it, 0))
			x = 0

			for tmp in self.vars:
				if self.store.get_column_type (self.vars.index (tmp) + 1).pytype == gtk.gdk.Pixbuf:
					
					self.store.set_value (it, x + self.last, tmp.get_text ())
					
					self.store.set_value (it, self.vars.index (tmp) + 1, utils.make_image (tmp.get_text ()))
					
					x += 1
				else:
					self.store.set_value (it, self.vars.index (tmp) + 1, tmp.get_text ())
			
			self.after_refresh (it)
		
		self.unlock ()
	
	def _on_remove (self, widget):
		self.lock ()
		
		# Prendiamo l'iter selezionato ed elimianiamolo dalla store
		mod, it = self.view.get_selection ().get_selected ()

		it = self.filter.convert_iter_to_child_iter (it)
		mod = self.store

		if it != None:
			# Questo e' il valore da confrontare
			value = int (self.store.get_value (it, 0))

			# Rimuoviamo dal database
			self.remove_id (value)

			# Rimuoviamo la riga selezionata
			self.store.remove (it)

			# Iteriamo tutte le righe per trovarne una con campo id
			# maggiore di value e modifichiamolo
			it = mod.get_iter_first ()

			while it != None:
				tmp = int (self.store.get_value (it, 0))

				if value < tmp:
					self.store.set_value (it, 0, tmp-1)
					self.decrement_id (tmp)
				
				it = mod.iter_next (it)
		self.unlock ()
	
	def create_context (self, n_row, n_col, cols, widgets, lst_store, cb_object, different_renderer=False):
		assert (len (cols) - 1 == len (widgets))
		assert (cb_object)
		
		self.stores.append (lst_store)
		self.views.append (gtk.TreeView (lst_store))
		self.lasts.append (len(cols) + 1)
		self._vars.append (widgets)
		self.p_obj.append (cb_object)

		c_id = len (lst_store) - 1

		view = self.views[c_id]

		# Filtro proviamo cosi'
		filter = lst_store.filter_new ()
		self.f_filters.append (filter)
		
		filter.set_visible_func (cb_object.filter_func)
		view.set_model (filter)

		self.f_menus.append (None)
		
		view.get_selection ().connect ('changed', self._on_selection_changed)
		view.connect ('row-activated', self.on_row_activated)
		
		self.editing = c_id
		self._prepare_columns (different_renderer, cols)
		
		sw = gtk.ScrolledWindow ()
		sw.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		sw.set_shadow_type (gtk.SHADOW_ETCHED_IN)
		
		sw.add (view)
		
		c_id = self.nb_view.append_page (sw)
		
		self.editing = c_id
		
		cols.remove (cols[0])
		
		page = self.custom_page (self._prepare_widgets(n_row, n_col, cols))
		
		self.nb_edit.append_page (page)
		
		self.nb_edit.show_all ()
		self.nb_view.show_all ()
		
		self.recreate_filter_menu_and_refresh ()
		
		return c_id
	
	def lock (self):
		self.locked_page = self.editing
	def unlock (self):
		self.locked_page = -1
	
	def recreate_filter_menu_and_refresh (self, islocked=False):
		self.f_menus[self.editing] = gtk.Menu ()
		self.page_obj.refresh_data (islocked)
	
	def refresh_all_pages (self):
		temp = self.editing
		
		for i in range (len (self.views)):
			self.editing = i
			if i == self.locked_page:
				self.recreate_filter_menu_and_refresh (True)
			else:
				self.recreate_filter_menu_and_refresh (False)
		
		self.editing = temp
	
	def update_status (self, type, string):
		self.image.show ()

		if type == NotifyType.SAVE:
			self.image.set_from_stock (gtk.STOCK_SAVE, gtk.ICON_SIZE_MENU)
		if type == NotifyType.ADD:
			self.image.set_from_stock (gtk.STOCK_ADD, gtk.ICON_SIZE_MENU)
		if type == NotifyType.DEL:
			self.image.set_from_stock (gtk.STOCK_REMOVE, gtk.ICON_SIZE_MENU)
		if type == NotifyType.LOCK:
			self.image.set_from_stock (gtk.STOCK_DIALOG_AUTHENTICATION, gtk.ICON_SIZE_MENU)
	
		if self.timeoutid != None:
			gobject.source_remove (self.timeoutid)
			self.status.pop (0)

		self.status.push (0, string)

		self.timeoutid = gobject.timeout_add (2000, self._on_timeout)
	
	def post_delete_event (self):
		pass
		
	#questa parte e per il pulsante filtro 
	def _on_filter_clicked (self, widget):
		self.filter.refilter ()

	def _on_popup (self, widget, event):
		if event.button == 3:
			self.filter_menu.popup (None, None, None, event.button, event.time)
			self.filter_menu.show_all ()

class Test(DBWindow):
	def __init__(self):
		# Per immagini prima le pixbuf e le stringhe alla fine
		lst = gtk.ListStore(int, str, str, gtk.gdk.Pixbuf, str)
		
		lst.append([1, "Francesco", "stringa",
				utils.make_image("prova.png"), "prova.png"])

		DBWindow.__init__(self, 2, 2, ["ID", "Nome", "Stringa", "Immagine"],
				[gtk.Entry(), gtk.Entry(), utils.ImgEntry()], lst)

	def remove_id (self, id):
		self.update_status(NotifyType.SAVE, "Immagine Rimossa! :)")
		
	


if __name__ == "__main__":
	Test()
	gtk.main ()
