# -*- coding: iso-8859-15 -*-
#Copyright (C) 2005, 2007 Py-Acqua
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

"""
Update staff.

$Id: database.py 904 2007-12-23 13:24:50Z stack_isteric $
"""

__author__    = "Francesco Piccinno <stack.box@gmail.com>"
__version__   = "$Revision: 904 $"
__copyright__ = "Copyright (c) 2007 Francesco Piccinno"

import os
import md5
import sys

from os.path import basename, split

from optparse import OptionParser
from pysqlite2 import dbapi2 as sqlite
from os.path import getsize

class DatabaseWrapper(object):
	def __init__(self, database):
		self.connection = sqlite.connect(database)
		self.cursor = self.connection.cursor()
	
	def sanitize(self, val):
		# TODO: more check?

		if type(val) == tuple:
			t = []
			for i in val:
				if i and (type(i) == str or type(i) == unicode):
					t.append(i.replace("'", "''"))
				else:
					t.append(i)
			return tuple(t)
		elif type(val) == str or type(val) == unicode:
			return val.replace("'", "''")
		elif type(val) == int:
			return val
		else:
			raise Exception("Unknown cast. Please define it :)")
	
	def select(self, req, dump=False):
		self.cursor.execute(req)
		ret = self.cursor.fetchall()
		
		if dump:
			print req
			print ret
		
		return ret
	
	def execute(self, req, commit=True):
		self.cursor.execute(req)
		
		if commit:
			self.connection.commit()

class DatabaseReader(DatabaseWrapper):
	def __init__(self, program, database, main=None, ver=None, rev=None):
		"""
		program = nome del programma da cui leggere la version o None per nessuno
		database = percorso del database
		main, ver, rev = None se dobbiamo fare una read altrimenti si possono settare
		"""
		
		DatabaseWrapper.__init__(self, database)
		self.program = program

		self.v_main = main
		self.v_ver = ver
		self.v_rev = rev
		
		self.checkDatabaseSchema()
		self.getVersions()
	
	def getDirRevision(self, dirname, pid):
		"""
		Return -1 se non trovata altrimenti la revision
		"""
		ret = self.select("SELECT id, revision FROM directory WHERE name='%s' AND program_id=%d" % self.sanitize((dirname, pid)))
		if len(ret) > 1: raise Exception("ugh .. Colliding directory :<")
		elif len(ret) == 0: return (-1, -1)
		else: return ret[0]
	
	def getFileRevision(self, fname, dirid, pid):
		ret = self.select("SELECT id, revision FROM file WHERE name='%s' AND directory_id=%d AND program_id=%d" % self.sanitize((fname, dirid, pid)))
		if len(ret) > 1: raise Exception("ugh .. Colliding files :> .. you are very lucky man!")
		elif len(ret) == 0: return (-1, -1)
		else: return ret[0]
	
	def checkConsistence(self, file_id, frev, fbytes, fmd5):
		print self.select("SELECT id, revision, bytes, md5 FROM file WHERE id=%d" % self.sanitize(file_id))
		if len(ret) > 1: raise Exception("ugh .. Colliding files :> .. you are very lucky man!")
		elif len(ret) == 0: return False
		else: return (file_id, frev, fbytes, fmd5) == ret[0]
	
	def checkDatabaseSchema(self):

		tables = [
			'directory', 'file', 'program'
		]

		schemas = [
			'CREATE TABLE directory(id INTEGER PRIMARY KEY, name TEXT, revision INTEGER, filenum INTEGER, program_id INTEGER)',
			'CREATE TABLE file(id INTEGER PRIMARY KEY, name TEXT, revision INTEGER, bytes REAL, md5 VARCHAR(32), directory_id INTEGER, program_id INTEGER)',
			'CREATE TABLE program(id INTEGER PRIMARY KEY, name TEXT, mainversion INTEGER, version INTEGER, revision INTEGER, dirnum INTEGER)'
		]

		unused = []
		
		ret = self.select("select * from sqlite_master")

		for i in ret:
			if i[4] not in schemas:
				print "Wrong schema in database."
				print "I know who is the killer :o"
				print "Table: %s" % i[2]
				
				if i[2] in tables:
					print "Wrong schema detected."
					print i[4]
					print " .. should be .."
					print schemas[tables.index(i[2])]

				sys.exit(0)
			else:
				unused.append(schemas.index(i[4]))


			if i[2] not in tables:
				print "non-necessary Table: %s" % i[2]

		for i in range(len(schemas)):
			if i not in unused:
				self.execute(schemas[i])
	
	def getVersions(self):
		if not self.program:
			return
		
		ret = self.select("SELECT * FROM program WHERE name=\"%s\"" % self.sanitize(self.program))

		if len(ret) == 1:
			if self.v_main == None:
				self.v_main = ret[0][2]
			if self.v_ver == None:
				self.v_ver  = ret[0][3]
			if self.v_rev == None:
				self.v_rev  = ret[0][4]
		
class DatabaseUpdater(DatabaseReader):
	def __init__(self, program, path, database, main=None, ver=None, rev=None):
		self.path = path
		DatabaseReader.__init__(self, program, database, main, ver, rev)

	def checkArgs(self):
		if self.v_main == None or self.v_ver == None or self.v_rev == None:
			print "Error in parameters: main, version and revision cannot be None"
			sys.exit(-1)
	
	def updateProgramTable(self, noupdate=False):
		ret = self.select("SELECT * FROM program WHERE name=\"%s\"" % self.sanitize(self.program))

		if len(ret) > 1:
			print "Error in database. Duplicated entries for program %s." % self.program
		elif len(ret) == 1:
			# must update

			id   = ret[0][0]

			if not noupdate:
				main = (self.v_main) and (self.v_main) or (ret[0][2])
				ver  = (self.v_ver)  and (self.v_ver)  or (ret[0][3])
				rev  = (self.v_rev)  and (self.v_rev)  or (ret[0][4])

				self.execute("UPDATE program SET mainversion=%d, version=%d, revision=%d WHERE id=%d" % (main, ver, rev, id))

			return id
		else:
			# insert rapido

			self.checkArgs()
				
			self.execute("INSERT INTO program VALUES(NULL, \"%s\", %d, %d, %d, 0)" % self.sanitize
				(
					(self.program, self.v_main, self.v_ver, self.v_rev)
				)
			)

			return self.updateProgramTable(noupdate=True)
	
	def updateDirectoryTable(self, dir, p_id, noupdate=False):
		# Dovremmo controllare l'esistenza
		# se esiste aggiornale la revision se non ci e' stato passato nulla come arg
		# 	altrimenti forzare sui valori passati
		# se non esiste inserire i valori passati
		# 	se non ci sono errore ed esci -1
		
		dir = (dir.startswith("./")) and (dir[2:]) or (dir)

		ret = self.select("SELECT * FROM directory WHERE name=\"%s\" AND program_id=%d" % self.sanitize((dir, p_id)))

		if len(ret) > 1:
			print "Error in database. Duplicated entries for directory %s with program_id = %d." % (dir, p_id)

		elif len(ret) == 1:

			id   = ret[0][0]

			if not noupdate:
				rev = (self.v_rev) and (self.v_rev) or (ret[0][2])
				self.execute("UPDATE directory SET revision=%d WHERE id=%d" % (rev + 1, id))

			return id
		else:

			self.checkArgs()

			self.execute("INSERT INTO directory VALUES(NULL, \"%s\", %d, 0, %d)" % self.sanitize
				(
					(dir, self.v_rev, p_id)
				)
			)

			return self.updateDirectoryTable(dir, p_id, noupdate=True)
	
	def updateDirectoryFileN(self, dirid, nfiles):
		self.execute("UPDATE directory SET filenum=%d WHERE id=%d" % (nfiles, dirid))
	
	def updateProgramDirectoryN(self, p_id, ndir):
		self.execute("UPDATE program SET dirnum=%d WHERE id=%d" % (ndir, p_id))
	
	def md5sum(self, file):
		fobj = open(file, 'rb')
		m = md5.new()

		while True:
			d = fobj.read(8096)
			if not d: break
			m.update(d)

		return m.hexdigest()

	def updateFileTable(self, file, p_id, dirid, dirname, noupdate=False):
		
		# Dovremmo controllare l'esistenza
		# se esiste aggiornale la revision se non ci e' stato passato nulla come arg e se md5 e minchiate son variate e propagare alla dir
		# 	altrimenti forzare sui valori passati
		# se non esiste inserire i valori passati
		# 	se non ci sono errore ed esci -1
		
		ret = self.select("SELECT * FROM file WHERE name=\"%s\" AND program_id=%d" % self.sanitize((file, p_id)))

		if len(ret) > 1:
			print "Error in database. Duplicated entries for file %s with program id = %d." % (file, p_id)

		elif len(ret) == 1:

			id   = ret[0][0]

			if not noupdate:
				rev   = (self.v_rev) and (self.v_rev) or (ret[0][2] + 1)
				
				bytes = ret[0][3]
				sumd5 = ret[0][4]
				did   = ret[0][5]

				c_bytes = getsize(file)
				c_sumd5 = self.md5sum(file)
				c_did   = dirid

				if c_bytes != bytes or c_sumd5 != sumd5 or c_did != did:
					self.execute("UPDATE file SET revision=%d, bytes=%d, md5=\"%s\", directory_id=%d, program_id=%d WHERE id=%d" % self.sanitize
						(
							(rev, c_bytes, c_sumd5, c_did, p_id, id)
						)
					)

					return True

			return False
		else:

			self.checkArgs()

			self.execute("INSERT INTO file VALUES(NULL, \"%s\", %d, %d, \"%s\", %d, %d)" % self.sanitize
				(
					(os.path.basename(file), self.v_rev, getsize(file), self.md5sum(file), dirid, p_id)
				)
			)

			return False
	
	def scanPath(self, programid):
		os.chdir(self.path)
		
		ndir = 1
		stack = ["."]

		while stack:
			dir = stack.pop()

			nfiles = 0; to_update = False
			dirid = self.updateDirectoryTable(dir, programid, True)

			for file in os.listdir(dir):
				fullname = os.path.join(dir, file)

				if not os.path.isdir(fullname):
					
					if self.updateFileTable(fullname, programid, dirid, dir):
						to_update = True

					nfiles += 1
				
				elif not os.path.islink(fullname):

					if file != ".svn":
						stack.append(fullname)
						ndir +=1
			if nfiles > 0:
				self.updateDirectoryFileN(dirid, nfiles)
			if to_update:
				self.updateDirectoryTable(dir, dirid)
		
		self.updateProgramDirectoryN(programid, ndir)
		
		print
		print "Id\tmain\tversion\trev\tdirnum\tname"
		print "--------------------------------------------"
		
		for i in self.select("SELECT * FROM program"):
			print "%d\t%d\t%d\t%d\t%d\t%s" % (i[0], i[2], i[3], i[4], i[5], i[1])

		print
		print "Id\trev\tnfiles\tpid\tname"
		print "------------------------------------"

		for i in self.select("SELECT * FROM directory"):
			print "%d\t%d\t%d\t%d\t%s" % (i[0], i[2], i[3], i[4], i[1])

		print
		print "Id\trev\tbytes\tmd5sum\t\t\t\t\tdir\tpid\tname"
		print "------------------------------------------------------------------------------------"

		for i in self.select("SELECT * FROM file"):
			print "%d\t%d\t%d\t%s\t%d\t%d\t%s" % (i[0], i[2], i[3], i[4], i[5], i[6], i[1])

		print
	
	def update(self):
		id = self.updateProgramTable()
		self.scanPath(id)
