# -*- coding: utf-8 -*-

import sys, os, shutil, threading, urllib2, glob, json, time, re, copy
import desktop


def log(title, format, *args):
	"""Log an arbitrary message.

    The first argument, FORMAT, is a format string for the
    message to be logged.  If the format string contains
    any % escapes requiring parameters, they should be
    specified as subsequent arguments (it's just like
    printf!).

	Source: BaseHTTPRequestHandler.log_message

	"""
	sys.stderr.write("%s [%s] %s\n" % ((title or "Service").ljust(8), time.strftime("%Y-%m-%d %H:%M:%S"), format%args))


class ServiceException(Exception):
	pass


class Config():

	_workdir = os.path.expanduser("~") + "/.rollpaper"

	_basename = "config.json"

	_default = {

		# delay before scraper starts
		"delay": 5,

		# delay between each scrape
		"refresh": 600,

		# remember last wallpapers count
		"history": 24,

		# retry count when scraper returns recently set wallpaper
		"retry": 5,

		# save recently added wallpapers into _workdir/cache directory (count)
		"cache": 8,

		# scraper name
		"scraper": "unsplash",

		# scraper options
		"options": {}

	}

	_config = None

	def __init__(self, path=None):
		"""Constructor.

		Set workdir, create workdir (if dont exist) and load config.

		"""
		if path:
			self._workdir = os.path.dirname(path)
			self._basename = os.path.basename(path)

		if not os.path.exists(self._workdir):
			os.makedirs(self._workdir)

		self.load()

	def path(self):
		"""Get config workdir.

		"""
		return self._workdir + "/" + self._basename

	def reset(self):
		"""Set default config.

		"""
		self._config = copy.deepcopy(self._default)

	def load(self):
		"""Load config from file.

		"""
		self.reset()

		if os.path.exists(self.path()):
			try:
				with open(self.path(), "r") as f:
					self._config = json.load(f)
			except Exception, e:
				self.reset()

		for key in self._default:
			if not key in self._config:
				self._config[key] = copy.deepcopy(self._default[key])

		for key in self._config.keys():
			if not key in self._default:
				del self._config[key]

	def save(self):
		"""Save config file.

		"""
		try:
			with open(self.path(), "w") as f:
				json.dump(self._config, f, indent=4)
		except Exception, e:
			raise ServiceException(e)

	def exists(self, key):
		"""Key exists in config.

		You can split keys with dot if you
		need some config key.

		>>> exists("port")
		True

		>>> exists("config.title")
		True

		>>> exists("config.nonexistingkey")
		False

		"""
		data = self._config
		args = key.split(".")

		for arg in args:
			try:
				if arg in data:
					data = data[arg]
				else:
					return False
			except Exception, e:
				return False

		return True

	def get(self, key):
		"""Get key value from config.

		You can split keys with dot if you
		need some config key.

		Non-existing key will return None.

		>>> get("port")
		8910

		>>> get("config.title")
		'Unknown title'

		>>> get("config.nonexistingkey")
		None

		"""
		data = self._config
		args = key.split(".")

		for arg in args:
			try:
				if arg in data:
					data = data[arg]
				else:
					return None
			except Exception, e:
				return None

		return data

	def set(self, key, value):
		"""Set key value in config.

		You can split keys with dot if you
		need some config key.

		>>> set("port", 1234)
		True

		>>> set("config.title", "Unknown title")
		True

		>>> set("config.nonexistingkey", False)
		True

		>>> set("config.anothernonexistingkey.key", "Foobar")
		False

		"""
		data = self._config
		args = key.split(".")
		last = args.pop()

		for arg in args:
			try:
				if arg in data:
					data = data[arg]
				else:
					return False
			except Exception, e:
				return False

		try:
			data[last] = value
		except Exception, e:
			return False

		return True

	def remove(self, key):
		"""Remove key from config.

		You can split keys with dot if you
		need some config key.

		>>> remove("port")
		True

		>>> remove("config.title")
		True

		>>> remove("config.nonexistingkey")
		False

		"""
		data = self._config
		args = key.split(".")
		last = args.pop()

		for arg in args:
			try:
				if arg in data:
					data = data[arg]
				else:
					return False
			except Exception, e:
				return False

		del data[last]

		return True


class Scraper():

	# working directory
	_workdir = os.path.expanduser("~") + "/.rollpaper"

	# thread
	_thread = None
	_timeout = None

	# scraper options
	# each scraper can have it's own config
	# set your own config when extending services.Scraper
	options = {}

	# retry count (see config.retry)
	retry = 5

	# recently added wallpapers
	wallpapers = []

	# remember recently added wallpapers count (see config.history)
	history = 24

	# save recently added wallpapers into _workdir/cache directory (see config.cache)
	cache = 8

	def __init__(self, path=None):
		"""Constructor.

		Set init data.

		"""
		if path:
			if os.path.isfile(path):
				path = os.path.dirname(path)
			self._workdir = path

		self._thread = None
		self._timeout = None

		self.wallpapers = []

	def __del__(self):
		"""Destructor.

		"""
		self.stop()

	def _loop(self, delay=0):
		"""Execute self.refresh() every self._timeout seconds.

		"""
		log("Scraper", "Loop started%s." % ("" if not delay else " (waiting %d seconds)" % delay))

		timeout = 0
		time.sleep(delay)

		while not self._timeout is None:
			timeout -= 1

			if timeout <= 0:
				self.refresh(self.retry)
				log("Scraper", "Waiting %d seconds...", self._timeout)

				timeout = self._timeout

			time.sleep(1)

		self._timeout = None
		self._thread = None

		log("Scraper", "Loop stopped.")

	def _handle_refresh_retry(self, url, retry):
		"""Onrefresh handler: check if we should retry request.

		"""
		if not url and retry:
			log("Scraper", "Scraper didn't find any wallpaper, retrieving new one (retry %d)...", retry)
			return self.refresh(retry - 1)
		elif not url and self.retry:
			return log("Scraper", "Scraper didn't find any wallpaper after %d tries, giving up.", self.retry)
		elif not url:
			return log("Scraper", "Scraper didn't find any wallpaper, giving up.")

		log("Scraper", "Wallpaper `%s` found.", url)

		if url in self.wallpapers and retry:
			log("Scraper", "Current wallpaper recently set, retrieving new one (retry %d)...", retry)
			return self.refresh(retry - 1)
		elif url in self.wallpapers and self.retry:
			log("Scraper", "Did not get unique wallpaper in %d tries.", self.retry)
		elif url in self.wallpapers:
			log("Scraper", "Current wallpaper recently set.")

		return True

	def _handle_refresh_file(self, url, retry):
		"""Onrefresh handler: copy file to self._workdir/wallpaper.

		"""
		protocol = url.split(":")[0]
		destination = self._workdir + "/wallpaper"

		if protocol in ["http", "https"]:
			log("Scraper", "Downloading `%s`...", url)
			try:
				req = urllib2.Request(url, headers={ "User-Agent" : "Magic Browser" })
				con = urllib2.urlopen(req)
				txt = con.read()
				con.close()

				with open(destination, "wb") as f:
					f.write(txt)
			except Exception, e:
				return log("Scraper", "Error downloading file (%s).", str(e))
		elif protocol in ["file"]:
			try:
				shutil.copyfile(re.sub(r"^file://", "", url), destination)
			except Exception, e:
				return log("Scraper", "Error copying file (%s).", str(e))
		else:
			return log("Scraper", "Unknown protocol `%s`.", protocol)

		return True

	def _handle_refresh_history(self, url, retry):
		"""Onrefresh handler: append url to history.

		"""
		if url in self.wallpapers: self.wallpapers.remove(url)
		self.wallpapers.insert(0, url)
		self.wallpapers = self.wallpapers[:self.history]

		return True

	def _handle_refresh_cache(self, url, retry):
		"""Onrefresh handler: append url to cache.

		"""
		if self.cache:
			src = self._workdir + "/wallpaper"
			dst = self._workdir + "/cache/" + time.strftime("%Y%m%d%H%M%S")

			try:
				if not os.path.isdir(self._workdir + "/cache/"):
					os.makedirs(self._workdir + "/cache/")

				shutil.copyfile(src, dst)
			except Exception, e:
				return log("Scraper", "Error copying file (%s).", str(e))

		files = glob.glob(self._workdir + "/cache/*")
		files = sorted(files)

		for f in files[:-self.cache]:
			try:
				os.remove(f)
			except Exception, e:
				log("Scraper", "Could not clear cache (%s).", str(e))

		return True

	def _handle_refresh_wallpaper(self, url, retry):
		"""Onrefresh handler: set desktop.

		"""
		log("Scraper", "Setting new wallpaper `%s`.", self._workdir + "/wallpaper")
		desktop.wallpaper(self._workdir + "/wallpaper")

	def status(self):
		"""Is scraper started.

		"""
		return bool(self._thread)

	def start(self, timeout, delay=0):
		"""Start self._loop()

		"""
		while self._thread:
			self.stop()

		self._timeout = timeout
		self._thread = threading.Thread(target=self._loop, args=(delay, ))
		self._thread.daemon = True
		self._thread.start()

	def stop(self):
		"""Stop self._loop()

		"""
		self._timeout = None

	def request(self):
		"""Get wallpaper.

		Set this method when extending Scraper()!!!
		See ./scrapers/unsplash.py as example.

		"""
		log("Scraper", "Warning: scraper not set.")

		return None

	def refresh(self, retry=0):
		"""Refresh method.

		Request for new wallpaper url.

		Restart request {retry} times if wallpaper
		already exists in self.wallpapers (was set
		in near past).

		"""
		log("Scraper", "Scrapping new data...")
		try:
			url = self.request()
		except Exception, e:
			return log("Scraper", str(e))

		if not self._handle_refresh_retry(url, retry): return
		if not self._handle_refresh_file(url, retry): return
		if not self._handle_refresh_history(url, retry): return
		if not self._handle_refresh_cache(url, retry): return
		if not self._handle_refresh_wallpaper(url, retry): return
