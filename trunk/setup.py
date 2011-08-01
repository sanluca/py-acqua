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
from distutils.core import setup

###
def moon_walk (root_dir, repl):
	packages, data_files = [], []
	
	for dirpath, dirnames, filenames in os.walk (root_dir):
		for i, dirname in enumerate (dirnames):
			if dirname.startswith('.'): del dirnames[i]
			data_files.append(("share/pyacqua/" + repl + dirpath[len(root_dir):], [os.path.join(dirpath, f) for f in filenames]))
	
	return data_files

if __name__ != "__main__":
	print moon_walk (sys.argv[1])
else:
	setup (
	name="py-acqua",
	version="1.0",
	description="PyAcqua program",
	author="Francesco Piccinno",
	author_email="stack.box@gmail.com",
	url="http://pyacqua.altervista.org",
	scripts=["src/acqua.py"],
	package_dir={'pyacqua': 'src'},
	packages=['pyacqua'],
	data_files=moon_walk ("skins", "skins") + moon_walk ("locale", "locale") + [
		#("src", glob.glob ("src/*")),
		("share/pyacqua/plugins", glob.glob ("plugins/*.py")),
		("share/pyacqua/pixmaps", glob.glob ("pixmaps/*")),
		("share/pyacqua/tips", ["src/tip_of_the_day_en.txt", "src/tip_of_the_day.txt"])
	]
	)
