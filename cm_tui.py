import urwid
import cm_menu
import cm_log

class TUI:

	def __init__(self):
		self._blank = urwid.Divider()
		self._frame = urwid.Frame(urwid.Text(""))
		self._frame.footer = urwid.AttrWrap(urwid.Text("Press <ESC> to exit"), 'header')
		self._palette = [
			('body','black','light gray', 'standout'),
			('reverse','light gray','black'),
			('header','white','dark blue', 'bold'),
			('important','dark blue','light gray',('standout','underline')),
			('editfc','white', 'dark blue', 'bold'),
			('editbx','light gray', 'dark blue'),
			('editcp','black','light gray', 'standout'),
			('bright','dark gray','light gray', ('bold','standout')),
			('buttn','black','dark cyan'),
			('buttnf','white','dark blue','bold'),
		]
		self.setBody(urwid.Filler(urwid.Text("")))

	def setKeyListener(self,listener):
		self._keyListener = listener

	def unhandled(self,key):
		if key == 'esc':
			if self._currentMenu.getParent() is None:
				self._keyListener(key)
			else:
				self._currentMenu = self._currentMenu.getParent()
				self._showMenu()
		else:
			self._keyListener(key)

	def start(self):
		loop = urwid.MainLoop(self._frame, self._palette, unhandled_input=self.unhandled)
		loop.run()

	def exit(self):
		raise urwid.ExitMainLoop()

	def setHeader(self,text):
		self._frame.header = urwid.AttrWrap(urwid.Text(text), 'header')

	def setFooter(self,text):
		self._frame.footer = urwid.AttrWrap(urwid.Text(text), 'header')

	def setBody(self,body):
		self._frame.body = urwid.AttrWrap(body,'body')

	def showMenu(self, menu):
		self._currentMenu = menu
		self._showMenu()

	def _showMenu(self):
		if self._currentMenu is None:
			return
		menulist = [
			self._blank,
			urwid.Text(('important',self._currentMenu.getText())),
			self._blank
		]
		for child in self._currentMenu.getSubmenus():
			menulist.append(urwid.AttrWrap(urwid.Button(child.text, self._menuListener),'buttn','buttnf'))
		if self._currentMenu.getParent() is not None:
			menulist.append(urwid.AttrWrap(urwid.Button(self._currentMenu.getParent().getText(), self._menuListener,'buttn'),'buttnf'))
		listbox = urwid.ListBox(urwid.SimpleListWalker(menulist))
		self._frame.body = urwid.AttrWrap(listbox,'body')
		if self._currentMenu.getParent() is None:
			self._frame.footer = urwid.AttrWrap(urwid.Text("Press <ESC> to exit"), 'header')
		else:
			self._frame.footer = urwid.AttrWrap(urwid.Text("Press <ESC> to go up"), 'header')
	
	def _menuListener(self, button, st = ""):
		menu = self._currentMenu.getMenuByText(button.get_label())
		if menu is None and self._currentMenu.getParent() is not None:
			menu = self._currentMenu.getParent().getMenuByText(button.get_label())
		self._frame.footer = urwid.AttrWrap(urwid.Text(menu.getText()), 'header')
		if len(menu.getSubmenus()) == 0:
			self._currentMenu = menu
			menu.getButtonFunction()(menu)
		else:
			self._currentMenu = menu
			self._showMenu()

	def showParentMenu(self):
		if self._currentMenu.getParent() is not None:
			self._currentMenu = self._currentMenu.getParent()
			self._showMenu()


class Page:

	def __init__(self, tui, title):
		self._logger = cm_log.getLogger('cm_tui_Page')
		self._tui = tui
		self._blank = urwid.Divider()
		self._lengthText = 27
		self._widthField = 50
		self._edit = None
		self._radioGroup = {}
		self._page = [
			self._blank,
			urwid.Text(('important',title)),
		]

	def _addSpaces(self, text):
		if self._lengthText-len(text)>0:
			text += " "*(self._lengthText-len(text))
		return text

	def getPage(self):
		return urwid.ListBox(urwid.SimpleListWalker(self._page))

	def addInsertField(self, text, value = '', section = None):
		edit = urwid.Edit(('editcp',self._addSpaces(text)),value)
		if self._edit is None:
			self._edit = {}
		if section is None:
			self._edit[text] = edit
		else:
			if not self._edit.has_key(section):
				self._edit[section] = {}
			self._edit[section][text] = edit
		self._page.extend([
			urwid.Padding(urwid.AttrWrap(edit,'editbx', 'editfc'),width=self._widthField+self._lengthText)
		])

	def addRadioButton(self, section, name, value, selectedValue):
		if self._radioGroup is None:
			self._radioGroup = {}
		if section not in self._radioGroup:
			self._radioGroup[section] = {}
		if name not in self._radioGroup[section]:
			self._radioGroup[section][name] = []
		rbutton = urwid.RadioButton(self._radioGroup[section][name],value)
		if value == selectedValue:
			rbutton.toggle_state()
		self._page.extend([
			urwid.Padding(urwid.AttrWrap(rbutton,'buttn','buttnf'),width=self._widthField,left=self._lengthText)
		])


	def getInsertValues(self):
		values = {}

		# Input
		for a in self._edit:
			values[a] = {}
			for b in self._edit[a]:
				values[a][b] = {}
				values[a][b]['value'] = self._edit[a][b].get_edit_text()

		# RadioButton
		for section in self._radioGroup:
			if section not in values:
				values[section] = {}
			for name in self._radioGroup[section]:
				values[section][name] = {}
				value = ''
				for rbutton in self._radioGroup[section][name]:
					if rbutton.get_state():
						value = rbutton.get_label()
				values[section][name]['value'] = value

		return values

	def addComment(self, comment):
		self._page.extend([
			urwid.Text(comment)
		])

	def addHeader(self, header):
		self._page.extend([
			urwid.Text(('important', header))
		])

	def addBlank(self):
		self._page.extend([
			self._blank
		])

	def addSaveButton(self, saveListener):
		self._page.extend([
			urwid.GridFlow(
			[urwid.AttrWrap(urwid.Button('Save', self._buttonConfigurationListener), 'buttn', 'buttnf'),
			urwid.AttrWrap(urwid.Button('Cancel', self._buttonConfigurationListener), 'buttn', 'buttnf')]
			,10,5,5,'center')
		])
		self._configurationSaveListener = saveListener

	def _buttonConfigurationListener(self, button):
		if button.get_label() == 'Save':
			self._configurationSaveListener()
		self._tui.showParentMenu()
