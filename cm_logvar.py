import logging

FILE = 'cm.log'
LEVEL = logging.DEBUG

def getLogger(module):
	logging.basicConfig(filename=FILE,level=LEVEL)
	return logging.getLogger(module)
