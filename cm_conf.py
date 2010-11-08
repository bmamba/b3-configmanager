import xml.dom.minidom
import cm_log

class Conf:

	def __init__(self):
		self._logger = cm_log.getLogger('cm_conf')
	
	def loadFile(self, file):
		self._logger.info('Reading file '+file)
		try:
			filehandle = open(file, 'r')
			self._xml = xml.dom.minidom.parse(filehandle)
			filehandle.close()
			self._file = file
		except IOError, err:
			self._logger.warning(str(err))


	def saveFile(self):
		self._logger.info('Writing xml into '+self._file)
		try:
			filehandle = open(self._file, 'w')
			filehandle.write(self._xml.toxml())
			filehandle.close()
		except IOError, err:
			self._logger.warning(str(err))


	def getSet(self, name):
		if self._file is None:
			return None
		if name is None:
			return None
		configuration = self._xml.getElementsByTagName('configuration')
		for set in configuration:
			if set.nodeType == set.ELEMENT_NODE:
				if set.getAttribute('name') == name:
					for textnode in set.childNodes:
						if textnode.nodeType == textnode.TEXT_NODE:
							return textnode.data
		return None


	def setSet(self, name, setting):
		if self._file is None:
			return None
		if name is None:
			return None
		if setting is None:
			setting = ''
		impl = xml.dom.getDOMImplementation()
		newdoc = impl.createDocument(None, 'nt', None)
		configurations = self._xml.getElementsByTagName('configuration')
		foundNode = 0
		foundTextnode = 0
		for configuration in configurations:
			for set in configuration.childNodes:
				if set.nodeType == set.ELEMENT_NODE:
					if set.getAttribute('name') == name:
						foundNode = 1
						for textnode in set.childNodes:
							if textnode.nodeType == textnode.TEXT_NODE:
								foundTextnode = 1
								if textnode.data != setting:
									self._logger.debug('Changing '+name+' from '+textnode.data+' to '+ setting)
									textnode.data = setting
						if foundTextnode == 0:
							textnode = newdoc.createTextNode(setting)
							set.appendChild(textnode)
							self._logger.debug('Adding textnode to '+name+' (value: '+setting+')')
			if foundNode == 0:
				self._logger.debug('Adding new setting (name: '+name+'; value: '+setting+')')
				node = newdoc.createElement('set')
				node.setAttribute('name',name)
				textnode = newdoc.createTextNode(setting)
				node.appendChild(textnode)
				configuration.appendChild(node)

