import os
import cm_log
import cm_parser

class PluginConf:

	def __init__(self):
		self._logger = cm_log.getLogger('cm_pluginconf')
		self.infoPlugins = []

	def readPlugins(self, type, pdir, pconf):
		self._logger.debug('Try to detect plugins (type='+type+') in '+pdir+' with config directory '+pconf)
		direntries = os.listdir(pconf)
		parser = cm_parser.Parser()
		for entry in direntries:
			if entry[len(entry)-4:len(entry)] == '.xml' and entry[0:3] != 'b3.':
				self._logger.debug('Found plugin conf: '+entry)
				parser.loadFile(pconf+'/'+entry)
				name = parser.getPluginName()
				if name is not None:
					info = PluginInfo()
					info.type = type
					info.name = name
					info.path = pdir+'/'+name+'.py+'
					info.conf = pconf+'/'+entry
					self.infoPlugins.append(info)
		self._logger.debug('Plugins: '+str(self.infoPlugins))

class PluginInfo:

	type = None
	name = None
	path = None
	conf = None

