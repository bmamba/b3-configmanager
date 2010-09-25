import os
import sys
import cm_menu
import cm_tui
import cm_plugin
import cm_parser

class ConfigManager:

	def __init__(self):
		self._b3xml = 'b3.xml'
		if not os.path.exists(self._b3xml) or not os.path.isfile(self._b3xml):
			print('Could not open main configuration file')
			sys.exit(-1)
		self._b3parser = cm_parser.Parser()
		self._b3parser.loadFile(self._b3xml)
		self._ui = cm_tui.TUI()
		self._ui.setHeader("ConfigManager")
		self._ui.setKeyListener(self._keyListener)

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

		plugins = self._b3parser.getPlugins()
		for plugin in plugins:
			pmenu = cm_menu.Menu()
			pmenu.setText(plugin.getName())
			pmenu.setButtonFunction(self._menuListener)
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
	
	def exit(self, button = None):
		self._ui.exit()

	def start(self):
		self._createMenu()
		self._ui.showMenu(self._mainmenu)
		self._ui.start()


configmanager = ConfigManager()
configmanager.start()
