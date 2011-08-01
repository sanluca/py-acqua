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
import random
import os.path
import utils
from impostazioni import get, set, save

class TipsDialog(gtk.Dialog):
	exist = False
	def __init__(self):

		# Controlliamo l'esistenza di un'altra istanza
		
		if not TipsDialog.exist:
			TipsDialog.exist = True
		else:
			return
		
		gtk.Dialog.__init__(self, _("Tips of the Day"), None, gtk.DIALOG_NO_SEPARATOR,
			(gtk.STOCK_OK, gtk.RESPONSE_OK, gtk.STOCK_GO_FORWARD, gtk.RESPONSE_NONE))
		
		
		self.textview = gtk.TextView()
		self.textview.set_wrap_mode(gtk.WRAP_WORD)
		self.textbuffer = self.textview.get_buffer()
		
		utils.set_icon (self)
		
		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)

		sw.add(self.textview)
		
		self.vbox.pack_start(sw)

		self.check = gtk.CheckButton(_('Non mostrare al prossimo avvio'))
		
		if get ("show_tips"):
			self.check.set_active(False)
		else:
			self.check.set_active(True)
		
		self.vbox.pack_start(self.check, False, False, 0)

		self.connect('response', self._on_response)
		self._tip()
		
		self.set_size_request(400, 250)
		self.show_all()
	
	def _on_response(self, dialog, rsp_id):
		if rsp_id == gtk.RESPONSE_NONE:
			self._tip()
		if rsp_id == gtk.RESPONSE_OK:
			self.hide()
			
			if self.check.get_active():
				set ("show_tips", False)
			else:
				set ("show_tips", True)
			
			save()
			
			self.destroy()
			
			TipsDialog.exist = False
	
	def _tip(self):

#FIXME: il file dei tips e' codificato male
#		if get ("lang").lower() == "en":
#			tip_file = open(os.path.join('src', 'tip_of_the_day_en.txt'), 'r')
#		else:
		#FIXME: probabilmente bug qui
		tip_file = open(os.path.join (utils.DHOME_DIR, os.path.join('tips', 'tip_of_the_day.txt')),'r')
	
		testo = tip_file.read()
		
		tip_file.close()
		
		lista_tips = testo.split('&')
		x = random.randint(0, len(lista_tips) - 1)
		
		testo = lista_tips[x] + _("\n\nDalle FAQ di it.hobby.acquari http://www.maughe.it/faq/faq.htm")
		
		self.textbuffer.set_text(testo)
