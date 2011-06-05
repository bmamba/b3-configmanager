import xml.dom.minidom
import os
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
		filehandle = open(self._file, 'w')
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
			plugin = cm_plugin.Plugin()
			plugin.name = name
			plugin.active = 1
			priority = pentry.getAttribute('priority')
			if priority != '':
				plugin.priority = priority
			conf = pentry.getAttribute('config')
			if conf != '':
				plugin.config = conf
			plugins[name] = plugin
			self._logger.debug('Found active plugin '+name)
		return plugins

	def getAllPlugins(self, dirlist):
		self._logger.debug('Try to detect plugins in '+str(dirlist))
		parser = Parser()
		plugins = self.getPlugins()
		infoPlugins = {}
		for dir in dirlist:
			direntries = os.listdir(dirlist[dir])
			for entry in direntries:
				if entry[len(entry)-4:len(entry)] == '.xml' and entry[0:3] != 'b3.':
					self._logger.debug('Found plugin conf: '+entry)
					parser.loadFile(dirlist[dir]+'/'+entry)
					name = parser.getPluginName()
					if name is not None:
						info = cm_plugin.Plugin()
						info.type = type
						info.name = name
						info.path = dir+'/'+name+'.py+'
						info.config = dirlist[dir]+'/'+entry
						if plugins.has_key(name):
							info.active = 1
							info.priority = plugins[name].priority
							self._logger.debug('Plugin '+name+' is active')
						infoPlugins[name] = info
		return infoPlugins

	def getPluginName(self):
		configurations = self._xml.getElementsByTagName('configuration')
		for conf in configurations:
			name = conf.getAttribute('plugin')
			if name is not None:
				self._logger.debug('Found name of plugin: '+name)
				return name
		return None

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

	def changePluginActivation(self, newSettings, allplugins):
		configurations = self._xml.getElementsByTagName('configuration')
		for conf in configurations:
			if conf.nodeType == conf.ELEMENT_NODE:
				sections = conf.getElementsByTagName('plugins')
				for section in sections:
					nodes = section.getElementsByTagName('plugin')
					for node in nodes:
						name = node.getAttribute('name')
						self._logger.debug('Checking plugin '+name)
						if newSettings.has_key(name):
							if newSettings[name]['Status']['value'] == 'not active':
								self._logger.debug('Remove plugin '+name)
								section.removeChild(node)
							if newSettings[name]['Priority']['value'] != node.getAttribute('priority'):
								if newSettings[name]['Priority']['value'] != '':
									self._logger.debug('Changing priority of '+name)
									node.setAttribute('priority',newSettings[name]['Priority']['value']) 
								else:
									self._logger.debug('Removing priority from '+name)
									node.removeAttribute('priority')
					for name in newSettings:
						if newSettings[name]['Status']['value'] == 'active' and allplugins[name].active == 0:
							self._logger.debug('Activate '+name)
							node = self.createNode('plugin')
							node.setAttribute('name',name)
							node.setAttribute('config',allplugins[name].config)
							if newSettings[name]['Priority']['value'] != '':
								node.setAttribute('priority',newSettings[name]['Priority']['value'])
							section.appendChild(node)

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

	def createNode(self,type):
		impl = xml.dom.getDOMImplementation()
		newdoc = impl.createDocument(None, 'nt', None)
		node = newdoc.createElement(type)
		return node

