import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

import requests
import services

class Scraper(services.Scraper):
	"""
	Rollpaper unsplash.com scraper.

	By default request returns random 1920x1080 image.

	You can set options in config.json to change default
	scraper options (see options variable).

	Valid options:
		size     - (str)  photo dimensions
		category - (str)  specific category
		user     - (str)  specific user's username
		likes    - (bool) photo that has been liked by a specific user

	For more details see https://source.unsplash.com/

	"""

	# set metadata for current scraper
	link = "https://unsplash.com/"
	title = "Unsplash"
	description = "Free (do whatever you want) high-resolution photos."
	copyright = "Crew"

	# scraper options
	options = {
		"size": "1920x1080",
		"category": None,
		"user": None,
		"likes": False
	}

	def _url(self):
		"""Get url from options.

		"""
		result = "https://source.unsplash.com/random"

		if self.options["category"] and self.options["user"]:
			services.log("Scraper", "Warning: category and user option can not be used together (ignoring category).")
		if self.options["likes"] and not self.options["user"]:
			services.log("Scraper", "Warning: likes option must be used with user option (ignoring likes option).")

		if self.options["category"]: result = "https://source.unsplash.com/category/%s" % self.options["category"]
		if self.options["user"]: result = result = "https://source.unsplash.com/user/%s" % self.options["user"]
		if self.options["user"] and self.options["likes"]: result = result = "https://source.unsplash.com/user/%s/likes" % self.options["user"]
		if self.options["size"]: result += "/" + self.options["size"]

		return result

	def request(self):
		"""Send request to self._url() and return
		new Item() object with retrieved wallpaper.

		"""
		url = self._url()
		req = requests.get(url, timeout=10, allow_redirects=False, headers={ "User-Agent" : "Magic Browser" })
		req.close()

		if not req.status_code in [200, 302]:
			return services.log("Scraper", "Request to `%s` returns status code %d.", url, req.status_code)

		if "Location" in req.headers:
			return req.headers["Location"]

		return services.log("Scraper", "Location header not found in `%s` request.", url)
