import logging
import colorama as clr

import os.path
import sys
import time
import traceback
# Pyling can't figure out what's in the record library for some reason
#pylint: disable-msg=E1101
class ColourHandler(logging.Handler):

	def __init__(self, level=logging.DEBUG):
		logging.Handler.__init__(self, level)
		self.formatter = logging.Formatter(clr.Style.RESET_ALL+'\r%(asctime)s - %(colour)s%(name)s'+clr.Style.RESET_ALL+'%(padding)s - %(style)s%(levelname)s - %(message)s'+clr.Style.RESET_ALL)
		clr.init()

	def emit(self, record):

		# print record.levelname
		# print record.name

		if record.name == "Main.Interface":
			record.colour = clr.Fore.BLUE
		elif record.name == "Main.DevPlugin":
			record.colour = clr.Fore.RED
		elif record.name == "Main.Main":
			record.colour = clr.Fore.GREEN
		elif record.name == "Main.LogPlugin":
			record.colour = clr.Fore.CYAN
		elif record.name == "Main.5":
			record.colour = clr.Fore.YELLOW
		elif record.name == "Main.6":
			record.colour = clr.Fore.MAGENTA
		else:
			record.colour = clr.Fore.WHITE


		if record.levelname == "DEBUG":
			record.style = clr.Style.DIM
		elif record.levelname == "WARNING":
			record.style = clr.Style.BRIGHT
		elif record.levelname == "ERROR":
			record.style = clr.Style.BRIGHT+clr.Fore.RED
		elif record.levelname == "CRITICAL":
			record.style = clr.Style.BRIGHT+clr.Back.BLUE+clr.Fore.RED
		else:
			record.style = clr.Style.NORMAL

		# record.padding = " "*(15-len(record.name))
		# text = self.format(record)
		# if "\n" in text:
		#       print text
		# else:
		#       lenOffset = (tt.get_terminal_width()-3) + len(record.style) + len(record.colour) + len(clr.Style.RESET_ALL)*2
		#       if len(text)> lenOffset:
		#               print text[:lenOffset]
		#               text = text[lenOffset:]
		#               width = tt.get_terminal_width()-3
		#               while len(text) > width:
		#                       print clr.Style.NORMAL+" "*20+record.style+"%s" % text[:width-20]
		#                       text = text[width-20:]
		#       else:
				# print text

		record.padding = ""
		print self.format(record)

class RobustFileHandler(logging.FileHandler):
	"""
	A handler class which writes formatted logging records to disk files.
	"""



	def emit(self, record):
		"""
		Emit a record.

		If the stream was not opened because 'delay' was specified in the
		constructor, open it before calling the superclass's emit.
		"""
		failures = 0
		while self.stream is None:
			try:
				self.stream = self._open()
			except:

				time.sleep(1)
				if failures > 3:
					traceback.print_exc()
					print "Cannot open log file?"
					return
				failures += 1
		failures = 0
		while failures < 3:
			try:
				logging.StreamHandler.emit(self, record)
				break
			except:
				failures += 1
		else:
			traceback.print_stack()
			print "Error writing to file?"


		self.close()


def exceptHook(exc_type, exc_value, exc_traceback):
	if issubclass(exc_type, KeyboardInterrupt):
		sys.__excepthook__(exc_type, exc_value, exc_traceback)
		return
	mainLogger = logging.getLogger("Main")                  # Main logger
	mainLogger.critical('Uncaught exception!')
	mainLogger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))



def initLogging(logLevel=logging.INFO):
	print "Setting up loggers....",

	mainLogger = logging.getLogger("Main")                  # Main logger
	mainLogger.setLevel(logLevel)
	ch = ColourHandler()
	mainLogger.addHandler(ch)

	logName = "Error - %s.txt" % (time.strftime("%Y-%m-%d %H;%M;%S", time.gmtime()))

	errLogHandler = RobustFileHandler(os.path.join("./logs", logName))
	errLogHandler.setLevel(logging.WARNING)
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	errLogHandler.setFormatter(formatter)

	mainLogger.addHandler(errLogHandler)

	# Install override for excepthook, to catch all errors
	sys.excepthook = exceptHook

	print "done"
