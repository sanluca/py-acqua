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
import gtk.gdk
import gobject
import os
import sys
import utils
import dbwindow
import datetime
import impostazioni
import app


# Listiamo altrimenti nn ci permette la modifica
gcolor = [
	gtk.gdk.color_parse ('#bcfffc'), # Minore
	gtk.gdk.color_parse ('#ff8080'), # Maggiore
	gtk.gdk.color_parse ('#80ff80'), # OK
	None  # Non settato.. lo prendo dal gtk.Style
]

class GraphPage (gtk.ScrolledWindow):
	
	def __init__ (self, legend=False):
		gtk.ScrolledWindow.__init__ (self)
		
		self.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		
		self.legend = legend
		
		tbl = gtk.Table (4, 2, False)
		
		self.menu = gtk.Menu ()
		
		for y in utils.get ('select * from vasca'):
			self.menu.append (gtk.CheckMenuItem (y[3]))
		
		al = gtk.Alignment(0, 0.5)
		btn = gtk.Button()
		btn.set_relief (gtk.RELIEF_NONE)
		hb = gtk.HBox (0, False)
		hb.add (gtk.Arrow (gtk.ARROW_RIGHT, gtk.SHADOW_ETCHED_IN))
		hb.add (gtk.Label (_("Selezione Vasche")))
		btn.add (hb)
		al.add (btn)
		
		btn.connect ('button_press_event', self.on_popup)
		
		bb = gtk.HButtonBox ()
		bb.set_layout (gtk.BUTTONBOX_EDGE)
		
		button = utils.new_button (_("Plot"), gtk.STOCK_ZOOM_IN)
		button.connect ('clicked', self.on_plot)
		
		bb.pack_start (button)
		
		self.m_box = gtk.VBox (False, 2)
		
		self.checks = []		
		labels = (_('Ph'), _('Kh'), _('Gh'), _('No2'), _('No3'),
			_('Conducibilita\''), _('Ammoniaca'), _('Ferro'), _('Rame'), _('Fosfati'),
			_('Calcio'), _('Magnesio'), _('Densita\''))
		
		x = 1
		funny_toggle = False
		
		for i in labels:
			widg = gtk.CheckButton (i)
			self.checks.append (widg)
			if not funny_toggle:
				tbl.attach (widg, 1, 2, x, x+1)
				x += 1
			else:
				tbl.attach (widg, 0, 1, x, x+1)
				
			funny_toggle = not funny_toggle
		
		tbl.attach (utils.new_label (_("Vasca:")), 0, 1, 0, 1)
		tbl.attach (utils.new_label (_("Valori:")), 0, 1, 1, 2)
		tbl.attach (al, 1, 2, 0, 1)
		tbl.attach (bb, 0, 2, x, x+1)
		
		self.add_with_viewport (tbl)
		
		self.show_all ()
	
	def on_plot (self, widget):
		vasche = []
		to_plot = []
		data = []
		
		# Facciamo una lista con tutte le vasche
		# checckate nel menu.. quindi da disegnare
		for i in self.menu.get_children():
			if i.active:
				vasche.append (i.get_children()[0].get_text())
		
		# Mettiamo in una lista i vari valori da plottare
		# tipo gh kh se sono ovviamenti checckati nelle
		# varie checkbox

		# Tipo se seleziono il primo e il secondo controllo
		# avro [0, 1]
		for i in self.checks:
			if i.get_active ():
				to_plot.append (self.checks.index (i))

		# Ed ecco qui la cosa piu' assurda mai fatta
		for i in to_plot:
			for n in vasche:
				temp = []
				
				for y in utils.get ("SELECT * FROM test WHERE vasca = '%s'" % n.replace("'", "''")):
					temp2 = []
					
					temp2.append (y[1]) # data
					temp2.append (y[2]) # nome
					temp2.append (y[i+3]) # valore (offset del cazzo +2 .. +1 perche' conta da 0)

					# temp2 = [u'03/06/2007', u'asdad', 0.69999999999999996]
					temp.append (temp2)
				
				if len (temp) != 0:
					data.append (i)
					data.append (temp)
		
		del to_plot
		
		if data:
			self.plot (data)
	
	def on_popup (self, widget, event):
		self.menu.popup (None, None, None, event.button, event.time)
		self.menu.show_all ()
	
	# Implementa un piccolo bubble sort "parallelo"
	def parallel_sort (self, dates, vals):
		for i in range (len (dates) - 1):
			for j in range (len (dates) - 1 - i):
				if dates[j+1] < dates[j]:
					tmp1 = dates[j]
					tmp2 = vals[j]
					
					dates[j] = dates[j+1]
					vals[j] = vals[j+1]
					
					dates[j+1] = tmp1
					vals[j+1] = tmp2
	
	def plot (self, values):
		
		window = gtk.Window ()
		window.set_title (_("PyAcqua - Grafico"))
		window.set_size_request (800, 600)
		
		window.figure = Figure ()#figsize=(6,4), dpi=72)
		window.axis = window.figure.add_subplot (111)
		
		window.canvas = FigureCanvasGTK(window.figure)
		
		sw = gtk.ScrolledWindow ()
		sw.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		sw.set_shadow_type (gtk.SHADOW_ETCHED_IN)
		sw.add_with_viewport (window.canvas)
		
		window.axis.clear ()		
		window.axis.grid(True)
		
		# [0, [[u'23/04/2006', u'Vasca Sala', 0.40000000000000002], [u'17/06/2006', u'Vasca Sala', 3.3999999999999999], [u'26/06/2006', u'Vasca Sala', 0.0]], 0, [[u'26/06/2006', u'Mia', 1.5000000000000002]], 1, [[u'23/04/2006', u'Vasca Sala', 1.6000000000000001], [u'17/06/2006', u'Vasca Sala', 1.6000000000000001], [u'26/06/2006', u'Vasca Sala', 1.6000000000000001]], 1, [[u'26/06/2006', u'Mia', 2.1000000000000005]]]
		
		
		labels = (_('pH'), _('KH'), _('GH'), _('NO2'), _('NO3'),
			_('Conducibilita'), _('Ammoniaca'), _('Ferro'), _('Rame'), _('Fosfati'),
			_('Calcio'), _('Magnesio'), _('Densita'))
		
		colors = ('r', 'g', 'y', 'b', 'c', 'm', 'k', 'w')
		color = 0
		
		label = values[0]
		dates = []
		valori = []
		
		limite_sup = 0
		limite_inf = 0

		for i in values:
			if type (i) == int:
				label = labels [i]
			else:
				for x in i:
					dt = x[0].split ('/')
					dates.append (datetime.date (int (dt[2]), int (dt[1]), int (dt[0])))
					valori.append (x[2])
				
				if color == 8:
					color = 0
					
				# Sort su dates
				self.parallel_sort (dates, valori)
				
				
				if limite_inf > valori[0]:
					limite_inf = valori[0]
				if limite_sup < valori[len(valori)-1]:
					limite_sup = valori[len(valori)-1]
				
				
				window.axis.plot_date (date2num (dates), valori, colors[color] + 'o--', label="%s %s" % (x[1], label))
				valori = []; dates = []
				color += 1
		
		# In caso si usi l'inglese meglio %m-%d
		window.axis.xaxis.set_major_formatter (DateFormatter(_('%d/%m')))
		window.axis.autoscale_view ()
		
		limite_sup += 2
		limite_inf -= 2
		
		window.axis.set_ylim (limite_inf, limite_sup)
		
		window.axis.legend ()
		window.canvas.draw ()
		
		bb = gtk.HButtonBox ()
		bb.set_layout (gtk.BUTTONBOX_END)
		
		btn = gtk.Button (stock=gtk.STOCK_SAVE)
		btn.connect ('clicked', self.on_save, window)
		btn.set_relief (gtk.RELIEF_NONE)
				
		bb.pack_start (btn)
		
		btn = gtk.Button (stock=gtk.STOCK_CLOSE)
		btn.connect ('clicked', self.exit, window)
		btn.set_relief (gtk.RELIEF_NONE)
		
		bb.pack_start (btn)
		
		vbox = gtk.VBox (False, 2)
		vbox.pack_start (sw, True, True, 0)
		vbox.pack_start (bb, False, False, 0)
		
		window.add (vbox)
		
		window.connect ('delete_event', self.exit, window)
		window.show_all()
	
	def on_save (self, widget, window):
		ret = utils.FileChooser (_("Salva Grafico..."), window, None, True, gtk.FILE_CHOOSER_ACTION_SAVE).run ()
		window.figure.savefig (ret)
		
	def exit (self, widget, window, unz=None):
		if unz:
			window = unz
		
		window.hide ()
		window.destroy ()

class Test (dbwindow.DBWindow):
	Chart = True
	def __init__ (self): 
		# id integer, date DATE, vasca FLOAT, ph FLOAT, kh FLOAT, gh
		# NUMERIC, no NUMERIC, noo NUMERIC, con NUMERIC, amm NUMERIC, fe
		# NUMERIC, ra NUMERIC, fo NUMERIC
		
		# Una liststore piu' grande dubito che esista 
		lst = gtk.ListStore (
			int,	# ID
			str,	# DATA
			str,	# VASCA
			
			float,	# PH
			float,	# KH
			float,	# GH
			float,	# NO2
			float,	# NO3
			float,	# COND
			float,	# AMMO
			float,	# FERRO
			float,	# RAME
			float,	# FOSFATI
			
			float,	# calcio
			float,	# magnesio
			float,	# densita
			str,	# Limiti
			
			gtk.gdk.Color,	# PH
			gtk.gdk.Color,	# KH
			gtk.gdk.Color,	# GH
			gtk.gdk.Color,	# NO2
			gtk.gdk.Color,	# NO3
			gtk.gdk.Color,	# COND
			gtk.gdk.Color,	# AMMO
			gtk.gdk.Color,	# FERRO
			gtk.gdk.Color,	# RAME
			gtk.gdk.Color,	# FOSFATI
			gtk.gdk.Color,	# CALCIO
			gtk.gdk.Color,	# MAGNESIO
			gtk.gdk.Color)	# DENSITA'

		cols = [_('Id'), _('Data'), _('Vasca'), _('Ph'), _('Kh'), _('Gh'), _('No2'), _('No3'),
			_('Conducibilita\''), _('Ammoniaca'), _('Ferro'), _('Rame'), _('Fosfati'),
			_('Calcio'), _('Magnesio'), _('Densita\''), _('Limiti')]
		
		inst = [utils.DataButton (), utils.Combo ()]
		
		for i in range (13):
			spin = utils.FloatEntry ()
			spin.connect ('output', self._on_spin_change)
			inst.append (spin)
		
		inst.append (utils.Combo ()) # Combo per i limiti

		dbwindow.DBWindow.__init__ (self, 2, 7, cols, inst, lst, True) # different renderer
		
		# Scan sulle colonne
		for i in self.view.get_columns ()[3:16]:
			i.add_attribute (i.get_cell_renderers ()[0], 'cell_background-gdk', self.view.get_columns().index (i) + 14)
		
		
		gcolor[3] = self.get_style ().copy ().bg[gtk.STATE_NORMAL]

		self.set_title (_("Test"))
		self.set_size_request (600, 400)
		
		utils.set_icon (self)
		
		self.note.set_current_page (0)
		self.show_all ()
	
	def refresh_data (self, islocked):
		if islocked: return
		
		self.store.clear ()
		self.vars[1].clear_all ()
		self.vars[15].clear_all ()
		
		for y in utils.get ('select * from vasca'):
			self.vars[1].append_text (y[3])
			self.filter_menu.append (gtk.CheckMenuItem (y[3]))
		
		for y in utils.get ('select * from test'):
			self.store.append ([y[0], y[1], y[2], y[3], y[4],
					y[5], y[6], y[7], y[8], y[9], y[10], y[11], y[12], y[13], y[14], y[15], y[16],
					gcolor[2], gcolor[2], gcolor[2], gcolor[2], gcolor[2], gcolor[2], gcolor[2],
					gcolor[2], gcolor[2], gcolor[2], gcolor[2], gcolor[2], gcolor[2]])
		
		# Riempo con i limiti
		for y in impostazioni.get_names_of_collections ():
			self.vars[15].append_text (y)
		
		mod = self.view.get_model ()
		it = mod.get_iter_first ()
		
		while it != None:
			self._check_iterator (mod, it)
			it = mod.iter_next (it)
		
		
	def post_delete_event (self):
		app.App.p_window["test"] = None
	
	def _on_change_view (self, widget):
		id = widget.get_active ()
		
		if Test.Chart and id == 1:
			#self.on_draw_graph (None)
			self.note.set_current_page (id)
		else:
			self.note.set_current_page (id)
	
	def pack_before_button_box (self, hb):
		cmb = utils.Combo ()
		
		cmb.append_text (_("Modifica"))
		
		if Test.Chart:
			cmb.append_text (_("Grafico"))
		
		cmb.append_text (_("Impostazioni"))
		
		cmb.set_active (0)
		
		cmb.connect ('changed', self._on_change_view)
		
		align = gtk.Alignment (0, 0.5)
		align.add (cmb)
		
		hb.pack_start (align, False, True, 0)
		
		if not Test.Chart:
			label = gtk.Label (_("<i>E' necessario matplotlib per i grafici.</i>"))
			label.set_use_markup (True)
			label.set_alignment (0, 0.5)
			hb.pack_start (label, False, True, 0)
		
		cmb.show ()
	
	def custom_page (self, edt_frame):
		import inserisci
		#import manutenzione
		self.note = gtk.Notebook ()
		
		self.note.set_show_tabs (False)
		self.note.set_show_border (False)
		
		self.note.append_page (edt_frame)
		
		if Test.Chart:
			self.grapher = GraphPage ()
			self.note.append_page (self.grapher)
		
		self.note.append_page (inserisci.Inserisci ())
		#self.note.append_page (manutenzione.Manutenzione ())
		
		return self.note
		
	def after_refresh (self, it):
		mod, it = self.view.get_selection().get_selected()

		id = mod.get_value (it, 0)
		
		data = self.vars[0].get_text ()
		vasca = self.vars[1].get_text ()
		ph = self.vars[2].get_text ()
		kh = self.vars[3].get_text ()
		gh = self.vars[4].get_text ()
		no = self.vars[5].get_text ()
		no2 = self.vars[6].get_text ()
		cond = self.vars[7].get_text ()
		ammo = self.vars[8].get_text ()
		ferro = self.vars[9].get_text ()
		rame = self.vars[10].get_text ()
		fosfati = self.vars[11].get_text ()
		calcio = self.vars[12].get_text ()
		magnesio = self.vars[13].get_text ()
		densita = self.vars[14].get_text ()
		limiti = self.vars[15].get_text ()
		
		utils.cmd("update test set date='%(data)s', vasca='%(vasca)s', ph='%(ph)s', kh='%(kh)s', gh='%(gh)s', no='%(no)s', noo='%(no2)s', con='%(cond)s', amm='%(ammo)s', fe='%(ferro)s', ra='%(rame)s', fo='%(fosfati)s', calcio='%(calcio)s', magnesio='%(magnesio)s', densita='%(densita)s', limiti='%(limiti)s' where id=%(id)s" % vars ())
		
		self.update_status (dbwindow.NotifyType.SAVE, _("Row Aggiornata (ID: %d") % id)
		
		self._check_iterator (mod, it)

	def add_entry (self, it):
		mod, id = self.view.get_selection ().get_selected ()
		mod = self.store

		id = mod.get_value (it, 0)
		
		utils.cmd ('insert into test values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', id,
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
				self.vars[12].get_text (),
				self.vars[13].get_text (),
				self.vars[14].get_text (),
				self.vars[15].get_text ()
		)

		self.update_status(dbwindow.NotifyType.ADD, _("Row aggiunta (ID: %d)") % id)
		
		self._check_iterator (mod, it)
		
	def remove_id (self, id):
		utils.cmd ('delete from test where id=%d' % id)
		self.update_status(dbwindow.NotifyType.DEL, _("Row rimossa (ID: %d)" % id))
	
	def decrement_id (self, id):
		utils.cmd ('update test set id=%d where id=%d' % (id - 1, id))
	
	def _on_spin_change (self, widget):
		id = self.vars.index (widget)
		id -= 2
		
		if id < 16:
			mod, it = self.view.get_selection ().get_selected ()
			
			if it == None: return
			
			checks = impostazioni.get_collection (mod.get_value (it, 16))
			# Nessun filtro selezionato! (colonna limiti)
			if checks == None: return

			keys = ('ph', 'kh', 'gh', 'no2', 'no3', 'con', 'am', 'fe', 'ra', 'fo', 'cal', 'mag', 'den')
			
			# Resettiamo il colore iniziale
			widget.modify_bg (gtk.STATE_NORMAL, gcolor[3])
			
			if not checks.has_key (keys[id]):
				widget.set_sensitive (False)
				return
			else:
				widget.set_sensitive (True)
			
			check = checks [keys [id]]
			
			val = widget.get_value ()
			
			if check[0] == None and check[1] == None:
				widget.set_sensitive (False)
				return
			else:
				widget.set_sensitive (True)
			
			if val < check[0]:
				widget.modify_bg (gtk.STATE_NORMAL, gcolor[0])
			elif val > check[1]:
				widget.modify_bg (gtk.STATE_NORMAL, gcolor[1])
			else:
				widget.modify_bg (gtk.STATE_NORMAL, gcolor[2])

	def _on_draw_graph (self, widget):
		if Test.Chart:
			mod, it = self.view.get_selection ().get_selected ()
			
			if it == None: return
			
			x = 0
			lst = [None,] * 13
			
			for i in range (13):
				if self.store.get_column_type (i + 3).pytype == gtk.gdk.Pixbuf:
					#utils.debug ("image is %s" % mod.get_value (it, self.last + x))
					lst[i] = mod.get_value (it, self.last + x)
					x += 1
				else:
					lst[i] = mod.get_value (it, i + 3)
			
			self.grapher.plot (lst)
	
	def _check_iterator (self, mod, it):
		# TODO: implementare i valori ideali
		
		if it == None: return

		if type (mod) != gtk.ListStore:
			it = mod.convert_iter_to_child_iter (it)
			mod = self.store
		
		checks = impostazioni.get_collection (mod.get_value (it, 16))
		
		if checks == None: return
		
		keys = ('ph', 'kh', 'gh', 'no2', 'no3', 'con', 'am', 'fe', 'ra', 'fo', 'cal', 'mag', 'den')
		x = 0
		
		for i in keys:
			if checks.has_key (i):
				val = mod.get_value (it, x + 3)
				
				if val < checks[i][0]:
					mod.set_value (it, x + 14 + 3, gcolor[0])
				elif val > checks[i][1]:
					mod.set_value (it, x + 14 + 3, gcolor[1])
				#elif val == checks[i][2]:
				#	utils.debug ("Ideal value")
				else:
					mod.set_value (it, x + 14 + 3, gcolor[2])
			x += 1
			
		
	def filter_func (self, mod, iter):
		filters = list ()
		for i in self.filter_menu.get_children ():
			if i.active:
				filters.append (i.get_children ()[0].get_text ())
		
		if filters == []:
			return True
		
		val = mod.get_value (iter, 2)
		
		if not val:
			return True
		
		if val in filters:
			return True
		else:
			return False

try:
	# TODO: implementa il caching delle import
	import matplotlib
	matplotlib.use ('GTKAgg')
	from matplotlib.figure import Figure
	from matplotlib.axes import Subplot
	from matplotlib.backends.backend_gtk import FigureCanvasGTK, NavigationToolbar
	from matplotlib.numerix import arange
	from matplotlib.dates import YEARLY, DateFormatter, rrulewrapper, RRuleLocator, drange, date2num
	Test.Chart = True
except:
	Test.Chart = False
