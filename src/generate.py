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

import os
import md5
import sys
from os.path import join, getsize
from xml.dom.minidom import parse, parseString, getDOMImplementation

class Generator (object):
	"""
	Questa classe serve a generare una lista di checksum data una dir o
	semplicemente a generare un checksum di un determinato file.
	"""
	
	def checksum (path):
		"""
		Genera un checksum MD5 a partire dal percorso del file stesso.
		
		Esempio:
			>> print Generator.checksum ("/home/foo/file.zip")
			850359fd43501306f912380273aca66e
		"""
		
		fobj = file (path, 'rb')
		m = md5.new()

		while True:
			d = fobj.read(8096)
			if not d:
				break
			m.update(d)
		
		return m.hexdigest()

	def ParseDir (dir):
		"""
		Genera i checksum MD5 di tutti i file presenti in una dir.
		NB: Analizza i file che si trovano nelle sottodirectory mentre non scanna
		i file all'interno di cartelle di nome ".svn"
		
		Il risultato e' un dizionario del tipo:
		dict ["percorso_file_relativo"] = "md5_come_hex_string"
		"""
		
		stack = [dir]
		data = {}

		while stack:
			dir = stack.pop ()
			for file in os.listdir (dir):
				fullname = os.path.join (dir, file)
				if not os.path.isdir (fullname):
					data[fullname[2:]] = str (getsize (fullname)) + "|" + str (Generator.checksum (fullname))
				elif not os.path.islink (fullname):
					if file != ".svn":
						stack.append (fullname)
		return data
	
	# Dichiariamoli statici
	checksum = staticmethod (checksum)
	ParseDir = staticmethod (ParseDir)


"""
NOTE:
						
Il file per l'aggiornamento dovrebbe avere un aspetto simile:

<pyacqua>
	<directory name="." revision="2">
		<file name="NOTE" md5="..." bytes="..." revision="2"/>
		<directory name="src" revision="2">
			<file name="generate" .../>
		</directory>
	</directory>
</pyacqua>

Per quanto concerne il tree (dict_object).. dovrebbe essere tipo:

dict_object = [
		2, # Il numero di revisione (type = int)
		["NOTE", 2, "bytes", "md5"], # Il file nella directory corrente (type list)
		{
			"src" :[
				2, # e si ripete
				["generate" ...],
				
				...
				
				{
					"altra_dir" :
						...
				}
			]
		}
]
"""
		
class UpdateXML (object):
	def __init__ (self):
		pass
	
	def make_diff (self, new_dict_object, old_dict_object):
		# Facciamo un for nelle chiavi del nuovo dizionario e compariamo
		# gli oggetti ad ogni iterazione
		
		# Se gli objects sono uguali cancelliamo la entry del vecchio
		# Se diversi aggiungiamo nel diff_dict la nuova entry la entry dal vecchio
		# Se la chiave non e' presente nel vecchio dizionario aggiungiamo una entry al diff
		# 
		# Alla fine facciamo un ciclo sulle chiavi rimanenti nel dizionario old
		# quelli saranno gli oggetti da eliminare
		
		diff_object = {}
		
		for key in new_dict_object:
			# Facciamo un confronto tra i file
			if old_dict_object.has_key (key):
				for file in new_dict_object[key]:
					
					v_new = new_dict_object[key][file]
					
					if old_dict_object[key].has_key (file):
						v_old = old_dict_object[key][file]
						
						if v_new != v_old:
							# FIXME: devi ignorare la revision mi sa
							# Non facciamo altri controlli sulla superiorita' di revision ecc..
							if not diff_object.has_key (key):
								diff_object[key] = {}
							
							diff_object[key][file] = v_new + v_old
							#print "adding %s" % file
						
						del old_dict_object [key][file]
					else: # Se il file non e' presente nel vecchio dict aggiungiamo
						if not diff_object.has_key (key):
							diff_object[key] = {}
						
						diff_object[key][file] = v_new + [0, "0", "0"]
			else:
				# Non presente la directory quindi aggiungiamola con tutti i file in essa presenti
				diff_object[key] = new_dict_object[key]
				
				# e la "." ?
				for x in diff_object[key]:
					diff_object[key][x] += [0, "0", "0"]
		
		for key in old_dict_object:
			diff_object["$$" + key + "$$"] = old_dict_object[key]
		
		print diff_object
		return diff_object
	
	def create_dict_from_string (self, xmlstr):
		"""
		Crea un dizionario da una stringa che contiene il file xml
		
		Ritorna un dizionario vuoto {} se ci sono errori
		"""
		
		if xmlstr == None: return {}
		
		try:
			doc = parseString (xmlstr)
		except:
			return {}
		
		return self._real_load (doc)
		
	def create_dict_from_file (self, file):
		"""
		Crea un dizionario da un file xml contenente la lista dei file da aggiornare..
		
		Ritorna un dizionario vuoto {} se ci sono errori
		"""
		
		if file == None: return {}
		
		try:
			doc = parse (file)
		except:
			return {}
		
		return self._real_load (doc)
	
	def _real_load (self, doc):
		dict_object = {"." : {"." : [1]}}#int (doc.documentElement.attributes ["revision"].nodeValue)]}}
		
		if doc.documentElement.tagName == "pyacqua":
			self.parse_schema (doc.documentElement, ".", dict_object)
		
		return dict_object
	
	def parse_schema (self, root, directory, dict_object):
		for node in root.childNodes:
			if node.nodeName == "directory":
				dict_object [node.attributes ["name"].nodeValue] = {"." : [int (node.attributes ["revision"].nodeValue)]}
				self.parse_schema (node, node.attributes ["name"].nodeValue, dict_object)
			elif node.nodeName == "file":
				dict_object [directory][node.attributes ["name"].nodeValue] = [
					int (node.attributes ["revision"].nodeValue),
					node.attributes ["bytes"].nodeValue,
					node.attributes ["md5"].nodeValue
				]
	
	def create_dict_from_directory (self, old_tree = None):
		"""
		Crea una nuova struttura dizionario per la directory
		
		I file anche se uguali devono essere stampati perche' bisogna creare un file.xml per l'update
		"""
		
		dict_object = {"." : {"." : [1]}} # Settiamo la revisione ad 1 preventivamente
		
		ret = self.appendFilesInfo (".", dict_object, old_tree)
		
		if ret == 1 and old_tree:
			dict_object["."]["."] = [old_tree["."]["."][0] + 1]
		
		return dict_object
	
	def appendFilesInfo (self, directory, dict_object, old_tree):
		
		directory_modified = 0 # non modificata
		
		for file in os.listdir (directory):
			fullname = os.path.join (directory, file)
			
			if os.path.isdir (fullname) and file[-5:] != ".svn":
				
				# Abbiamo una directory.
				# Aggiungiamo. I controlli verrano eseguiti sui file.
				# Al massimo se la revision e' la stessa possiamo eventualmente zappare questa entry
				
				dict_object [fullname] = {"." : [1]}
				
				ret = self.appendFilesInfo (fullname, dict_object, old_tree)
				
				if ret == 1 and old_tree:
					dict_object[fullname]["."][0] = old_tree[fullname]["."][0] + 1
				#elif ret == 0:
				#	del dict_object[fullname]
				
			elif not os.path.isdir (fullname):
				
				try:
					# Prendiamo le informazioni del file corrente se presenti per il confronto successivo
					tmp = old_tree [directory][file]
				except:
					tmp = [0, None, None]
					update_revision_of_directory = -1
				
				# Generiamo md5sum e prendiamo la size per il confronto
				bytes = str (getsize (fullname))
				md5   = str (Generator.checksum (fullname))
				
				if tmp[1] != bytes or (tmp[1] == bytes and tmp[2] != md5):
					# Aggiungiamo il file al dizionario
					
					dict_object[directory][file] = [tmp[0] + 1, bytes, md5]
					
					# Markiamo come nuovo file.. quindi la revision della root dir e' da aggiornare
					directory_modified = 1
				elif tmp[1] == bytes and tmp[2] == md5:
					
					dict_object[directory][file] = tmp
					
				elif not old_tree:
					# Se non abbiamo il file da confrontare significa che bisogna creare una lista ex novo.
					# Aggiungiamo con revision 1 quindi
					
					dict_object[directory][file] = [1, bytes, md5]
					directory_modified = 2 # modificata ma dobbiamo lasciare intatta la revisione
				
		return directory_modified
	
	def dump_tree_to_file (self, tree, file = None):
		doc = getDOMImplementation ().createDocument (None, "pyacqua", None)
		
		current = doc.documentElement
		
		for i in tree:
			# dict conterra' tutti i file
			
			dict = tree[i]
			
			element = doc.createElement ("directory")
			element.setAttribute ("name", i)
			if tree[i].has_key ("."):
				element.setAttribute ("revision", str (tree[i]["."][0]))
			
			for x in dict:
				if x == ".": continue
				
				node = doc.createElement ("file")
				node.setAttribute ("name", x)
				node.setAttribute ("revision", str (dict[x][0]))
				node.setAttribute ("bytes", str (dict[x][1]))
				node.setAttribute ("md5", str (dict[x][2]))
				
				element.appendChild (node)
			
			current.appendChild (element)
		
		if not file:
			doc.writexml (sys.stdout, " ", " ", " \n")
		else:
			writer = open (file, "w")
			doc.writexml (writer, "\t", "\t", "\n")
			writer.close ()

if __name__ == "__main__":
	a = UpdateXML ()
	
	try:
		if sys.argv[1] == "makeupdate":
			old_tree = a.create_dict_from_file ("list.xml")
			a.dump_tree_to_file (a.create_dict_from_directory (old_tree), "update.xml")
		elif sys.argv[1] == "makelist":
			a.dump_tree_to_file (a.create_dict_from_directory (), "list.xml")
			print "[*] If you are making an update: remember to copy list.xml into parent directory ... (win32-list.xml / source-list.xml)"
	except:
		print "Usage:"
		print "python src/generate.py makeupdate            -  to make a new update.xml  [depreacated]"
		print "python src/generate.py makelist              -  to make a new list.xml        [release]"
