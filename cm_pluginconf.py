import os
import cm_log
import cm_parser
import cm_plugin

class PluginConf:

	def __init__(self, b3parser):
		self._logger = cm_log.getLogger('cm_pluginconf')
		self._b3parser = b3parser
		self.infoPlugins = []

	def readPlugins(self, type, pdir, pconf):
		self._logger.debug('Try to detect plugins (type='+type+') in '+pdir+' with config directory '+pconf)
		direntries = os.listdir(pconf)
		parser = cm_parser.Parser()
		plugins = self._b3parser.getPlugins()
		for entry in direntries:
			if entry[len(entry)-4:len(entry)] == '.xml' and entry[0:3] != 'b3.':
				self._logger.debug('Found plugin conf: '+entry)
				parser.loadFile(pconf+'/'+entry)
				name = parser.getPluginName()
				if name is not None:
					info = cm_plugin.Plugin()
					info.type = type
					info.name = name
					info.path = pdir+'/'+name+'.py+'
					info.config = pconf+'/'+entry
					if plugins.has_key(name):
						info.active = 1
						info.priority = plugins[name].priority
						self._logger.debug('Plugin '+name+' is active')
					self.infoPlugins.append(info)

