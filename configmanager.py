import os, sys, getopt
import cm_menu
import cm_tui
import cm_plugin
import cm_parser
import cm_log

__author__ = 'BlackMamba'
__version__ = '0.1.1'

class ConfigManager:

	def __init__(self):
		self._logger = cm_log.getLogger('configmanager')
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
			elif opt == 'config-dir':
				self._b3Dir = arg
			elif opt in ['-c', '--config-file']:
				self._b3xml = arg
		if len(args) != 1:
			print(self.usage())
			sys.exit(0)
		self._b3Dir = args[0]+'/b3'
		if self._b3Confdir is None:
			self._b3Confdir = self._b3Dir+'/conf'
		if self._b3xml is None:
			self._b3xml = self._b3Confdir+'/b3.xml'
		if not os.path.exists(self._b3Dir):
			print('Could not find b3. Use option -h to get more informations.')
			self._logger.error('Could not find b3. Given path: '+self._b3Dir)
			sys.exit(0)
		if not os.path.exists(self._b3Confdir):
			print('Could not find path for the configuration files. Use option --config-dir. To get more informations use option -h.')
			self._logger.error('Could not find configuration directory. Given path: '+self._b3Confdir)
			sys.exit(0)
		if not os.path.exists(self._b3xml) or not os.path.isfile(self._b3xml):
			print('Could not open main configuration file. Use option -c to identify the configuration file of b3. Use option -h to get more informations.')
			self._logger.error('Could not find b3.xml. Given file: '+self._b3xml)
			sys.exit(0)
		self._b3Dir = os.path.abspath(self._b3Dir)
		self._b3Confdir = os.path.abspath(self._b3Confdir)
		self._b3xml = os.path.abspath(self._b3xml)
		self._logger.debug('B3 directory: '+self._b3Dir)
		self._logger.debug('Configuration directory: '+self._b3Confdir)
		self._logger.debug('b3.xml: '+self._b3xml)
		self._b3parser = cm_parser.Parser()
		self._b3parser.loadFile(self._b3xml)
		self._ui = cm_tui.TUI()
		self._ui.setHeader("ConfigManager")
		self._ui.setKeyListener(self._keyListener)

	def usage(self):
		text = "Usage: python configmanager.py [OPTIONS...] B3DIR\n\n"
		text += " B3DIR                   define the place where b3 is\n\n"
		text += " --config-dir=CONFDIR    define the place where the configuration is\n"
		text += "                         if not given: CONFDIR=B3DIR/b3/conf\n"
		text += " -c, --config-file=FILE  define main configuration file\n"
		text += "                         if not given: FILE=CONFDIR/b3.xml\n"
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
		page = cm_tui.Page(self._ui, 'Configure '+menu.getText())
		parser = cm_parser.Parser()
		plugin = self._plugins[menu.getText()]
		file = plugin.getConfig().replace('@conf',self._b3Confdir)
		file = file.replace('@b3',self._b3Dir)
		parser.loadFile(file)
		pluginConf = parser.getPluginConf()
		for section in pluginConf:
			page.addBlank()
			page.addHeader(section)
			for setting in pluginConf[section]:
				page.addBlank()
				comment = pluginConf[section][setting]['comment']
				if comment != '':
					comment = comment.expandtabs(1).strip()
					page.addComment(comment)
				page.addInsertField(setting, pluginConf[section][setting]['value'], section)
		page.addBlank()
		page.addSaveButton(self._savePluginConfiguration)
		page.addBlank()
		self._page = page
		self._ui.setBody(page.getPage())
		self._pluginParser = parser

	def _savePluginConfiguration(self):
		self._ui.setFooter('save')
		self._pluginParser.changePluginConfiguration(self._page.getInsertValues())
		self._pluginParser.saveFile()

	def exit(self, button = None):
		self._ui.exit()

	def start(self):
		self._createMenu()
		self._ui.showMenu(self._mainmenu)
		self._ui.start()


configmanager = ConfigManager()
configmanager.start()
