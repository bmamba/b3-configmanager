class Menu:
	#parent
	#text
	#button_function
	#children

	def __init__(self):
		self.parent = None
		self.text = ""
		self.buttonFunction = None
		self.button = None
		self.children = []

	def setButtonFunction(self, function):
		self.buttonFunction = function

	def getButtonFunction(self):
		return self.buttonFunction

	def setText(self, text):
		self.text = text

	def getText(self):
		return self.text

	def setParent(self, parent):
		self.parent = parent

	def getParent(self):
		return self.parent

	def addSubmenu(self, menu):
		if menu.getParent() is None:
			menu.setParent(self)
		self.children.append(menu)

	def setSubmenus(self, menus):
		self.children = menus

	def getSubmenus(self):
		return self.children

	def getMenuByText(self, searchText):
		if (self.text == searchText):
			return self
		elif (self.children != []):
			for child in self.children:
				found = child.getMenuByText(searchText)
				if (found != None):
					return found
			return None
		else:
			return None

