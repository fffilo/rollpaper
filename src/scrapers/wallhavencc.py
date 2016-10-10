import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

import requests, re, lxml.html
import services

class Scraper(services.Scraper):
	"""
	Rollpaper wallhaven.cc scraper.

	By default request returns random 1920x1080 image.

	You can set options in config.json to change default
	scraper options (see options variable).

	Valid options:
		size    - (str)  photo dimensions (1024x768|1280x800|1366x768|1280x960|1440x900|1600x900|1280x1024|1600x1200|1680x1050|1920x1080|1920x1200|2560x1440|2560x1600|3840x1080|5760x1080|3840x2160|5120x2880)
		general - (bool) use category general
		anime   - (bool) use category anime
		people  - (bool) use category people

	Note: you can use combination of sizes -> eg. { size: "1920x1080,3840x2160" }

	"""

	# set metadata for current scraper
	link = "https://alpha.wallhaven.cc/"
	title = "Wallhaven"
	description = "The best wallpapers on the Net!"
	copyright = "https://wallhaven.cc/"

	# scraper options
	options = {
		"size": "1920x1080",
		"general": True,
		"anime": True,
		"people": True
	}

	def _url(self):
		"""Get url from options.

		"""
		category = "" \
			+ ("1" if bool(self.options["general"]) else "0") \
			+ ("1" if bool(self.options["anime"]) else "0") \
			+ ("1" if bool(self.options["people"]) else "0")
		if category == "000": category = "111"
		purity = "110"
		resolutions = self.options["size"]

		return self.link + "search?categories=%s&purity=%s&resolutions=%s&sorting=random&order=desc" % (category, purity, resolutions)

	def request(self):
		"""Send request to self._url() and parse
		wallpaper from HTML response.

		Execute request with stream option, so we
		can dowload html by chunks (no need for
		full page download). Read chunks until figure
		tag closure is found.

		"""
		url = self._url()
		req = requests.get(url, timeout=10, allow_redirects=False, headers={ "User-Agent" : "Magic Browser" }, stream=True)
		if not req.status_code in [200]:
			req.close()
			return services.log("Scraper", "Request to `%s` returns status code %d.", url, req.status_code)

		buff = ""
		for chunk in req.iter_content():
			buff += chunk

			if "</figure>" in buff:
				break
		req.close()

		pattern = re.compile("<figure(.*?)>(.*?)<\/figure>")
		match = re.search(pattern, buff)
		if not match:
			return services.log("Scraper", "Unable to parse response data (figure tag).")

		try:
			doc = lxml.html.fromstring(match.group(0))
			guid = doc.xpath("//figure")[0].get("data-wallpaper-id")
			#thumb = doc.xpath("//img")[0].get("data-src")
			#link = doc.xpath("//a[@class=\"preview\"]")[0].get("href")
		except Exception, e:
			return services.log("Scraper", "Unable to parse response data (media data).")

		return "https://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-%s.jpg" % guid

