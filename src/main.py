#!/usr/bin/env python
# -*- coding: utf-8 -*-

import services


config = None
scraper = None

def init_config():
	global config
	config = None

	# init config object
	try:
		config = services.Config()
	except Exception, e:
		raise Exception("Can not init config (%s)" % str(e))

	services.log("Service", "Config initialized.")

def init_scraper():
	global scraper
	scraper = None

	if config.get("scraper") is None:
		return services.log("Service", "Warning: scraper set to null, scraper not started.")

	# import scraper from config
	try:
		mod = getattr(__import__("scrapers.%s" % config.get("scraper")), config.get("scraper"))
	except ImportError, e:
		return services.log("Service", "Error: %s. Try to install module by executing shell command: `pip install {module_name}`", str(e))
	except Exception, e:
		return services.log("Service", "Error: can not import scraper (%s), scraper not started.", str(e))

	# init scraper object
	try:
		scraper = mod.Scraper(config.path())
		scraper.history_max_size = config.get("history")
		scraper.document_max_size = config.get("history")
		scraper.retry = config.get("retry")
	except Exception, e:
		scraper = None
		return services.log("Service", "Error: can not init scraper (%s), scraper not started.", str(e))

	# remove invalid scraper options from config
	for option in config.get("options").copy():
		if not option in scraper.options:
			config.remove("options.%s" % option)

	# set default scraper options in config (if not present)
	# set scraper options from config
	for option in scraper.options:
		if not config.exists("options.%s" % option):
			config.set("options.%s" % option, scraper.options[option])
		scraper.options[option] = config.get("options.%s" % option)

	services.log("Service", "Scraper initialized.")

def init():
	init_config()
	init_scraper()

	if config:
		config.save()

	loop()

def loop():
	try:
		# start scraper (if properly initialized)
		if not scraper is None:
			scraper.start(config.get("refresh"), config.get("delay"))

		if scraper is None:
			return services.log("Service", "Closing app loop...")

		# set app loop
		import time
		while True:
			time.sleep(0.2)
	except KeyboardInterrupt:
		services.log(None, "Break signal received, closing...")
	except Exception, e:
		raise e


if __name__ == "__main__":
	try:
		init()
	except Exception, e:
		print "Error: %s" % str(e)
