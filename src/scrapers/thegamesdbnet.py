import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

import requests, random, xmltodict
import services

class Scraper(services.Scraper):
	"""
	Rollpaper thegamesdb.net scraper.

	By default request returns random 1920x1080 fanart
	from user's 38DC1C113AD7CABF favorites.

	You can set options in config.json to change default
	scraper options (see options variable).

	Valid options:
		size      - (str)  wallpaper dimensions
		accountid - (str)  thegamesdb user

	You can register at http://thegamesdb.net/, and pick
	your own favorite games. Set your accountid in config
	and your own favorite fanarts will bi scraped...

	"""

	# set metadata for current scraper
	link = "http://thegamesdb.net/"
	title = "TheGamesDB"
	description = "An open, online database for video game fans."
	copyright = "http://thegamesdb.net/"

	# scraper options
	options = {
		"size": "1920x1080",
		"accountid": "38DC1C113AD7CABF"
	}

	def _request_api(self, method, params={}):
		"""thegamesdb.net API request.

		Source:
		https://github.com/fffilo/thegamesdbnet/

		URL:
		http://wiki.thegamesdb.net/index.php/API_Introduction

		"""
		url = self.link + "/api/" + method
		for key, value in params.items():
			if value == None:
				del params[key]

		request = requests.get(url, params, timeout=30)
		response = request.text
		request.close()

		if not request.status_code == 200:
			return services.log("Scraper", "Request to `%s` returns status code %d.", url, request.status_code)

		result = xmltodict.parse(response, xml_attribs=True)

		if "Error" in result and result["Error"]:
			return services.log("Scraper", result["Error"])

		#return json.loads(json.dumps(result))
		return result

	def _size(self):
		"""Convert option size to width/height tuple.

		"""
		a = self.options["size"].split("x", 1)
		x = None
		y = None

		try:
			x = int(a[0])
		except Exception, e:
			pass
		try:
			y = int(a[1])
		except Exception, e:
			pass

		return (x, y)

	def request(self):
		"""Find user's favorite games, pick random one
		and check if not in history...

		"""
		favorites = self._request_api("User_Favorites.php", {"accountid": self.options["accountid"]})
		if favorites is None: return None
		favorites = favorites["Favorites"]
		favorites = favorites["Game"]
		favorites = sorted(favorites, key=lambda a: int(a))

		gameid = random.choice(favorites)
		gamedata = self._request_api("GetGame.php", {"id": gameid})
		if gamedata is None: return None
		gamedata = gamedata["Data"]

		#guid = gameid
		#title = ""
		#description = ""
		#category = ""
		#link = "%sgame/%s/" % (self.link, str(gameid))
		imglist = []
		result = None

		#if "Game" in gamedata and "GameTitle" in gamedata["Game"]: title = gamedata["Game"]["GameTitle"]
		#if "Game" in gamedata and "Overview" in gamedata["Game"]: description = gamedata["Game"]["Overview"]
		#if "Game" in gamedata and "Platform" in gamedata["Game"]: category = gamedata["Game"]["Platform"]

		size = self._size()
		baseurl = "" if not "baseImgUrl" in gamedata else gamedata["baseImgUrl"]

		if "Game" in gamedata and "Images" in gamedata["Game"] and "fanart" in gamedata["Game"]["Images"]:
			for img in gamedata["Game"]["Images"]["fanart"] if type(gamedata["Game"]["Images"]["fanart"]) is list else [gamedata["Game"]["Images"]["fanart"]]:
				ok = True
				if size[0] and int(img["original"]["@width"]) != size[0]: ok = False
				if size[1] and int(img["original"]["@height"]) != size[1]: ok = False

				if ok:
					imglist.append(baseurl + img["original"]["#text"])

		if not len(imglist):
			return None

		while len(imglist) and (not result or result in self.wallpapers):
			result = random.choice(imglist)
			imglist.remove(result)

		return result
