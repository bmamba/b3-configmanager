
class Plugin:
	
	def __init__(self, name):
		self._name = name
		self._priority = None
		self._config = None
		self._active = 1

	def setName(self, name):
		self._name = name

	def getName(self):
		return self._name

	def setPriority(self, priority):
		self._priority = priority

	def getPriority(self):
		return self.priority

	def setConfig(self, config):
		self._config = config

	def getConfig(self):
		return self._config

	def setActive(self, active):
		self._active = active

	def getActive(self):
		return self._active
