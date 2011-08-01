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
from updater.database import DatabaseWrapper, DatabaseReader
from updater.xmlreport import ReportReader, Indexer

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

REPOSITORY_ADDRESS = r"localhost"
#BASE_DIR = r"/~stack/update/source/"
#LIST_FILE = r"/~stack/update/source-list.xml"

class Fetcher(threading.Thread):
	
	def __init__(self, callback, url, args=None):
		self.data = None
		self.callback = callback
		self.url = url
		self.args = args
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
			self.callback(self.data, self.response, self.args)
		finally:
			gtk.gdk.threads_leave()
		
		return False


_ = lambda x: x

COL_ICON = 0
COL_FILE = 1
COL_NREV = 2
COL_OREV = 3
COL_BYTE = 4
COL_PERC = 5
COL_TOGG = 6
COL_COLO = 7

class UpdateEngine(object):
	NORMAL_UPDATE = 0
	FORCED_UPDATE = 1
	CUSTOM_UPDATE = 2
	
	def __init__(self, database="old.db"):
		self.new_db = None
		self.old_db = DatabaseReader(None, database)
		
		self.locked = False
		
		#self.startThread(self.dumpDB, "/~stack/pyupdate/pyacqua.db")
		#self.startThread(self.listInfo, "/~stack/pyupdate/index.xml")
	
	def reportError(self, data, response, args, where):
		"""Ovverride this method"""
		self.lockInterface(False)
	
	def lockInterface(self, lock=True):
		"""Ovverride this method"""
		pass
	
	def fetchComponents(self, callback):
		"""
		callback:
		
		for i in report.programs:
			print "-> %s" % i
			self.startThread(self.dumpXml, "/~stack/pyupdate/%s-update.xml" % i, i)
		"""
		self.startThread(self.__listInfo, "/~stack/pyupdate/index.xml", callback)
	
	def startThread(self, callback, url, args=None):
		print _(">> Creo un thread per %s") % url
		f = Fetcher(callback, url, args)
		f.setDaemon(True)
		f.start()
	
	def __listInfo(self, data, response, args):
		if data == None or response.status != 200:
			return self.reportError(data, response, args, STEP_INDEX)
		
		args(Indexer(data).programs)
	
	def getVersion(self, schema):
		a = (schema.get("mainversion"), schema.get("secondversion"), schema.get("revision"))
		return "-r".join((".".join(map(str,a[:2])), str(a[2])))
	
	def dumpXml(self, data, response, args):
		new_schema = ReportReader(data)
		old_schema = ReportReader(None, os.path.join(utils.DHOME_DIR, "%s.xml" % args))
		
		ret = old_schema.checkDiff(new_schema)
		
		if ret == 0: print "NO_UPDATE"
		elif ret == 1: print "UPDATE"
		elif ret == 2: print "UNSECURE_UPDATE"
		elif ret == 3: print "IMPOSSIBLE"
		
		print "LOCAL version:  %s" % self.getVersion(old_schema)
		print "REMOTE version: %s" % self.getVersion(new_schema)
		
		self.updateProgram(args)
	
	def __updateFirstPass(self, program, u_type, new_pid, old_pid):
		
		# @update standard@ - second pass - soggetto new_db
		# Controlliamo l'esistenza della stessa dir
		# -> se nn c'e' aggiungiamo tutti i file
		# Se esiste
		#    -> controlliamo la revision (se la nuova e' maggiore altrimenti ignore (custom update precedente))
		#       -> for sui file
		#          controlla revision (se la nuova e' maggiore scarica | se minore nulla | se uguale controlla consistenza in caso riscarica)
		
		# @update forzato@ clone (update standard)
		# Controlliamo l'esistenza della stessa dir
		# -> se nn c'e' aggiungiamo tutti i file
		# Se esiste
		#    -> controlliamo la revision (se uguale ignore)
		#       -> for sui file
		#          controlla revision (se diversa riscarica | se uguale controlla consistenza in caso riscarica)
		
		for dir_entry in self.new_db.select("SELECT * FROM directory WHERE program_id=%d" % self.new_db.sanitize(new_pid)):
			# dir_entry => (idx, name, revision, filenum, pid)
			
			new_did, new_dname, new_drev, new_dfilenum, new_pid = dir_entry
			
			print "[1] Checking %s" % new_dname
			old_did, old_drev = self.old_db.getDirRevision(new_dname, old_pid)
			
			if u_type == Update.FORCED_UPDATE:
				if old_drev == new_drev:
					continue
			else: # TODO: add custom
				# Esiste e la revision e' maggiore o uguale
				if old_drev >= new_drev:
					print "[1] Skipping %d >= %d" % (old_drev, new_drev)
					continue
				
			#       -> for sui file
			#          controlla revision (se la nuova e' maggiore scarica | se minore nulla | se uguale controlla consistenza in caso riscarica)
			
			for file_entry in self.new_db.select("SELECT * FROM file WHERE program_id=%d AND directory_id=%d" % self.new_db.sanitize((new_pid, new_did))):
				# file_entry => (idx, name, revision, bytes, md5, did, pid)
				
				new_fid, new_fname, new_frev, new_fbytes, new_fmd5, new_did, new_pid = file_entry
				
				old_fid, old_frev = self.old_db.getFileRevision(new_fname, old_did, old_pid)
				
				if u_type == Update.FORCED_UPDATE:
					
					if old_frev == new_frev and self.old_db.checkConsistence(old_fid, new_frev, new_fbytes, new_fmd5):
						continue # il file e' ok
					elif old_frev != new_frev:
						self.downloadFile(old_fid, new_fname, new_frev, new_fbytes, new_fmd5)
					
				else: # TODO: add custom
					
					if (old_frev == new_frev and not self.old_db.checkConsistence(old_fid, new_frev, new_fbytes, new_fmd5)) or (old_frev < new_frev):
						self.downloadFile(old_fid, new_fname, new_frev, new_fbytes, new_fmd5)
	
	def __updateSecondPass(self, program, u_type, new_pid, old_pid):
		# @update standard@ - removing - soggetto old_db
		# Controlliamo se la dir non esiste
		#   -> Rimuoviamo la dir con tutti i file all'interno
		# se esiste
		#   -> for sui file
		#      se esite controlla md5 e bytes (versione minore | se maggiore non far nulla)
		#        -> se non ok riscarica (o errore di update sul server)
		#      se non esiste
		#        -> elimina file
		
		# @update forzato@ - removing - soggetto old_db
		# Controlliamo se la dir non esiste
		#   -> Rimuoviamo la dir con tutti i file all'interno
		# se esiste
		#   -> for sui file
		#      se esite controlla md5 e bytes (sempre)
		#        -> se non ok riscarica
		#      se non esiste
		#        -> elimina file

		for dir_entry in self.old_db.select("SELECT * FROM directory WHERE program_id=%d" % self.old_db.sanitize(old_pid)):
			old_did, old_dname, old_drev, old_dfilenum, old_pid = dir_entry
			
			print "[2] Checking %s" % old_dname
			new_did, new_drev = self.new_db.getDirRevision(old_dname, new_pid)
			
			if new_did == -1 and new_drev == -1:
				print "[2] Full removing %s (and all contents) ..." % old_dname
				continue
			
			for file_entry in self.old_db.select("SELECT * FROM file WHERE program_id=%d AND directory_id=%d" % self.new_db.sanitize((old_pid, old_did))):
				# file_entry => (idx, name, revision, bytes, md5, did, pid)
				
				old_fid, old_fname, old_frev, old_fbytes, old_fmd5, old_did, old_pid = file_entry
				
				new_fid, new_frev = self.new_db.getFileRevision(old_fname, new_did, new_pid)
				
				if new_fid == -1 and new_frev == -1:
					print "[2] Removing file %s ..." % old_fname
				else:
					if u_type == Update.FORCED_UPDATE:
						if not self.new_db.checkConsistence(new_fid, old_frev, old_fbytes, old_fmd5):
							print "[2] Consistence check failed for file %s." % old_fname
							# riscarica
							
					else: # TODO: add custom
						
						if new_frev <= old_frev and not self.new_db.checkConsistence(new_fid, old_frev, old_fbytes, old_fmd5):
							print "[2] Consistence check failed for file %s." % old_fname
	
	def updateProgram(self, program, u_type=NORMAL_UPDATE):
		if not self.new_db: raise "No db."
		
		new_pid = self.new_db.select("SELECT id FROM program WHERE name='%s'" % self.new_db.sanitize(program))[0][0]
		old_pid = self.old_db.select("SELECT id FROM program WHERE name='%s'" % self.old_db.sanitize(program))[0][0]
		
		print "Pid: old -> %d new -> %d" % (old_pid, new_pid)
		
		self.__updateFirstPass(program, u_type, new_pid, old_pid)
		self.__updateSecondPass(program, u_type, new_pid, old_pid)
	
	def downloadFile(self, file_id, fname, frev, fbytes, fmd5):
		self.startThread(self.checkConsistence, "/~stack/pyupdate/source/%s" % fname, (file_id, fname, frev, fbytes, fmd5))
	
	def checkConsistence(self, data, response, args):
		file_id, fname, frev, fbytes, fmd5 = args
		
		print "\t%s -> " % fname,
		
		if data == None:
			print "Error in recv."
			return

		if response.status != 200:
			print "Error in response."
			return
		
		if len(data) == fbytes and self.MD5(data) == fmd5:
			print "File is ok. merge."
			self.old_db.execute("UPDATE file SET revision=%d, bytes=%d, md5=\"%s\" WHERE id=%d" % self.sanitize((frev, fbytes, fmd5, file_id)))
		else:
			print "Error in file."
	
	def MD5(self, data):
		m = md5.new()
		m.update(data)
		return m.hexdigest()
	
	def dumpDB(self, data, response, args):
		f = open("tmp.database", "wb")
		f.write(data)
		f.close()
		
		self.new_db = DatabaseReader(None, "tmp.database")
		print "Database downloaded."

class WebUpdate(gtk.Window, UpdateEngine):
	def __init__(self):
		gtk.Window.__init__(self)
		UpdateEngine.__init__(self)
		
		utils.set_icon(self)
		self.set_title(_("Web Update"))
		self.set_size_request(600, 400)
		
		vbox = gtk.VBox(False, 2)
		
		self.nb = gtk.Notebook()
		vbox.pack_start(self.nb)
		
		self.status = gtk.Statusbar()
		vbox.pack_start(self.status, False, False, 0)
		
		self.add(vbox)
		
		self.connect('delete-event', self._on_delete_event)
		
		# ---------------------------------------------------------------------------------------
		
		self.store = gtk.TreeStore(
			gtk.gdk.Pixbuf, # icona
			str, # nome file
			str, # new_revision
			str, # old_revision
			int, # bytes
			int, # percentuale scaricamento
			bool, # da scaricare
			gtk.gdk.Color # colre di background
		)
		
		self.tree = gtk.TreeView(self.store)
		self.tree.append_column(gtk.TreeViewColumn("", gtk.CellRendererPixbuf(), pixbuf=0))

		rend = gtk.CellRendererText(); id = 1
		
		for i in (_("File"), _("New"), _("Current"), _("Bytes")):
			col = gtk.TreeViewColumn(i, rend, text=id)
			self.tree.append_column(col)
			id += 1
			
		# Colonna percentuale
		rend = gtk.CellRendererProgress()
		col = gtk.TreeViewColumn(_("%"), rend, value=COL_PERC)
		
		self.tree.append_column(col)
		
		# Background su tutte le celle
		for i in self.tree.get_columns():
			i.add_attribute(i.get_cell_renderers()[0], 'cell_background-gdk', COL_COLO)
		
		sw = gtk.ScrolledWindow()
		sw.add(self.tree)
		
		vbox = gtk.VBox(False, 2)
		vbox.pack_start(sw)
		
		bb = gtk.HButtonBox()
		bb.set_layout(gtk.BUTTONBOX_END)
		
		self.update_btn = btn = utils.new_button(_("Aggiorna"), gtk.STOCK_REFRESH)
		btn.connect('clicked', self._on_start_update)
		bb.pack_start(btn)

		btn.set_sensitive(False)

		self.get_btn = btn = utils.new_button(_("Controlla Aggiornamenti"), gtk.STOCK_APPLY)
		btn.connect('clicked', self.onGetList)
		bb.pack_start(btn)
		
		vbox.pack_start(bb, False, False, 0)
		
		self.nb.append_page(vbox)
		
		self.file = None
		self.it = None
		
		self.program_list = None
		
		self.icon_add = gtk.gdk.pixbuf_new_from_file(os.path.join(utils.DPIXM_DIR, "add.png"))
		self.icon_del = gtk.gdk.pixbuf_new_from_file(os.path.join(utils.DPIXM_DIR, "del.png"))
		self.icon_done = gtk.gdk.pixbuf_new_from_file(os.path.join(utils.DPIXM_DIR, "done.png"))
		self.icon_error = gtk.gdk.pixbuf_new_from_file(os.path.join(utils.DPIXM_DIR, "error.png"))
		self.icon_program = gtk.gdk.pixbuf_new_from_file(os.path.join(utils.DPIXM_DIR, "program.png"))
		
		self.color_add = gtk.gdk.color_parse('#70ef70')
		self.color_del = gtk.gdk.color_parse('#ff8080')
		self.color_done = gtk.gdk.color_parse('#bcfffc')
		self.color_error = gtk.gdk.color_parse('#ff9060')
		self.color_wait = gtk.gdk.color_parse('#ebebeb')
		
		# ---------------------------------------------------------------------------------------

		# Dobbiamo inserire una checklist per scegliere quali componenti aggiornare.
		# Quindi facciamo un for sulle entry del database locale per creare la lista
		# dei vari programmi.
		
		vbox = gtk.VBox(False, 2)
		
		self.choice_store = gtk.ListStore(
			gtk.gdk.Pixbuf, # icona
			str, # nome programma
			bool, # checked
		)
		
		self.choice_tree = gtk.TreeView(self.choice_store)
		
		col = gtk.TreeViewColumn("", gtk.CellRendererPixbuf(), pixbuf=0)
		col.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
		col.set_fixed_width(50)
		
		self.choice_tree.append_column(col)
		
		col = gtk.TreeViewColumn(_("Program"), gtk.CellRendererText(), text=1)
		col.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
		
		self.choice_tree.append_column(col)
		
		rend = gtk.CellRendererToggle()
		rend.connect('toggled', self.onToggled, self.choice_tree.get_model())
		
		col = gtk.TreeViewColumn("", rend, active=2)
		col.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
		col.set_fixed_width(50)
		
		self.choice_tree.append_column(col)
		
		sw = gtk.ScrolledWindow()
		sw.add(self.choice_tree)
		
		vbox.pack_start(sw)

		self.program_db = DatabaseWrapper(os.path.join(utils.DHOME_DIR, DB_FILE))
		self.program_iters = []
		
		self.lockInterface()
		self.fetchComponents(self.populateChoiceStore)
		
		bb = gtk.HButtonBox()
		bb.set_layout(gtk.BUTTONBOX_END)
		
		btn = utils.new_button(_("Procedi con l'aggiornamento"), gtk.STOCK_GO_FORWARD)
		btn.connect('clicked', self.onGoForward)
		bb.pack_start(btn)
		
		vbox.pack_start(bb, False, False, 0)
		
		self.nb.append_page(vbox)
		
		self.show_all()
	
	def lockInterface(self, lock=True):
		print "lockInterface", lock
	
	def reportError(self, data, response, args, where):
		UpdateEngine.reportError(data, response, args, where)
	
	def populateChoiceStore(self, programs):
		for i in programs:
			self.choice_store.append([self.icon_program, i, False])

		self.lockInterface(False)
	
	def getVersionFromDatabase(self, program):
		a = self.program_db.select("SELECT mainversion,version,revision FROM program WHERE name='%s'" % self.program_db.sanitize(program))[0]
		return self.versionize(a)
	
	def versionize(self, a):
		return "-r".join((".".join(map(str,a[:2])), str(a[2])))
	
	def populateUpdateTree(self, p_list):
		for i in p_list:
			self.store.append(None,
				[
					self.icon_program,
					i,
					"...", # FIXME
					self.getVersionFromDatabase(i),
					0,
					0,
					False,
					self.color_wait
				]
			)
		
		self.program_list = p_list
	
	def onToggled(self, cell, path, model):
		iter = model.get_iter((int(path),))
		fixed = model.get_value(iter, 2)
		fixed = not fixed
		model.set(iter, 2, fixed)
	
	def onGoForward(self, widget):
		# Facciamo un for sugli iter e controlliamo quali sottoprogrammi abbiamo abilitato
		
		model = self.choice_tree.get_model()
		it = self.choice_tree.get_model().get_iter_first()
		
		p_list = []
		
		while it:
			if model.get_value(it, 2):
				p_list.append(model.get_value(it, 1))
			it = model.iter_next(it)
		
		if len(p_list) == 0:
			self.status.push(0, _("Seleziona almeno un componente per l'aggiornamento."))
		else:
			self.choice_store.clear()
			self.nb.set_current_page(0)
			self.populateUpdateTree(p_list)
	
	def onGetList(self, widget):
		#TODO
		#self.lockInterface()

		idx = 0
	
		for i in self.program_list:
			self.startThread(
				self.populateProgramIter,
				BASE_DIR + i + "-update.xml",
				idx
			)
			idx += 1
	
	def startThread(self, callback, url, args=None):
		print _(">> Creo un thread per %s") % url
		f = Fetcher(callback, url, args)
		f.setDaemon(True)
		f.start()
	
	def getIterFromIndex(self, idx):
		prog = self.program_list[idx]
		
		model = self.tree.get_model()
		it = self.tree.get_model().get_iter_first()
		
		while it:
			if model.get_value(it, 1) == prog:
				return it
			
			it = model.iter_next(it)
		
		raise Exception("ARGHHH No Iter!")

	def populateProgramIter(self, data, response, index):
		#TODO: unlock interface
		
		it = self.getIterFromIndex(index)
		model = self.tree.get_model()
		
		#print response.status, data

		if data == None or response.status != 200:
			self.reportError(data, response, index, STEP_PROGRAM)
			#self.status.push(0, _("Errore durante lo scaricamento della lista dei file(HTTP %d)") % response.status)
			model.set_value(it, COL_COLO, self.color_error)
			return
	
		#try:
		# TODO: in pratica qui dovremmo leggere la revisione e piazzarla nella colonna
		# infatti suggerisco di modificare il nome delle colonne eliminando la col per l'md5
		# e inserirne solo 2 una per la revision nuova e una per la vecchia
		# NOTA: una sola colonna contenente revision tipo 1.2-r2
		
		new_schema = ReportReader(data)
		old_schema = ReportReader(None, os.path.join(utils.DHOME_DIR, "pyacqua.xml"))
		
		a = (new_schema.get("mainversion"), new_schema.get("secondversion"), new_schema.get("revision"))
		model.set_value(it, COL_NREV, self.versionize(a))
		
		ret = old_schema.checkDiff(new_schema)
		
		if ret == 0:
			# messaggio nessun aggiornamento disponibile ecc...
			utils.info(_("Nessun aggiornamento disponibile"))
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
		#except:
		#	self.status.push(0, _("Impossibile interpretare il file xml"))
		#	return
		
		self.update_btn.set_sensitive(True)
	
	def __checkFileToUpdate(self, schema):
		self.mirrors = schema.getList("mirrors", "url")
		self.program = schema.getProgramName()

		if self.program == None or self.mirrors == None:
			utils.error(_("Impossibile procedere con l'aggiornamento. Nessun mirror trovato o nome programma assente"))
			self.status.push(0, _("Nessun mirror fornito o nome programma assente"))
			return

		self._thread(self.__markFileForUpdate, utils.url_encode("%s/%s-update.db" % (self.mirrors[0], self.program)))
	
	def __markFileForUpdate(self, data, response):
		
		# Finche non abbiamo scaricato il database proviamo con il mirror successivo

		if not data or response.status != 200:
			
			if len(self.mirrors) == 0:
				utils.error(_("Impossibile scaricare il database delle revisioni"))
				self.status.push(0, _("Impossibile scaricare il database delle revisioni"))
				return
			else:
				self._thread(self.__markFileForUpdate, utils.url_encode("%s/%s-update.db" % (self.mirrors[0], self.program)))
				del self.mirrors[0]

		# Ok abbiamo scaricato correttamente il database

		self.__diffDatabase(data)
	
	def __diffDatabase(self, data, programs_list):
		f = open(os.path.join(utils.UPDT_DIR, self.file), 'wb')
		f.write(data)
		f.close()

		new_db = DatabaseReader(os.path.join(utils.UPDT_DIR, self.file))
		old_db = DatabaseReader(os.path.join(utils.DHOME_DIR, DB_FILE))

		# Bisogna fare un diff sulle row e controllare le entry delle revisioni
		# Possiamo avere un update tra revision differenti e tra
		# revision e secondversion differenti

		if new_db.v_main != old_db.v_main:
			return False

		if new_db.v_ver != old_db.v_ver:
			# Full update di tutti i file..
			pass
		
		if new_db.v_rev == old_db.v_rev:
			return True

		return True
		
	def _on_start_update(self, widget):
		self.it = self.tree.get_model().get_iter_first()
		self._update_from_iter()
		
	def _update_file(self, data, response):
		# Dovremmo semplicemente salvare in una directory temporanea
		# del tipo ~/.pyacqua/.update o .update nella directory corrente
		# insieme ad una lista di file|bytes|checksum per il controllo sull'update
		# Al riavvio il programma dovrebbe controllare che in .update ci siano file
		# e aggiornare di conseguenza
		
		# TODO: da finire
		
		if not data:
			print _(">> Nessun file da ricevere")
		
		if response.status != 200:
			self._sign_error(response)
			return

		print response.status
		
		# Creiamo le subdirectory necessarie
		dirs = self.file.split(os.path.sep); dirs.pop()
		path = utils.UPDT_DIR
		
		try:
			for i in dirs:
				path = os.path.join(path, i)
				if not os.path.exists(path):
					os.mkdir(path)
		
			print _(">> File ricevuto %s") % self.file
		
			f = open(os.path.join(utils.UPDT_DIR, self.file), 'wb')
			f.write(data)
			f.close()
			
			self._update_percentage()
			self._go_with_next_iter()
		except:
			self._sign_error(response)
	
	def _sign_error(self, response):
		# Qualcosa di strano e' successo.. mhuahuahuau *_*
		# -.- come stiamo sotto
		
		self.tree.get_model().set_value(self.it, 0, self.icon_error)
		self.tree.get_model().set_value(self.it, 10, self.color_error)
		self.tree.get_model().set_value(self.it, 8, 0)
		
		self.status.push(0, _("Errore durante lo scaricamento di %s(response: %d)") %(self.file, response.status))
		
		# Qui dovresti bloccare tutto e cancellare i file gia scaricati
		# altrimenti nella callback di scaricamento dovresti inserire un check
		# se esistono gia dei file che dovrebbero essere scaricati controlli md5 e bytes e se giusti
		# non li scarichi
		
	def _update_percentage(self):
		self.tree.get_model().set_value(self.it, 0, self.icon_done)
		self.tree.get_model().set_value(self.it, 10, self.color_done)
		self.tree.get_model().set_value(self.it, 8, 100)
		
	def _go_with_next_iter(self):
		self.it = self.tree.get_model().iter_next(self.it)
		self._update_from_iter()
		
	def _update_from_iter(self):
		if self.it != None:
			self.file = self.tree.get_model().get_value(self.it, 1)
			
			if self.tree.get_model().get_value(self.it, 9):
				
				# FIXME: Controlla se esiste gia il file(se l'abbiamo scaricato precedentemente)
				tmp = os.path.join(utils.UPDT_DIR, self.file)
				
				if os.path.exists(tmp):
					# Controlliamo se il file e' corretto
					bytes = os.path.getsize(tmp)
					md5   = generate.Generator.checksum(tmp)
					
					if md5 != self.tree.get_model().get_value(self.it, 4) or int(bytes) != self.tree.get_model().get_value(self.it, 3):
						os.remove(tmp)
						self._thread(self._update_file, utils.url_encode(BASE_DIR + self.file))
					else:
						self._update_percentage()
						self._go_with_next_iter()
				else:
					self._thread(self._update_file, utils.url_encode(BASE_DIR + self.file))
			else:
				self._update_percentage()
				self._go_with_next_iter()
		else:
			self.xml_util.dump_tree_to_file(self.diff_object, os.path.join(utils.UPDT_DIR, ".diff.xml"))
			
			utils.info(_("Riavvia per procedere all'aggiornamento di PyAcqua"))
			
			self.destroy()
			
			# La list.xml la si becca dal sito.. ergo no problem
	def _on_delete_event(self, *w):
		app.App.p_window["update"] = None
