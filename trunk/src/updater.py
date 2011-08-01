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
import httplib
import threading
import generate
import app
import utils
import os
import os.path
import sys

from xml.dom.minidom import parseString, getDOMImplementation
from updater.database import DatabaseWrapper

REPOSITORY_ADDRESS = None
BASE_DIR = None
LIST_FILE = None

if os.name == 'nt':
	REPOSITORY_ADDRESS = "www.pyacqua.net"
	REPOSITORY_ADDRESS = "localhost"
	BASE_DIR = "/update/windows/"
	LIST_FILE = "/update/win32-list.xml"
else:
	REPOSITORY_ADDRESS = "www.pyacqua.net"
	BASE_DIR = "/update/source/"
	LIST_FILE = "/update/source-list.xml"

DB_FILE = "pyacqua.db"
XML_FILE = "pyacqua.xml"

#REPOSITORY_ADDRESS = r"localhost"
#BASE_DIR = r"/~stack/update/source/"
#LIST_FILE = r"/~stack/update/source-list.xml"

class SchemaUpdateInterface(object):
	def __init__(self, data):
		doc = parseString(data)
		
		self.info = {
			"mainversion" : 	[None, int],
			"secondversion" : 	[None, int],
			"revision" : 		[None, int],
			"message" : 		[None, str]
		}
		
		self.arrays = {
			"downloads" : {
				"svn" : 	[],
				"windows" : 	[],
				"tarball" : 	[]
			},
			"actions" : {
				"pre" : 	[],
				"post" : 	[]
			},
			"mirrors" : {
				"url" : 	[]
			}
		}
		
		self.program = None # il database sara' => "%s/%s-update.db" % (mirrors[0], self.program)

		if doc.documentElement.tagName.lower().endswith("-update"):
			self.program = doc.documentElement.tagName[:-7]

		if self.program == None:
			raise Exception("No such program")
		
		for node in doc.documentElement.childNodes:
			if node.nodeName.lower() == "info":
				self.__parseInfo(node)
			elif node.nodeName.lower() == "mirrors" or node.nodeName.lower() == "actions" or node.nodeName.lower() == "downloads":
				self.__parseArray(node, node.nodeName.lower())
	
	def __parseInfo(self, node):
		for i in node.childNodes:
			if i.nodeName.lower() in self.info.keys():
				converter = self.info[i.nodeName.lower()][1]
				self.info[i.nodeName.lower()][0] = converter((i.lastChild) and(i.lastChild.data) or(None))
	
	def __parseArray(self, node, category):
		kittie_cat = self.arrays[category]
		print kittie_cat, category
		
		for i in node.childNodes:
			print i.nodeName, kittie_cat.keys()
			
			if i.nodeName.lower() in kittie_cat.keys():
				kittie_cat[i.nodeName.lower()].append(i.lastChild.data)
	
	def getInfo(self, id):
		if id in self.info:
			return self.info[id]
		return None
	
	def getList(self, cat, subcat):
		if cat in self.arrays:
			if subcat in self.arrays[cat]:
				return self.arrays[cat][subcat]
		return None
	
	def getProgramName(self):
		return self.program
	
	def checkDiff(self, other):
		"""
		Ritorna:
			3 se le versioni sono incompatibili
			2 se le versioni sono potenzialmente compatibile
			1 se le verrsioni sono compatibili
			0 se le versioni sono identiche
		"""
		o_m, o_s, o_r = other.getInfo("mainversion"), other.getInfo("secondversion"), other.getInfo("revision")
		c_m, c_s, c_r = self.getInfo("mainversion"), self.getInfo("secondversion"), self.getInfo("revision")
		
		if o_m == m and o_s == s and o_r == r: return 0
		if o_m != m: return 3
		else:
			if o_s != s: return 2
			if o_r != r: return 1
	
	def getCurrentSchema():
		return SchemaUpdate(os.path.join(utils.DHOME_DIR, "pyacqua.xml"))
	
	getCurrentSchema = staticmethod(getCurrentSchema)

class Fetcher(threading.Thread):
	
	def __init__(self, callback, url):
		self.data = None
		self.callback = callback
		self.url = url
		threading.Thread.__init__(self, name="Fetcher")

	def run(self):
		try:
			self.response = None; self.data = None
			try:
				conn = httplib.HTTPConnection(REPOSITORY_ADDRESS)
				conn.request("GET", self.url)
				self.response = conn.getresponse()
				self.data = self.response.read()
			except:
				print _("!! Errore mentre scaricavo da %s") % self.url
		finally:
			gobject.idle_add(self.__onData)

	def __onData(self):
		gtk.gdk.threads_enter()
		
		try:
			self.callback(self.data, self.response)
		finally:
			gtk.gdk.threads_leave()
		
		return False

if not _:
	_ = lambda x: x

class WebUpdater(gtk.Assistant):
	def __init__(self):
		gtk.Assistant.__init__(self)

		self.createIntro()
		self.createChoice()
		self.createSummary()

		self.set_title(_("PyAcqua: Aggiornamento"))
		self.show_all()
	
	def createIntro(self):
		tbl = self.createNewPage(
			gtk.ASSISTANT_PAGE_INTRO,
			_("Il wizard ti guidera' durante l'aggiornamento di pyacqua."),
			gtk.Table(2, 1)
		)

		tbl.attach(
			gtk.Label(_("Per controllare la presenza di aggiornamenti premere il bottone sotto.")),
			0, 1, 0, 1,
			xoptions=gtk.SHRINK | gtk.EXPAND
		)
		
		btn = utils.new_button("Controlla Aggiornamenti.", gtk.STOCK_REFRESH)
		btn.connect('clicked', self.onCheckUpdateCallback)
		tbl.attach(btn, 0, 1, 1, 2, xoptions=gtk.SHRINK | gtk.EXPAND, yoptions=gtk.SHRINK | gtk.EXPAND)
		
		tbl.show_all()

	def createChoice(self):
		vbox = self.createNewPage(
			gtk.ASSISTANT_PAGE_CONTENT,
			_("Seleziona i componenti da aggiornare")
		)
		vbox.pack_start(gtk.Label("..."))
		vbox.show_all()
	
	def createSummary(self):
		self.riepilogo = self.createNewPage(
			gtk.ASSISTANT_PAGE_SUMMARY,
			_("Riepilogo aggiornamento")
		)
		self.riepilogo_label = gtk.Label("")
		self.riepilogo.pack_start(self.riepilogo_label)
		self.riepilogo.show_all()
	
	def createNewPage(self, type, title, _entry=None):
		if not _entry: vbox = gtk.VBox()
		else: vbox = _entry
		
		self.append_page(vbox)
		self.set_page_title(vbox, title)
		self.set_page_type(vbox, type)
		self.set_page_header_image(vbox, utils.LOGO_PIXMAP)
		self.set_page_side_image(vbox, utils.LOGO_PIXMAP)
		self.set_page_complete(vbox, True)
		return vbox
	
	def _thread(self, callback, url):
		print _(">> Creo un thread per %s") % url
		f = Fetcher(callback, REPOSITORY_ADDRESS + url)
		f.setDaemon(True)
		f.start()
	
	def onCheckUpdateCallback(self, widget):
		# TODO: metti il bottone insensitive e poi ripristinalo
		#       magari implementa una barra di stato che scoore
		#       o una label che mostra i puntini animati ecc...
		self._thread(self.onCheckUpdate, LIST_FILE)

	def onCheckUpdate(self, data, response):
		# TODO: controlla gli altri stati e se la response != 200
		#       blocca l'aggiornamento e porta alla pagine di 
		#       riepilogo con un warning
		if response.status != 200:
			self.riepilogo_label.set_text(_("Impossibile scaricare la lista degli aggiornamenti"))

		try:
			new_schema = SchemaUpdateInterface(parseString(data))
			old_schema = SchemaUpdateInterface.getCurrentSchema()
			
			if ret == 0:
				self.riepilogo_label.set_text(_("Nessun aggiornamento disponibile."))
			if ret == 1:
				# versioni compatibili possiamo aggiornare
				self.__checkFileToUpdate(new_schema)
			if ret == 2:
				# TODO: Una choice ..
				# come una clean install
				utils.warning(_("Le versioni sono potenzialmente compatibili\nma _NON_ viene garantito il perfetto aggiornamento"))
				pass
			if ret == 3:
				utils.error(_("Versioni incompatibili per procedere con l'aggiornamento"))
				pass
		except:
			utils.error(_("Impossibile interpretare il file xml"))
			return

if __name__ == "__main__":
	WebUpdater()
	gtk.main()
