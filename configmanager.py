import cm_menu
import cm_tui

class ConfigManager:

	def __init__(self):
		self._ui = cm_tui.TUI()
		self._ui.setHeader("ConfigManager")
		self._ui.setKeyListener(self._keylistener)

	def _keylistener(self,key):
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
