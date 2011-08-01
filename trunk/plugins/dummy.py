import gtk
import app
import impostazioni

class dummy:
	__name__ = "dummy plugin"
	__desc__ = "a dummy plugin"
	__ver__ = "0.0.1"
	__author__ = "PyAcqua team"
	__preferences__ = {
		'dummy_nervose_mode' : False
	}

	def start (self):
		print ">> Starting", self.__name__
		
		print ">> Dummy.. showtips :", impostazioni.get("show_tips")
		
		if impostazioni.get("dummy_nervose_mode"):
			print "Prova"
		
		menu = app.App.get_plugin_menu ()

		self.item = gtk.MenuItem ("Dummy Plugin")
		self.item.connect ('activate', self.on_activated)
		self.item.show ()

		menu.append (self.item)

	def stop (self):
		print "** Stopping", self.__name__

		self.item.hide ()
		self.item.destroy ()
	
	def on_activated(self, widget):
		print "clicked"
