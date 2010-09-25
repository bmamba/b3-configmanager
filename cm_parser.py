import xml.dom.minidom
import cm_plugin

class Parser:
	
	def loadFile(self, file):
		self._file = file
		filehandle = open(self._file, 'r')
		self._xml = xml.dom.minidom.parse(filehandle)
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
		return plugins

	def getExtconfPath(self):
		section = self.getSection('settings','plugins')
		nodes = section.getElementsByTagName('set')
		for node in nodes:
			if node.getAttribute('name') == 'external_dir':
				for textnode in node.childNodes:
					if textnode.nodeType == textnode.TEXT_NODE:
						return textnode.data

	def getPluginConf(self):
		pluginConf = {}
		configurations = self._xml.getElementsByTagName('configuration')
		for conf in configurations:
			if conf.nodeType == conf.ELEMENT_NODE:
				sections = conf.getElementsByTagName('settings')
				for section in sections:
					nameSection = section.getAttribute('name')
					nodes = section.getElementsByTagName('set')
					pluginConf[nameSection] = {}
					for node in nodes:
						name = node.getAttribute('name')
						for textnode in node.childNodes:
							if textnode.nodeType == textnode.TEXT_NODE:
								value = textnode.data
						pluginConf[nameSection][name]=value
		return pluginConf
