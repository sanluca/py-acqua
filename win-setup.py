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
import sys
import glob
import py2exe
from distutils.core import setup
from distutils.filelist import findall
import matplotlib
import src.generate as generate
import time

from py2exe.build_exe import py2exe as build_exe

class my_py2exe(build_exe):
	def run (self):
		if not os.path.exists ("win32-merger/pyacqua.exe"):
			print "You must compile the win32-merger"
			return
		print "**"
		print "** Remember to clean dist/ dir before running this"
		print "** Or at least to remove dist/list.xml"
		print "**"
		print "** Sleeping 5 seconds now..."
		time.sleep (5)
		print "**"
		print
		
		build_exe.run (self)
		
		print "Creating list.xml ..."
		
		os.chdir ("dist\\")
		xml = generate.UpdateXML ()
		xml.dump_tree_to_file (xml.create_dict_from_directory (), "list.xml")
		
		print "List created."

def moon_walk (root_dir, repl):
	packages, data_files = [], []
	
	for dirpath, dirnames, filenames in os.walk (root_dir):
		for i, dirname in enumerate (dirnames):
			if dirname.startswith('.'): del dirnames[i]
			data_files.append((repl + dirpath[len(root_dir):], [os.path.join(dirpath, f) for f in filenames]))
	
	return data_files

#opts = {
#"py2exe": {
#	"includes": "_winreg",
#	}
#}
#setup (
#	name="merger",
#	version="1.0",
#	description="PyAcqua program",
#	author="Francesco Piccinno",
#	author_email="stack.box@gmail.com",
#	url="http://www.pyacqua.net",
    #windows = [
    #    {"script": "src/merger.py",
    #    "icon_resources": [(1, "pixmaps/pyacqua.ico")]
    #    }
    #],
#	console=[
#	    {"script": "src/merger.py",
#        "icon_resources": [(1, "pixmaps/pyacqua.ico")]
#		}
#    ],
#	packages=[''],
#	package_dir={'': 'src'},
#)

opts = {
"py2exe": {
	"includes": "pangocairo,gtk,pango,atk,gobject,cairo,win32api,pysqlite2",
	"dll_excludes": [
	"iconv.dll","intl.dll","libatk-1.0-0.dll",
	"libgdk_pixbuf-2.0-0.dll","libgdk-win32-2.0-0.dll",
	"libglib-2.0-0.dll","libgmodule-2.0-0.dll",
	"libgobject-2.0-0.dll","libgthread-2.0-0.dll",
	"libgtk-win32-2.0-0.dll","libpango-1.0-0.dll",
	"libpangowin32-1.0-0.dll",
	'tcl84.dll', 'tk84.dll', 'wxmsw26uh_vc.dll'],
	"packages" : ["matplotlib", "pytz"],
	"excludes": ["Tkconstants", "Tkinter", "tcl", ],
	}
}

setup (
	cmdclass = {"py2exe": my_py2exe},
	name="py-acqua",
	version="1.0",
	description="PyAcqua program",
	author="Francesco Piccinno",
	author_email="stack.box@gmail.com",
	url="http://www.pyacqua.net",
    windows = [
        {"script": "src/acqua.py",
        "icon_resources": [(1, "pixmaps/pyacqua.ico")]
        }
    ],
	#console=[
	#    {"script": "src/acqua.py",
    #    "icon_resources": [(1, "pixmaps/pyacqua.ico")]
	#	}
    #],
	packages=[''],
	package_dir={'': 'src'},
	options=opts,
	data_files=moon_walk ("skins", "skins") + moon_walk ("locale", "locale") + [
		#("src", glob.glob ("src/*")),
		#Disabilitiamo i plugins
		#("plugins", glob.glob ("plugins/*.py")),
		("pixmaps", glob.glob ("pixmaps/*")),
		("tips", glob.glob ("tips/*.txt"))
	] + [matplotlib.get_py2exe_datafiles()]
)
