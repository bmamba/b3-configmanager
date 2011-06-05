import os, sys, getopt
import cm_menu
import cm_tui
import cm_plugin
import cm_parser
import cm_log
import cm_conf

__author__ = 'BlackMamba'
__version__ = '0.1'

class ConfigManager:

	def __init__(self):
		self._logger = cm_log.getLogger('configmanager')
		self._b3Dir = None
		self._b3Confdir = None
		self._b3xml = None
		self._b3PluginsDir = None
		self._b3ExtDir = None
		self._b3ExtConfDir = None
		conf = cm_conf.Conf()
		conf.loadFile('cm_conf.xml')
		try:
			opts, args = getopt.getopt(sys.argv[1:],'hvc:', ['help', 'version', 'b3=', 'config-file=', 'config-dir=', 'b3-dir=', 'extplugin-dir=', 'extconf-dir='])
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
			elif opt == '--b3-dir':
				self._b3Dir = arg
			elif opt == '--config-dir':
				self._ConfDir = arg
			elif opt in ['-c', '--config-file']:
				self._b3xml = arg
			elif opt == '--extplugin-dir':
				self._b3ExtDir = arg
			elif opt == '--extconf-dir':
				self._b3ExtConfDir = arg
		if self._b3Dir is None:
			self._b3Dir = conf.getSet('b3dir')
			if self._b3Dir is None:
				self._logger.debug('b3Dir not given and not find in configuration file')
				print(self.usage())
				sys.exit(0)
		else:
			self._b3Dir = self._b3Dir+'/b3'
			self._b3Dir = os.path.expanduser(self._b3Dir)
			self._b3Dir = os.path.abspath(self._b3Dir)
			if not os.path.exists(self._b3Dir):
				print('Could not find b3. Use option -h to get more informations.')
				self._logger.error('Could not find b3. Given path: '+self._b3Dir)
				sys.exit(0)

			b3Dir = conf.getSet('b3dir')
			if self._b3Dir != b3Dir:
				#resetting paths if main path was changed
				self._logger.debug('Removing paths from config since main path was changed')
				conf.removeSet('b3dir')
				conf.removeSet('b3confdir')
				conf.removeSet('b3xml')
				conf.removeSet('b3pluginsdir')
				conf.removeSet('b3extdir')
				conf.removeSet('b3extconfdir')
		if self._b3Confdir is None:
			self._b3Confdir = conf.getSet('b3confdir')
			if self._b3Confdir is None:
				self._b3Confdir = self._b3Dir+'/conf'
		if self._b3xml is None:
			self._b3xml = conf.getSet('b3xml')
			if self._b3xml is None:
				self._b3xml = self._b3Confdir+'/b3.xml'
		if self._b3PluginsDir is None:
			self.b3PluginsDir = conf.getSet('b3pluginsdir')
			if self._b3PluginsDir is None:
				self._b3PluginsDir = self._b3Dir+'/plugins'
		if self._b3ExtDir is None:
			self.b3ExtDir = conf.getSet('b3extdir')
			if self._b3ExtDir is None:
				self._b3ExtDir = self._b3Dir+'/extplugins'
		if self._b3ExtConfDir is None:
			self.b3ExtConfDir = conf.getSet('b3extconfdir')
			if self._b3ExtConfDir is None:
				self._b3ExtConfDir = self._b3ExtDir+'/conf'
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
		conf.setSet("b3dir",self._b3Dir)
		self._b3Confdir = os.path.abspath(self._b3Confdir)
		conf.setSet("b3confdir",self._b3Confdir)
		self._b3xml = os.path.abspath(self._b3xml)
		conf.setSet("b3xml", self._b3xml)
		self._b3PluginsDir = os.path.abspath(self._b3PluginsDir)
		conf.setSet("b3pluginsdir", self._b3PluginsDir)
		self._b3ExtDir = os.path.abspath(self._b3ExtDir)
		conf.setSet("b3extdir", self._b3ExtDir)
		self._b3ExtConfDir = os.path.abspath(self._b3ExtConfDir)
		conf.setSet("b3extconfdir", self._b3ExtConfDir)
		self._logger.debug('B3 directory: '+self._b3Dir)
		self._logger.debug('Configuration directory: '+self._b3Confdir)
		self._logger.debug('b3.xml: '+self._b3xml)
		self._logger.debug('Internal plugins: '+self._b3PluginsDir)
		self._logger.debug('External plugins: '+self._b3ExtDir)
		self._logger.debug('Configuration directory for external plugins: '+self._b3ExtConfDir)
		conf.saveFile()
		self._b3parser = cm_parser.Parser()
		self._b3parser.loadFile(self._b3xml)
		self._ui = cm_tui.TUI()
		self._ui.setHeader("ConfigManager")
		self._ui.setKeyListener(self._keyListener)

	def usage(self):
		text = "Usage: python configmanager.py [OPTIONS...]\n\n"
		text += " --b3-dir=B3DIR            define the place where b3 is\n"
		text += "                           if not given: B3DIR from last time\n"
		text += " --config-dir=CONFDIR      define the place where the configuration is\n"
		text += "                           if not given: CONFDIR from last time\n"
		text += "                           or CONFDIR=B3DIR/b3/conf\n"
		text += " --plugin-dir=PLUGINDIR    define the place of the internal plugins\n"
		text += "                           if not given: PLUGINDIR from last time\n"
		text += "                           or PLUGINDIR=B3DIR/b3/plugins\n"
		text += " -c, --config-file=FILE    define main configuration file\n"
		text += "                           if not given: FILE from last time\n"
		text += "                           or FILE=CONFDIR/b3.xml\n"
		text += " --extplugin-dir=EXTDIR    define the place of the external plugins\n"
		text += "                           if not given: EXTDIR from last time\n"
		text += "                           or EXTDIR=B3DIR/b3/extplugins\n"
		text += " --extconf-dir=EXTCONFDIR  define the place of the configuration of external plugins\n"
		text += "                           if not given: FILE from last time\n"
		text += "                           or EXTCONFDIR=EXTDIR/conf\n"
		text += " -h, --help                show this text\n"
		text += " -v, --version             show the version\n"
		return text

	def _keyListener(self,key):
		if key == 'esc':
			self._ui.exit()

	def _menuListener(self, button):
		self._ui.setFooter("This function is not implemented yet.")

	def _createMenu(self):
		self._mainmenu = cm_menu.Menu()
		self._mainmenu.setText('Main menu')

		menu = cm_menu.Menu()
		menu.setText('Configure main settings')
		menu.setButtonFunction(self._confPluginListener)
		self._mainmenu.addSubmenu(menu)

		menu = cm_menu.Menu()
		menu.setText('Configure plugins')
		menu.setButtonFunction(self._menuListener)

		self._plugins = self._b3parser.getPlugins()
		for name in self._plugins:
			plugin = self._plugins[name]
			if plugin.config is not None:
				pmenu = cm_menu.Menu()
				pmenu.setText(plugin.name)
				pmenu.setButtonFunction(self._confPluginListener)
				menu.addSubmenu(pmenu)

		self._mainmenu.addSubmenu(menu)

		menu = cm_menu.Menu()
		menu.setText('(De-)Activate plugins')
		menu.setButtonFunction(self._activatePlugins)
		self._mainmenu.addSubmenu(menu)

		menu = cm_menu.Menu()
		menu.setText('Configure Database')
		menu.setButtonFunction(self._confDatabase)
		self._mainmenu.addSubmenu(menu)


		menu = cm_menu.Menu()
		menu.setText('Quit')
		menu.setButtonFunction(self.exit)
		self._mainmenu.addSubmenu(menu)


	def _confDatabase(self, menu):
		parser = cm_parser.Parser()
		page = cm_tui.Page(self._ui, menu.getText())
		file = self._b3Confdir+'/b3.xml'
		parser.loadFile(file)
		pluginConf = parser.getPluginConf()
		mysql = parser.getSetData("b3","database")
		text = mysql.split('/')
		connection = text[2]
		database = text[3]
		text = connection.split('@')
		if len(text)>1:
			userpw = text[0]
			host = text[1]
			text = userpw.split(':')
			user = text[0]
			if len(text)>1:
				password = text[1]
			else:
				password = ''
		else:
			user = ''
			password = ''
			host = text[0]
		text = host.split(':')
		if len(text)>1:
			host = text[0]
			port = text[1]
		else:
			port = ''
		page.addBlank()
		page.addInsertField("Host:",host)
		page.addInsertField("Port:",port)
		page.addInsertField("Database name:",database)
		page.addInsertField("User:",user)
		page.addInsertField("Password:",password)
		page.addBlank()
		page.addSaveButton(self._saveDatabaseConfiguration)
		self._page = page
		self._ui.setBody(page.getPage())
		self._pluginParser = parser

	def _confPluginListener(self, menu):
		self._ui.setFooter(menu.getText())
		parser = cm_parser.Parser()
		if menu.getText() == "Configure main settings":
			page = cm_tui.Page(self._ui, menu.getText())
			file = self._b3Confdir+'/b3.xml'
			name = 'b3'
		else:
			page = cm_tui.Page(self._ui, 'Configure '+menu.getText())
			plugin = self._plugins[menu.getText()]
			file = plugin.config.replace('@conf',self._b3Confdir)
			file = file.replace('@b3',self._b3Dir)
			name = menu.getText()
		parser.loadFile(file)
		parser.loadExtraFile('cm_conf/'+name+'.xml')
		pluginConf = parser.getPluginConf()
		pluginExtraConf = parser.getPluginExtraConf()
		for section in pluginConf:
			page.addBlank()
			page.addHeader(section)
			for setting in pluginConf[section]:
				page.addBlank()
				try:
					comment = pluginExtraConf[section][setting]['comment']
				except:
					comment = pluginConf[section][setting]['comment']
				if comment != '':
					comment = comment.expandtabs(1).strip()
					page.addComment(comment)
				input = None
				try:
					input = pluginExtraConf[section][setting]['input']
					if input['type'] == 'radiobutton':
						for value in input['values'].keys():
							page.addRadioButton(section, setting, input['values'][value], pluginConf[section][setting]['value'])
					else:
						raise
				except:
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

	def _saveDatabaseConfiguration(self):
		self._ui.setFooter('save')
		values = self._page.getInsertValues()
		host = values['Host:']['value']
		port = values['Port:']['value']
		dbname = values['Database name:']['value']
		user = values['User:']['value']
		password = values['Password:']['value']
		mysql = 'mysql://'
		if user != '':
			mysql += user
			if password != '':
				mysql += ':'+password
			mysql += '@'
		mysql += host
		if port != '':
			mysql += ':'+port
		mysql += '/'+dbname
		self._logger.debug('mysql connection string: '+mysql)
		parser = self._pluginParser
		parser.setSetData("b3","database",mysql)
		parser.saveFile()

	def _activatePlugins(self, menu):
		self._ui.setFooter(menu.getText())
		page = cm_tui.Page(self._ui, menu.getText())
		self._page = page
		file = self._b3Confdir+'/b3.xml'
		parser = cm_parser.Parser()
		parser.loadFile(file)

		page.addBlank()
		dirlist = {}
		dirlist[self._b3PluginsDir] = self._b3Confdir
		dirlist[self._b3ExtDir] = self._b3ExtConfDir

		plugins = parser.getAllPlugins(dirlist)

		for plugin in plugins:
			p = plugins[plugin]
			page.addHeader(p.name)
			if p.active == 0: selectedValue = 'not active'
			else: selectedValue = 'active'
			page.addRadioButton(p.name,'Status','active',selectedValue)
			page.addRadioButton(p.name,'Status','not active',selectedValue)
			if p.priority is None: priority = ''
			else: priority = str(p.priority)
			page.addBlank()
			page.addInsertField('Priority',priority,p.name) #.type
			page.addBlank()
			page.addBlank()
		page.addSaveButton(self._saveActivePluginsConfiguration)
		self._ui.setBody(page.getPage())
		self._parser = parser
		self._allplugins = plugins

	def _saveActivePluginsConfiguration(self):
		self._ui.setFooter('save')
		self._parser.changePluginActivation(self._page.getInsertValues(), self._allpluginsnconf)
		self._parser.saveFile()

	def exit(self, button = None):
		self._ui.exit()

	def start(self):
		self._createMenu()
		self._ui.showMenu(self._mainmenu)
		self._ui.start()


configmanager = ConfigManager()
configmanager.start()
