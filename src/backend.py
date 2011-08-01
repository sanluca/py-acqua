# -*- coding: utf-8 -*-
# Copyright © 2005, 2008 Py-Acqua
#http://www.pyacqua.net
#email: info@pyacqua.net
#
# This file is part of PyAcqua.
#
# PyAcqua is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# PyAcqua is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyAcqua; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  
# USA

import os
import os.path
import impostazioni
import app
from utils import c_info
from dbwindow import DBWindow

class ColumnType:
	"""
	Valori maggiori di 5 vengono trattati come varchar.
	In questo caso per un varchar (500) sarebbe un =>
	ColumnType.VARCHAR + 500
	"""
	INTEGER, FLOAT, DATE, TEXT, NUMERIC = range (5)
	VARCHAR = 5

class BackendFE(object):
	"""
	BackendFE per la gestione standardizzata dei vari database.
	"""
	def __init__ (self, filename):
		self.filename = filename
		self.schema_is_ok = False
		c_info ("Initing a backend DB")
	
	def check_database (self):
		return os.path.exists (self.filename)
	
	def safe_value_convert (self, value):
		return value.replace ("'", "''")
	
	def set_schema_presents (self, flag):
		self.schema_is_ok = flag
		
	def get_schema_presents (self):
		return self.schema_is_ok
	
	def get_type (self, type_col):
		"""
		Ritorna una stringa per il tipo di dati rappresentato
		"""
		if type_col == ColumnType.INTEGER:
			return "INTEGER"
		elif type_col == ColumnType.FLOAT:
			return "FLOAT"
		elif type_col == ColumnType.DATE:
			return "DATE"
		elif type_col == ColumnType.TEXT:
			return "TEXT"
		elif type_col == ColumnType.NUMERIC:
			return "NUMERIC"
		elif type_col >= ColumnType.VARCHAR:
			return "VARCHAR(%d)" % (type_col - ColumnType.VARCHAR)
		
		raise "Cannot find an adeguate type"
		
	def create_table (self, name, columns, types):
		"""
		Crea una tabella di nome name
		columns => una lista contenente il nome delle colonne (["nome", "id"] ad esempio)
		types => una lista ColumnType con il tipo di colonne ([ColumnType.TEXT, ColumnType.INTEGER] ad esempio)
		"""
		raise "Not implemented"
	
	def select (self, what, table):
		"""
		Fa una (select %s from %s) % (what, table)
		"""
		raise "Not implemented"
	
	def update (self, table, colums, values):
		"""
		Fa un update sulla tabella selezionata (table)
		columns => le colonne da aggiornare in una lista (["nome", "cognome"] ad esempio)
		values => i valori per le rispettive colonne in lista (["mio_nome", "mio_cognome"] ad esempio)
		
		l'ultima colonna dovrebbe anche contenere il valore per il WHERE come anche values
		in questo la query si trasforma in
		
		self.update ("tabella", ["nome", "id"], ["francesco", 1]) =>
			UPDATE tabella SET NOME="francesco" WHERE id=1
		"""
		raise "Not implemented"
	
	def insert (self, table, values):
		"""
		Inserisce dei valori in una tabella
		table => tabella in cui inserire i valori
		values => lista con i valori da inserire
		"""
		raise "Not implemented"
	
	def delete (self, table, column, value):
		"""
		Elimina qualcosa dalla tabella table
		table => nome della tabella
		column => la colonna su cui eseguire il matching
		value => il valore della colonna
		
		Si eseguira' in questo caso un
		DELETE FROM table WHERE column=value
		"""
		raise "Not implemented"
	
	def refresh_pending_windows (self):
		if not app.App: return

		for win in app.App.p_window:
			if app.App.p_window[win]:
				w = app.App.p_window[win]
				if isinstance (w, DBWindow):
					w.refresh_all_pages ()

def get_backend_class ():
	if impostazioni.get ("betype") == "sqlite":
		import sqlitebe
		return sqlitebe.sqliteBE
