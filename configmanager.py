import os, sys, getopt
import cm_menu
import cm_tui
import cm_plugin
import cm_parser

__author__ = 'BlackMamba'
__version__ = '0.1.0'

class ConfigManager:

	def __init__(self):
		self._b3Dir = None
		self._b3Confdir = None
		self._b3xml = None
		try:
			opts, args = getopt.getopt(sys.argv[1:],'hvc:', ['help', 'version', 'b3=', 'config-file=', 'config-dir='])
		except getopt.GetoptError, err:
			print str(err)
			sys.exit(1)
		for opt, arg in opts:
			if opt in ['--version','-v']:
				print('ConfigManager '+__version__+' by '+__author__)
				sys.exit(0)
			elif opt in ['--help','-h']:
				print(self.usage())
				sys.exit(0)
			elif opt == '--b3':
				self._b3Dir = arg
			elif opt == 'config-dir':
				self._b3dir = arg
			elif opt in ['-c', '--config-file']:
				self._b3xml = arg
		if self._b3Dir is None:
			self._b3Dir = '.'
		if self._b3Confdir is None:
			self._b3Confdir = self._b3Dir+'/conf'
		if self._b3xml is None:
			self._b3xml = self._b3Confdir+'/b3.xml'
		if not os.path.exists(self._b3xml) or not os.path.isfile(self._b3xml):
			print('Could not open main configuration file. Use option -c to identify the configuration file of b3. Use option -h to get more informations.')
			sys.exit(-1)
		self._b3parser = cm_parser.Parser()
		self._b3parser.loadFile(self._b3xml)
		self._b3extconf = self._b3parser.getExtconfPath()
		self._ui = cm_tui.TUI()
		self._ui.setHeader("ConfigManager")
		self._ui.setKeyListener(self._keyListener)

	def usage(self):
		text = "Usage: python configmanager.py [OPTION...]\n"
		text += " --b3=DIR                define the place where b3 is\n"
		text += "                         if not given DIR=.\n"
		text += " --config-dir=CONFDIR    define the place where the configuration is\n"
		text += "                         if not given CONFDIR=DIR/conf\n"
		text += " -c, --config-file=FILE  define main configuration file\n"
		text += "                         if not given FILE=CONFDIR/b3.xml\n"
		text += " -h, --help              show this text\n"
		text += " -v, --version           show the version\n"
		return text

	def _keyListener(self,key):
		if key == 'esc':
			self._ui.exit()

	def _menuListener(self, button):
		self._ui.setFooter("bla")

	def _createMenu(self):
		self._mainmenu = cm_menu.Menu()
		self._mainmenu.setText('Main menu')

		menu = cm_menu.Menu()
		menu.setText('Configure main settings')
		menu.setButtonFunction(self._menuListener)
		self._mainmenu.addSubmenu(menu)

		menu = cm_menu.Menu()
		menu.setText('Configure plugins')
		menu.setButtonFunction(self._menuListener)

		self._plugins = self._b3parser.getPlugins()
		for name in self._plugins:
			plugin = self._plugins[name]
			if plugin.getConfig() is not None:
				pmenu = cm_menu.Menu()
				pmenu.setText(plugin.getName())
				pmenu.setButtonFunction(self._confPluginListener)
				menu.addSubmenu(pmenu)

		self._mainmenu.addSubmenu(menu)

		menu = cm_menu.Menu()
		menu.setText('(De-)Activate plugins')
		menu.setButtonFunction(self._menuListener)
		self._mainmenu.addSubmenu(menu)

		menu = cm_menu.Menu()
		menu.setText('Quit')
		menu.setButtonFunction(self.exit)
		self._mainmenu.addSubmenu(menu)

	def _confPluginListener(self, menu):
		self._ui.setFooter(menu.getText())
		page = cm_tui.Page(menu.getText())
		parser = cm_parser.Parser()
		plugin = self._plugins[menu.getText()]
		file = plugin.getConfig().replace('@conf',self._b3Confdir)
		file = file.replace('@b3',self._b3Dir)
		parser.loadFile(file)
		pluginConf = parser.getPluginConf()
		for section in pluginConf:
			page.addHeader(section)
			for setting in pluginConf[section]:
				page.addInsertField(setting, pluginConf[section][setting], section)
		self._page = page
		self._ui.setBody(page.getPage())
	
	def exit(self, button = None):
		self._ui.exit()

	def start(self):
		self._createMenu()
		self._ui.showMenu(self._mainmenu)
		self._ui.start()


configmanager = ConfigManager()
configmanager.start()
