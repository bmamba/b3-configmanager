import xml.dom.minidom
import cm_plugin
import cm_log

class Parser:

	def __init__(self):
		self._logger = cm_log.getLogger('cm_parser')
	
	def loadFile(self, file):
		self._logger.info('Reading file '+file)
		self._file = file
		filehandle = open(self._file, 'r')
		self._xml = xml.dom.minidom.parse(filehandle)
		filehandle.close()


	def loadExtraFile(self, file):
		self._logger.info('Reading extra file '+file)
		self._extrafile = file
		try:
			filehandle = open(self._extrafile, 'r')
			self._extraxml = xml.dom.minidom.parse(filehandle)
			filehandle.close()
		except IOError, msg:
			self._logger.info('Could not read extra file: '+str(msg))
			self._extraxml = None


	def saveFile(self):
		self._logger.info('Writing xml into '+self._file)
		filehandle = open(self._file+'.new', 'w')
		filehandle.write(self._xml.toxml())
		filehandle.close()

	def getSection(self, section, name = None):
		configurations = self._xml.getElementsByTagName('configuration')
		for conf in configurations:
			if conf.nodeType == conf.ELEMENT_NODE:
				sections = conf.getElementsByTagName(section)
				for section in sections:
					if name is None or section.getAttribute('name') == name:
						return section
		return None

	def getSet(self, section, section_name, name):
		section_node = self.getSection(section, section_name)
		if section_node is None:
			return None
		for node in section_node.childNodes:
			if node.nodeType == node.ELEMENT_NODE:
				if node.getAttribute('name') == name:
					return node

	
	def getSetData(self, section_name, name):
		node = self.getSet("settings", section_name, name)
		if node is None:
			return None
		for textnode in node.childNodes:
			if textnode.nodeType == textnode.TEXT_NODE:
				return textnode.data	


	def setSetData(self, section_name, name, value):
		node = self.getSet("settings", section_name, name)
		if node is None or value is None:
			return None
		for textnode in node.childNodes:
			if textnode.nodeType == textnode.TEXT_NODE:
				textnode.data = value


	def getPlugins(self):
		psection = self.getSection('plugins')
		if psection is None:
			return
		plugins = {}
		psection = psection.getElementsByTagName('plugin')
		for pentry in psection:
			name = pentry.getAttribute('name')
			plugin = cm_plugin.Plugin(name)
			priority = pentry.getAttribute('priority')
			if priority != '':
				plugin.setPriority(priority)
			conf = pentry.getAttribute('config')
			if conf != '':
				plugin.setConfig(conf)
			plugins[name] = plugin
			self._logger.debug('Found active plugin '+name)
		return plugins

	def getPluginConf(self):
		pluginConf = {}
		configurations = self._xml.getElementsByTagName('configuration')
		for conf in configurations:
			if conf.nodeType == conf.ELEMENT_NODE:
				sections = conf.getElementsByTagName('settings')
				for section in sections:
					nameSection = section.getAttribute('name')
					nodes = section.childNodes
					pluginConf[nameSection] = {}
					comment = ''
					for node in nodes:
						if node.nodeType == node.COMMENT_NODE:
							comment += node.data
						if node.nodeName == 'set':
							name = node.getAttribute('name')
							for textnode in node.childNodes:
								if textnode.nodeType == textnode.TEXT_NODE:
									value = textnode.data
							pluginConf[nameSection][name] = {}
							pluginConf[nameSection][name]['value'] = value
							pluginConf[nameSection][name]['comment'] = comment
							comment = ''
		return pluginConf

	def changePluginConfiguration(self, newSettings):
		configurations = self._xml.getElementsByTagName('configuration')
		for conf in configurations:
			if conf.nodeType == conf.ELEMENT_NODE:
				sections = conf.getElementsByTagName('settings')
				for section in sections:
					nameSection = section.getAttribute('name')
					nodes = section.getElementsByTagName('set')
					for node in nodes:
						name = node.getAttribute('name')
						if newSettings.has_key(nameSection) and newSettings[nameSection].has_key(name):
							for textnode in node.childNodes:
								if textnode.nodeType == textnode.TEXT_NODE:
									if textnode.data != newSettings[nameSection][name]['value']:
										self._logger.debug('Changing '+nameSection+' - '+name+'; old value: '+textnode.data+', new value: '+newSettings[nameSection][name]['value'])
										textnode.data = newSettings[nameSection][name]['value']

	def getPluginExtraConf(self):
		if self._extraxml == None:
			return None
		pluginConf = {}
		configurations = self._extraxml.getElementsByTagName('configuration')
		for conf in configurations:
			if conf.nodeType == conf.ELEMENT_NODE:
				sections = conf.getElementsByTagName('settings')
				for section in sections:
					nameSection = section.getAttribute('name')
					nodes = section.childNodes
					pluginConf[nameSection] = {}
					for node in nodes:
						if node.nodeName == 'set':
							name = node.getAttribute('name')
							pluginConf[nameSection][name] = {}
							for cnode in node.childNodes:
								if cnode.nodeType == cnode.ELEMENT_NODE:
									if cnode.nodeName == 'comment':
										for textnode in cnode.childNodes:
											if textnode.nodeType == textnode.TEXT_NODE:
												pluginConf[nameSection][name]['comment'] = textnode.data
									if cnode.nodeName == 'input':
										pluginConf[nameSection][name]['input'] = {}
										pluginConf[nameSection][name]['input']['type'] = cnode.getAttribute('type')
										pluginConf[nameSection][name]['input']['values'] = {}
										for value in cnode.childNodes:
											if value.nodeType == value.ELEMENT_NODE:
												pluginConf[nameSection][name]['input']['values'][value.getAttribute('name')] = value.getAttribute('value')

		return pluginConf

