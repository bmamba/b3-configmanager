import xml.dom.minidom
import cm_plugin
import logging, cm_logvar

class Parser:

	def __init__(self):
		self._logger = cm_logvar.getLogger('cm_parser:Parser')
	
	def loadFile(self, file):
		self._logger.info('Reading file '+file)
		self._file = file
		filehandle = open(self._file, 'r')
		self._xml = xml.dom.minidom.parse(filehandle)
		filehandle.close()

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
					#nodes = section.getElementsByTagName('set')
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

