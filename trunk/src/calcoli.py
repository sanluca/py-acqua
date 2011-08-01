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
import app
import utils

report_dolce = """
Vasca:                     %s
Lunghezza:                 %s
Larghezza:                 %s
Altezza:                   %s
Volume:                    %s
Piante inseribili:         %s
Numero pesci 3/4 cm:       %s
Numero pesci 5/6 cm:       %s
Watt piante esigenti:      %s
Watt piante poco esigenti: %s
"""

report_marino = """
Vasca:                     %s
Lunghezza:                 %s
Larghezza:                 %s
Altezza:                   %s
Volume:                    %s
Luce vasche pesci:         %s
Luce coralli molli:        %s
Luce coralli duri:         %s
Totale l/h in movimento:   %s
Quantita sabbia per dsb:   %s
"""

class Calcoli(gtk.Window):
	def __init__(self): 
		gtk.Window.__init__(self)
		
		self.set_title(_("Calcoli"))
		self.set_resizable(False)
		
		utils.set_icon (self)
		
		vbox = gtk.VBox()
		vbox.set_spacing(4)
		vbox.set_border_width(4)
		
		# I due frame
		f1 = gtk.Frame(_('Valori')); f2 = gtk.Frame(_('Risultati'))
		
		# Pacchiamoli...
		vbox.pack_start(f1, False, False, 0)
		vbox.pack_start(f2, False, False, 0)
		
		# Tabella per i valori
		tbl_valori = gtk.Table(3, 2)
		tbl_valori.set_border_width(4)
		tbl_valori.set_row_spacings(4)
		
		# Le varie label
		tbl_valori.attach(utils.new_label(_("Vasca:")), 0, 1, 0, 1)
		tbl_valori.attach(utils.new_label(_("Lunghezza in cm:")), 0, 1, 1, 2)
		tbl_valori.attach(utils.new_label(_("Larghezza in cm:")), 0, 1, 2, 3)
		tbl_valori.attach(utils.new_label(_("Altezza in cm:")), 0, 1, 3, 4)
		
		# ComboBox
		self.e_vasca = utils.Combo()
		self.e_vasca.append_text(_("Dolce"))
		self.e_vasca.append_text(_("Marino"))
		self.e_vasca.set_active(0)

		# Quando si sceglie marino o dolce invochiamo aggiorna()
		self.e_vasca.connect('changed', self._on_change_vasca)
		
		# Creiamo le entry per la tabella valori
		self.e_altezza, self.e_lunghezza, self.e_larghezza = gtk.Entry(), gtk.Entry(), gtk.Entry()
		
		tbl_valori.attach(self.e_vasca, 1, 2, 0, 1, yoptions=0)
		tbl_valori.attach(self.e_lunghezza, 1, 2, 1, 2, yoptions=0)
		tbl_valori.attach(self.e_larghezza, 1, 2, 2, 3, yoptions=0)
		tbl_valori.attach(self.e_altezza, 1, 2, 3, 4, yoptions=0)
		
		# Creiamo un notebook di due schede contenenti le diverse
		# tabelle (per dolce e marino)
		self.notebook = gtk.Notebook()
		self.notebook.set_show_tabs(False)
		self.notebook.set_show_border(False)

		# Creiamo la tabella per il tipo Dolce
		tbl = gtk.Table(6, 2)
		tbl.set_border_width(4)
			
		self.dlc_volume = utils.new_label('0', False, labelCopy=_("Volume: %s"))
		self.dlc_piante_inseribili = utils.new_label('0', False, labelCopy=_("Piante inseribili: %s"))
		self.dlc_num_pesci_3_4 = utils.new_label('0', False, labelCopy=_("Numero di pesci 3-4 cm: %s"))
		
		tbl.attach(utils.new_label(_("Volume:")), 0, 1, 0, 1)
		tbl.attach(utils.new_label(_("Piante Inseribili:")), 0, 1, 1, 2)
		tbl.attach(utils.new_label(_("Numero di pesci 3-4 cm:")), 0 ,1, 2, 3)
		
		tbl.attach(self.dlc_volume, 1, 2, 0, 1)
		tbl.attach(self.dlc_piante_inseribili, 1, 2, 1, 2)
		tbl.attach(self.dlc_num_pesci_3_4, 1, 2, 2, 3)
		
		tbl.attach(utils.new_label(_("Numero di pesci 5-6 cm:")), 0, 1, 3, 4)
		tbl.attach(utils.new_label(_("Watt per piante esigenti:")), 0, 1, 4, 5)
		tbl.attach(utils.new_label(_("Watt per piante poco esigenti:")), 0, 1, 5, 6)
		
		self.dlc_num_pesci_5_6 = utils.new_label('0', False, labelCopy=_("Numero di pesci 5-6 cm: %s"))
		self.dlc_watt_esigenti = utils.new_label('0', False, labelCopy=_("Watt per piante esigenti: %s"))
		self.dlc_watt_poco_esigenti = utils.new_label('0', False, labelCopy=_("Watt per piante poco esigenti: %s"))
		
		tbl.attach(self.dlc_num_pesci_5_6, 1, 2, 3, 4)
		tbl.attach(self.dlc_watt_esigenti, 1, 2, 4, 5)
		tbl.attach(self.dlc_watt_poco_esigenti, 1, 2, 5, 6)

		box = gtk.VBox()
		box.pack_start(tbl, False, False, 0)

		# Aggiungiamo la table per il tipo dolce alla notebook
		self.notebook.append_page(box, None)

		# Creiamo la table per il tipo marino
		tbl = gtk.Table(2, 2)
		tbl.set_border_width(4)
		#tbl.set_row_spacings(4)
		
		self.mar_volume = utils.new_label('0', False, labelCopy=_("Volume %s"))
		self.luce_vasche_pesci = utils.new_label('0', False, labelCopy=_("Luce per vasche di pesci: %s"))
		self.luce_coralli_molli = utils.new_label('0', False, labelCopy=_("Luce per coralli molli: %s"))
		self.luce_coralli_duri = utils.new_label('0', False, labelCopy=_("Luce per coralli duri: %s"))
		self.totale_litri_movimento = utils.new_label('0', False, labelCopy=_("Totale l/h in movimento"))
		self.quantita_sabbia_dsb = utils.new_label('0', False, labelCopy=_("Quantita' di sabbia per dsb: %s"))
		
		tbl.attach(utils.new_label(_("Volume:")), 0, 1, 0, 1)
		tbl.attach(utils.new_label(_("Luce per vasche di pesci:")), 0, 1, 1, 2)
		tbl.attach(utils.new_label(_("Luce per coralli molli:")), 0, 1, 2, 3)
		tbl.attach(utils.new_label(_("Luce per coralli duri:")), 0, 1, 3, 4)
		tbl.attach(utils.new_label(_("Totale l/h in movimento:")), 0, 1, 4, 5)
		tbl.attach(utils.new_label(_("Quantita di sabbia per dsb:")), 0, 1, 5, 6)
		
		
		tbl.attach(self.mar_volume, 1, 2, 0, 1)
		tbl.attach(self.luce_vasche_pesci, 1, 2, 1, 2)
		tbl.attach(self.luce_coralli_molli, 1, 2, 2, 3)
		tbl.attach(self.luce_coralli_duri, 1, 2, 3, 4)
		tbl.attach(self.totale_litri_movimento, 1, 2, 4, 5)
		tbl.attach(self.quantita_sabbia_dsb, 1, 2, 5, 6)
		
		
		# Da definire cosa aggiungere.. ecc :p

		box = gtk.VBox()
		box.pack_start(tbl, False, False, 0)

		# Aggiungiamo la table per il tipo marino alla notebook
		self.notebook.append_page(box, None)

		# Pacchiamo la tabella dei valori
		f1.add(tbl_valori)

		# .. e la notebook
		f2.add(self.notebook)
		
		bb = gtk.HButtonBox()
		bb.set_layout(gtk.BUTTONBOX_END)
		
		btn = gtk.Button(stock=gtk.STOCK_REFRESH)
		btn.connect('clicked', self._on_refresh)
		bb.pack_start(btn)

		btn = gtk.Button(stock=gtk.STOCK_COPY)
		btn.connect('clicked', self._on_copy)
		bb.pack_start(btn)
		
		vbox.pack_start(bb, False, False, 0)
		
		self.add(vbox)
		
		self.connect ('delete-event', self._on_delete_event)
		
		self.show_all()
	
	def _on_delete_event (self, widget, event):
		app.App.p_window["calcoli"] = None
		
	def _on_refresh(self, widget):
		
		# FIXME: i nomi delle variabili sono da cambiare...
		# tipo self.dlc_volume robe del genere :p
		#if True: return

		try:
			a = int(self.e_larghezza.get_text())
			b = int(self.e_lunghezza.get_text())
			c = int(self.e_altezza.get_text())
			
		except ValueError:
			a = 0
			b = 0
			c = 0
			#Finestra dialog con errore
		
		e = a*b*c/1000
		f = b*a/50
		g = e/(1.5*4)
		h = e / (3*6)
		i = e*0.5
		l = e*0.35
		m = e*1.5
		n = e*10
		o = (a*b*12/1000)*1.33

		self.dlc_volume.set_text(str(e))
		self.dlc_piante_inseribili.set_text(str(f))
		self.dlc_num_pesci_3_4.set_text(str(g))
		self.dlc_num_pesci_5_6.set_text(str(h))
		self.dlc_watt_esigenti.set_text(str(i))
		self.dlc_watt_poco_esigenti.set_text(str(l))
		
		self.mar_volume.set_text(str(e))
		self.luce_vasche_pesci.set_text(str(i))
		self.luce_coralli_molli.set_text(str(e))
		self.luce_coralli_duri.set_text(str(m))
		self.totale_litri_movimento.set_text(str(n))
		self.quantita_sabbia_dsb.set_text(str(o))

	def _on_copy (self, widget):
		clip = gtk.Clipboard(selection='CLIPBOARD')

		if self.e_vasca.get_active () == 0:
			s = report_marino % ("Marina",
				self.e_lunghezza.get_text(),
				self.e_larghezza.get_text(),
				self.e_altezza.get_text(),
				self.mar_volume.get_text(),
				self.luce_vasche_pesci.get_text(),
				self.luce_coralli_molli.get_text(),
				self.luce_coralli_duri.get_text(),
				self.totale_litri_movimento.get_text(),
				self.quantita_sabbia_dsb.get_text()
			)
		elif self.e_vasca.get_active () == 1:
			s = report_dolce % ("Dolce",
				self.e_lunghezza.get_text(),
				self.e_larghezza.get_text(),
				self.e_altezza.get_text(),
				self.dlc_volume.get_text(),
				self.dlc_piante_inseribili.get_text(),
				self.dlc_num_pesci_3_4.get_text(),
				self.dlc_num_pesci_5_6.get_text(),
				self.dlc_watt_esigenti.get_text(),
				self.dlc_watt_poco_esigenti.get_text()
			)

		clip.set_text (s)
	
	def _pulisci_calcoli(self, obj):
		#self.entry1.set_text("")
		#self.entry2.set_text("")
		#self.entry3.set_text("")
		pass
			
	def _on_change_vasca(self, widget):
		self.notebook.set_current_page(self.e_vasca.get_active())
