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
		plugins = []
		psection = psection.getElementsByTagName('plugin')
		for pentry in psection:
			plugin = cm_plugin.Plugin(pentry.getAttribute('name'))
			priority = pentry.getAttribute('priority')
			if priority != '':
				plugin.setPriority(priority)
			conf = pentry.getAttribute('conf')
			if conf != '':
				plugin.setConf(conf)
			plugins.append(plugin)
		return plugins
