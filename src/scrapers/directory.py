import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

import random
import services

class Scraper(services.Scraper):
	"""
	Rollpaper directory scraper.

	By default request returns random image from ~/Pictures.

	You can set options in config.json to change default
	scraper options (see options variable).

	Valid options:
		path - (mixed)  photo location (string or list of strings)

	"""

	# set metadata for current scraper
	link = "https://github.com/fffilo/rollpaper"
	title = "Directory"
	description = "Rollpaper directory scraper."
	copyright = "fffilo"

	# scraper options
	options = {
		"path": os.path.expanduser("~") + "/Pictures"
	}

	def request(self):
		"""Find random image from options.path and create
		new Item() object with retrieved wallpaper.

		"""
		if type(self.options["path"]) in [str, unicode]:
			self.options["path"] = [ self.options["path"] ]

		imglist = []
		for source in self.options["path"]:
			if not os.path.isdir(source):
				services.log("Scraper", "Not a directory `%s`, skipping source." % source)
				continue
			for filename in os.listdir(source):
				ext = os.path.splitext(filename)[1]
				if ext.lower() in [".jpeg", ".jpg", ".png"]:
					imglist.append(os.path.join(source, filename))

		if not len(imglist):
			return services.log("Scraper", "Empty sources list.")

		result = random.choice(imglist)
		result = os.path.abspath(result)
		result = "file://" + result

		return result
