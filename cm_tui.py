import urwid
import cm_menu

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
		self._keylistener = listener

	def unhandled(self,key):
		self._keylistener(key)

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
	
	def _menuListener(self, button):
		menu = self._currentMenu.getMenuByText(button.get_label())
		self._frame.footer = urwid.AttrWrap(urwid.Text(menu.getText()), 'header')
		if len(menu.getSubmenus()) == 0:
			menu.getButtonFunction()(menu)
		else:
			self._currentMenu = menu
			self._showMenu()


