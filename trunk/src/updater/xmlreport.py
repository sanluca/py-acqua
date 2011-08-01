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

$Id: xmlreport.py 903 2007-12-22 00:19:08Z stack_isteric $
"""

__author__    = "Francesco Piccinno <stack.box@gmail.com>"
__version__   = "$Revision: 903 $"
__copyright__ = "Copyright (c) 2007 Francesco Piccinno"

import os
import sys
import base64
import ConfigParser

from optparse import OptionParser
from database import DatabaseWrapper
from xml.dom.minidom import parse, parseString, getDOMImplementation

class ProgramInterface(object):
	
	def __init__(self, name):
		self.name = name

		self.options = {
			'%s.uselast'           % self.name : True,
			'%s.mainversion'       % self.name : 0,
			'%s.secondversion'     % self.name : 0,
			'%s.revision'          % self.name : 0,
			'%s.changelog'         % self.name : '',
			'%s.database'          % self.name : '',
			'%s.message'           % self.name : '',

			'%s.message-pre'       % self.name : '',
			'%s.message-post'      % self.name : '',

			'%s.mirrors'           % self.name : [],

			'%s.downloads-windows' % self.name : [],
			'%s.downloads-tarball' % self.name : [],
			'%s.downloads-svn'     % self.name : [],

			'%s.actions-pre'       % self.name : [],
			'%s.actions-post'      % self.name : [],

		}
	
	def get(self, option):
		return self.options['%s.%s' % (self.name, option)]
	
	def check(self, option):
		return "%s.%s" % (self.name, option) in self.options

	def set(self, option, value):
		self.options['%s.%s' % (self.name, option)] = value
	
	def dump(self):
		print self.options

class ReportReader(ProgramInterface):
	def __init__(self, data, path=None):
		try:
			if data != None:
				doc = parseString(data)
			elif data == None and path != None:
				doc = parse(path)
			else:
				raise Exception("uh. :o")
		except:
			raise Exception("Cannot parse xml-report")
		
		if doc.documentElement.tagName.endswith("-update"):
			
			ProgramInterface.__init__(self, doc.documentElement.tagName[:-7])
			
			for node in doc.documentElement.childNodes:
				if node.nodeName == "info": self.parseInfo(node)
				if node.nodeName == "database": self.set("database", node.firstChild.data)
				if node.nodeName == "mirrors":
					self.parseArray(node, ("mirrors", "url"))
				if node.nodeName == "actions":
					self.parseArray(node, ("actions-pre", "pre"))
					self.parseArray(node, ("actions-post", "post"))
				if node.nodeName == "downloads":
					self.parseArray(node, ("downloads-windows", "windows"))
					self.parseArray(node, ("downloads-tarball", "tarball"))
					self.parseArray(node, ("downloads-svn", "svn"))
	
	def parseInfo(self, noderoot):
		prop = [
			'uselast',
			'mainversion',
			'secondversion',
			'revision',
			'changelog',
			'message'
		]
		
		for node in noderoot.childNodes:
			if node.nodeName in prop:
				if node.firstChild: self.set(node.nodeName, node.firstChild.data)
	
	def parseArray(self, noderoot, obj):
		lst = []
		
		for node in noderoot.childNodes:
			if node.nodeName == obj[1]:
				if node.firstChild: lst.append(node.firstChild.data)
		
		self.set(obj[0], lst)
	
	def checkDiff(self, other):
		"""
		Ritorna:
			3 se le versioni sono incompatibili
			2 se le versioni sono potenzialmente compatibile
			1 se le verrsioni sono compatibili
			0 se le versioni sono identiche
		"""
		o_m, o_s, o_r = other.get("mainversion"), other.get("secondversion"), other.get("revision")
		c_m, c_s, c_r = self.get("mainversion"), self.get("secondversion"), self.get("revision")
		
		if o_m == c_m and o_s == c_s and o_r == c_r: return 0
		if o_m != c_m: return 3
		else:
			if o_s != c_s: return 2
			if o_r != c_r: return 1

class Indexer(object):
	
	programs = property(lambda x: x.__programs)
	
	def __init__(self, data=None):
		self.__programs = []
		
		if data != None:
			try:
				doc = parseString(data)
			except:
				raise Exception("Cannot parse index file.")
			
			if doc.documentElement.tagName == "pyacqua-index":
				for node in doc.documentElement.childNodes:
					if node.nodeName == "content" and node.firstChild:
						self.addContent(node.firstChild.data)
			else:
				raise Exception("Unknown file format for index file.")
	
	def addContent(self, program):
		self.__programs.append(program)
	
	def saveToFile(self, file):
		doc = getDOMImplementation().createDocument(None, "pyacqua-index", None)
		element = doc.documentElement
		
		for i in self.__programs:
			t = doc.createElement("content")
			t.appendChild(doc.createTextNode(i))
			element.appendChild(t)
		
		try:
			f = open(file, "w")
			doc.writexml (f, "", "", "")
			f.close()
			
			print "%s written." % file
		except:
			print "Cannot write to %s ... ignoring." % file

class IndexMaker(object):
	def __init__(self, db, out):
		self.db = DatabaseWrapper(db)
		self.idx = Indexer()
		self.out = out
	
	def create(self):
		for i in self.db.select("SELECT name FROM program")[0]:
			print "-> %s added." % i
			self.idx.addContent(i)
		
		self.idx.saveToFile(self.out)

class ListCreator(object):
	def __init__(self, database, info):
		self.db = DatabaseWrapper(database)

		self.info = info
		self.programs = {}

		self.readInfoFile()
	
	def readVersionFromDatabase(self, name):
		try:
			program = self.programs[name]

			t = map(
				int, self.db.select("SELECT mainversion, version, revision FROM program WHERE name=\"%s\"" % self.db.sanitize(name))[0]
			)
			
			program.set("mainversion", t[0])
			program.set("secondversion", t[1])
			program.set("revision", t[2])
		except:
			print "Cannot get the versions for program %s." % name
			sys.exit(-1)
	
	def readInfoFile(self):
		parser = ConfigParser.ConfigParser()
		parser.read(self.info)

		# First load the programs name
		for sec in parser.sections():
			if '.' not in sec:
				self.programs[sec] = ProgramInterface(sec)

		for sec in parser.sections():
			for opt in parser.options(sec):
				self.handleOption(sec.lower(), opt.lower(), parser.get(sec, opt))
		
		for k in self.programs:
			program = self.programs[k]
			if program.get("uselast"):
				self.readVersionFromDatabase(program.name)
	
	def handleOption(self, sec, opt, value):
		
		if '.' not in sec:
			program = self.programs[sec]
		else:
			program = self.programs[sec.split(".")[0]]
			sec = sec.split(".", 1)[1]

		if program.check(sec):
			# Mirrors or lists to handle

			# TODO: evalutate numbers

			check = lambda x, y: x[:len(y)] == y and ((len(x[len(y):]) > 0 and x[len(y):].isdigit()) or (len(x[len(y):]) == 0))

			if check(opt, "mirror"):
				program.get("mirrors").append(value)

			elif check(opt, "svn"):
				program.get("downloads-svn").append(value)
			elif check(opt, "tarball"):
				program.get("downloads-tarball").append(value)
			elif check(opt, "windows"):
				program.get("downloads-windows").append(value)

			elif check(opt, "pre"):
				program.get("actions-pre").append(value)
			elif check(opt, "post"):
				program.get("actions-post").append(value)
		else:
			# type checking
			
			if not program.check(opt):
				print "%s not used." % opt
				return

			converter = type(program.get(opt))
			
			# Necessary ugly code :D

			def strict_bool(x):
				if x == "1" or x.lower() == "true":
					return True
				elif x == "0" or x.lower() == "false":
					return False
				else:
					raise

			if converter == bool:
				converter = strict_bool

			try:
				if value != "":
					program.set(opt, converter(value))
			except:
				print "Type error detected:"
				print "%s must be of %s not %s" % (full, (converter == strict_bool) and (bool) or (converter), type(value))
				
				sys.exit(-1)
	
	def create(self):
		for i in self.programs:
			self.createXmlForProgram(i)

	def createXmlForProgram(self, name):
		
		program = self.programs[name]

		doc = getDOMImplementation().createDocument(None, "%s-update" % name, None)
		
		element = doc.documentElement

		def temp(x):
			try:
				f = open(x, 'r')
				t = base64.b64encode(f.read())
				f.close()
				return t
			except:
				return ""

		values = [
			# optionname category howto dump
			['mainversion', 	'info', 	str],
			['secondversion',	'info', 	str],
			['revision', 		'info', 	str],
			['message', 		'info', 	str],

			['changelog', 		'info',	temp],
			
			['database', 		None, 		str],

			['message-pre', 	'info',	str],
			['message-post',	'info',	str],

			['mirrors',		'mirrors',	None,	'url'],

			['actions-pre',		'actions',	None,	'pre'],
			['actions-post',	'actions',	None,	'post'],

			['downloads-svn',	'downloads',	None,	'svn'],
			['downloads-tarball',	'downloads',	None,	'tarball'],
			['downloads-windows',	'downloads',	None,	'windows']

		]

		self.categories = {}

		for option in values:
			if len(option) == 4:
				if not option[1] in self.categories:
					t = self.categories[option[1]] = doc.createElement(option[1])
					element.appendChild(t)
				
				t = self.categories[option[1]]
				
				for i in program.get(option[0]):
					x = doc.createElement(option[3])
					x.appendChild(doc.createTextNode(i))
					t.appendChild(x)
			else:
				if option[1] == None:
					t = doc.createElement(option[0])
					t.appendChild(doc.createTextNode(str(program.get(option[0]))))
					element.appendChild(t)
				else:
					if not option[1] in self.categories:
						t = self.categories[option[1]] = doc.createElement(option[1])
						element.appendChild(t)
					
					t = self.categories[option[1]]
					x = doc.createElement(option[0])
					
					x.appendChild(doc.createTextNode(option[2](program.get(option[0]))))
					t.appendChild(x)
		try:
			f = open("%s-update.xml" % name, "w")
			doc.writexml (f, "", "", "")
			f.close()
			
			print "%s-update.xml written." % name
		except:
			print "Cannot write to %s-update.xml ... ignoring." % name
