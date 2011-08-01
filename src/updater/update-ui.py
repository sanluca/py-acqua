import gtk

class UpdateUi(gtk.Window):#, UpdateEngine):
	def __init__(self):
		gtk.Window.__init__(self)
		#UpdateEngine.__init__(self, "old.db")
		
		#utils.set_icon(self)
		self.set_title("Web Update")
		self.set_size_request(600, 400)
		
		self.actions_store = gtk.ListStore(str)
		
		for i in ("Add/Update", "Remove", "Ignore", "Custom"):
			self.actions_store.append([i])
		
		self.nb = gtk.Notebook()
		self.nb.append_page(self.prepareComponentsPage())
		self.nb.append_page(self.prepareDownloadPage())
		self.nb.append_page(self.prepareAdvancedPage())
		
		self.add(self.nb)
		self.show_all()
	
	def prepareComponentsPage(self):
		vbox = gtk.VBox(False, 2)
		
		self.cmp_store = gtk.ListStore(
			gtk.gdk.Pixbuf,	# icon
			str,		# name
			str,		# remote version
			str,		# local version
			str,
			gtk.gdk.Color
		)
		
		self.cmp_view = gtk.TreeView(self.cmp_store)
		
		rend = gtk.CellRendererPixbuf()
		col = gtk.TreeViewColumn("Name", rend, pixbuf=0)
		col.set_attributes(rend, cell_background_gdk=5)

		rend = gtk.CellRendererText()
		col.pack_start(rend)
		col.set_attributes(rend, text=1, cell_background_gdk=5)

		self.cmp_view.append_column(col)
		self.cmp_view.append_column(gtk.TreeViewColumn("RVer", rend, text=2))
		self.cmp_view.append_column(gtk.TreeViewColumn("LVer", rend, text=3))
		
		rend = gtk.CellRendererCombo()
		
		rend.set_property("model", self.actions_store)
		rend.set_property("text-column", 0)
		rend.set_property("editable", True)
		rend.set_property("has-entry", False)
		
		rend.connect("edited", self.__onEditAction, self.cmp_store)
		
		col = gtk.TreeViewColumn("Action", rend, markup=4)
		col.set_attributes(rend, markup=4, cell_background_gdk=5)

		self.cmp_view.append_column(col)
		
		# TEST
		self.cmp_store.append([None, "unz", "1.2", "1.1", "", self.getColorForAction("Add/Update")])
		self.cmp_store.append([None, "unz", "1.2", "1.1", "", self.getColorForAction("Add/Update")])
		self.cmp_store.append([None, "unz", "1.2", "1.1", "", self.getColorForAction("Add/Update")])
		self.cmp_store.append([None, "unz", "1.2", "1.1", "", self.getColorForAction("Add/Update")])

		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		sw.add(self.cmp_view)
		
		vbox.pack_start(sw)
		
		return vbox
	
	def prepareAdvancedPage(self):
		vbox = gtk.VBox(False, 20)

		self.adv_store = gtk.TreeStore(
			gtk.gdk.Pixbuf,	# icon for actions
			str,		# dir -> file
			str,		# remote version
			str,		# local versionA
			bool,		# download
			bool,		# ignore
			str,		# perc -> perc (string error)
			int,		# perc -> perc
			gtk.gdk.Color
		)
		
		self.adv_view = gtk.TreeView(self.adv_store)

		rend = gtk.CellRendererPixbuf()
		col = gtk.TreeViewColumn("Name", rend, pixbuf=0)

		rend = gtk.CellRendererText()
		col.pack_start(rend)
		#col.set_attributes(rend, text=1, background-gdk=5)

		self.adv_view.append_column(gtk.TreeViewColumn("Name", rend, text=1, cell_background_gdk=8))
		self.adv_view.append_column(gtk.TreeViewColumn("RVer", rend, text=2, cell_background_gdk=8))
		self.adv_view.append_column(gtk.TreeViewColumn("LVer", rend, text=3, cell_background_gdk=8))

		self.adv_view.get_column(0).set_expand(True)

		for i, z in zip(("D", "I"), (4, 5)):
			rend = gtk.CellRendererToggle()
			
			rend.set_property('activatable', True)
			rend.set_property('radio', rend)
			rend.connect('toggled', self.__onToggleAction, (self.adv_store, z))

			col = gtk.TreeViewColumn(i, rend)

			col.set_attributes(rend, active=z, cell_background_gdk=8)
			col.set_max_width(20)

			self.adv_view.append_column(col)

		col = gtk.TreeViewColumn("%", gtk.CellRendererProgress(), text=6, value=7, cell_background_gdk=8)
		col.set_min_width(150)

		self.adv_view.append_column(col)

		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		sw.add(self.adv_view)

		vbox.pack_start(sw)

		#TEST
		it = self.adv_store.append(None, [None, "asd", "asd", "asd", True, False, "Downloading...", 100, self.getColorForAction('Ignore')])
		it = self.adv_store.append(it, [None, "asd", "asd", "asd", True, False, "unz", 0, self.getColorForAction('Ignore')])
		it = self.adv_store.append(it, [None, "asd", "asd", "asd", True, False, "unz", 0, self.getColorForAction('Ignore')])

		return vbox
	
	def prepareDownloadPage(self):
		vbox = gtk.VBox(False, 20)
		
		self.detail_lbl = gtk.Label("<b>Downloading basic system ...</b>")
		self.global_lbl = gtk.Label("<b>Downloading basic system ...</b>")
		
		self.detail_sb = gtk.ProgressBar()
		self.global_sb = gtk.ProgressBar()
		
		for i in (self.detail_lbl, self.global_lbl):
			i.set_alignment(0, 1.0)
			i.set_use_markup(True)
		
		tbl = gtk.Table(4, 1, False)
		tbl.set_border_width(20)
		tbl.set_row_spacings(5)
		
		tbl.attach(self.detail_lbl, 0, 1, 0, 1, yoptions=gtk.FILL)
		tbl.attach(self.global_lbl, 0, 1, 2, 3)
		
		tbl.attach(self.detail_sb, 0, 1, 1, 2, yoptions=gtk.FILL)
		tbl.attach(self.global_sb, 0, 1, 3, 4, yoptions=gtk.FILL)
		
		vbox.pack_start(tbl)
		
		return vbox
	
	def getColorForAction(self, action):
		c_dict = {
			'Add/Update' : gtk.gdk.color_parse('#bcfffc'),
			'Remove' :     gtk.gdk.color_parse('#ff8080'),
			'Ignore' :     gtk.gdk.color_parse('#80ff80'),
			'Custom' :     gtk.gdk.color_parse('#80ff80')
		}

		if action in c_dict:
			return c_dict[action]
		else:
			return None
	
	def __onEditAction(self, crt, path, new_text, store):
		if not new_text: return

		it = store.get_iter_from_string(path)

		store.set_value(it, 4, "<b>%s</b>" % new_text)

		color = self.getColorForAction(new_text)

		if color != None:
			store.set_value(it, 5, color)

	def __onToggleAction(self, crt, path, user_data):
		store, col = user_data

		root = store.get_iter_from_string(path)

		self.__recursiveSet(store, col, root)

		store[path][4] = False
		store[path][5] = False

		store[path][col] = True
	
	def __recursiveSet(self, store, col, root):
		store.set_value(root, 8,
			(col == 4) and
				(self.getColorForAction("Add/Update")) or
				(self.getColorForAction("Ignore"))
		)
		
		if not store.iter_has_child(root):
			return

		child = store.iter_children(root)

		while child != None:
			store.set_value(child, 4, False)
			store.set_value(child, 5, False)
			store.set_value(child, col, True)

			store.set_value(child, 8, (col == 4) and (self.getColorForAction("Add/Update")) or (self.getColorForAction("Ignore")))

			self.__recursiveSet(store, col, child)

			child = store.iter_next(child)

if __name__ == "__main__":
	ui = UpdateUi()
	gtk.main()
