import logging

FILENAME = 'cm.log'
LEVEL = logging.DEBUG

logging.basicConfig(level=LEVEL, format='%(levelname)s:%(name)s:%(asctime)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename=FILENAME)

def getLogger(module):
	logger = logging.getLogger(module)
	return logger
