#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, subprocess, re

class Wallpaper():

	def __init__(self):
		pass

	# http://stackoverflow.com/questions/2035657/what-is-my-current-desktop-environment/21213358#21213358
	def _is_running(self, process):
		try:
			s = subprocess.Popen(["ps", "axw"], stdout=subprocess.PIPE)
		except:
			s = subprocess.Popen(["tasklist", "/v"], stdout=subprocess.PIPE)

		for x in s.stdout:
			if re.search(process, x):
				return True

		return False

	# http://stackoverflow.com/questions/2035657/what-is-my-current-desktop-environment/21213358#21213358
	def _get_desktop_environment(self):
		if sys.platform in ["win32", "cygwin"]:
			return "windows"
		elif sys.platform == "darwin":
			return "mac"
		else:
			desktop_session = os.environ.get("DESKTOP_SESSION")
			if desktop_session is not None:
				desktop_session = desktop_session.lower()
				if desktop_session in ["gnome", "unity", "cinnamon", "mate", "xfce4", "lxde", "fluxbox", "blackbox", "openbox", "icewm", "jwm", "afterstep", "trinity", "kde"]:
					return desktop_session
				elif "xfce" in desktop_session or desktop_session.startswith("xubuntu"):
					return "xfce4"
				elif desktop_session.startswith("ubuntu"):
					return "unity"
				elif desktop_session.startswith("lubuntu"):
					return "lxde"
				elif desktop_session.startswith("kubuntu"):
					return "kde"
				elif desktop_session.startswith("razor"):
					return "razor-qt"
				elif desktop_session.startswith("wmaker"):
					return "windowmaker"
			if os.environ.get("KDE_FULL_SESSION") == "true":
				return "kde"
			elif os.environ.get("GNOME_DESKTOP_SESSION_ID"):
				if not "deprecated" in os.environ.get("GNOME_DESKTOP_SESSION_ID"):
					return "gnome2"
			elif self._is_running("xfce-mcs-manage"):
				return "xfce4"
			elif self._is_running("ksmserver"):
				return "kde"

		return "unknown"

	def _set_wallpaper_gnome(self, path):
		#uri = "'file://%s'" % file_loc
		try:
			gsettings = Gio.Settings.new("org.gnome.desktop.background")
			gsettings.set_string("picture-uri", path)
		except:
			subprocess.Popen(["gsettings", "set", "org.gnome.desktop.background", "picture-uri", path])

	def _set_wallpaper_unity(self, path):
		_set_wallpaper_gnome(path)

	def _set_wallpaper_cinnamon(self, path):
		_set_wallpaper_gnome(path)

	def _set_wallpaper_mate(self, path):
		try:
			subprocess.Popen(["gsettings", "set", "org.mate.background", "picture-filename", "'%s'" % path])
		except:
			subprocess.Popen(["mateconftool-2", "-t", "string", "--set", "/desktop/mate/background/picture_filename",'"%s"' % path])

	def _set_wallpaper_gnome2(self, path):
		subprocess.Popen(["gconftool-2", "-t", "string", "--set", "/desktop/gnome/background/picture_filename", '"%s"' % path])

	def _set_wallpaper_kde3(self, path):
		subprocess.Popen('dcop kdesktop KBackgroundIface setWallpaper 0 "%s" 6' % path, shell=True)

	def _set_wallpaper_trinity(self, path):
		_set_wallpaper_kde3(path)

	def _set_wallpaper_xfce4(self, path):
		subprocess.Popen(["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor0/image-path", "-s", path])
		subprocess.Popen(["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor0/image-style", "-s", "3"])
		subprocess.Popen(["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor0/image-show", "-s", "true"])
		subprocess.Popen(["xfdesktop", "--reload"])

	def _set_wallpaper_razor_qt(self, path):
		desktop_conf = configparser.ConfigParser()
		desktop_conf_file = os.path.join(self.get_config_dir("razor"), "desktop.conf")
		if os.path.isfile(desktop_conf_file):
			config_option = r"screens\1\desktops\1\wallpaper"
		else:
			desktop_conf_file = os.path.join(self.get_home_dir(),".razor/desktop.conf")
			config_option = r"desktops\1\wallpaper"
			desktop_conf.read(os.path.join(desktop_conf_file))
			try:
				if desktop_conf.has_option("razor", config_option):
					desktop_conf.set("razor", config_option, path)
					with codecs.open(desktop_conf_file, "w", encoding="utf-8", errors="replace") as f:
						desktop_conf.write(f)
			except:
				pass

	def _set_wallpaper_fluxbox(self, path):
		subprocess.Popen(["fbsetbg", path])

	def _set_wallpaper_jwm(self, path):
		_set_wallpaper_fluxbox(path)

	def _set_wallpaper_openbox(self, path):
		_set_wallpaper_fluxbox(path)

	def _set_wallpaper_afterstep(self, path):
		_set_wallpaper_fluxbox(path)

	def _set_wallpaper_icewm(self, path):
		subprocess.Popen(["icewmbg", path])

	def _set_wallpaper_blackbox(self, path):
		subprocess.Popen(["bsetbg", "-full", file_loc])

	def _set_wallpaper_lxde(self, path):
		subprocess.Popen("pcmanfm --set-wallpaper %s --wallpaper-mode=scaled" % path, shell=True)

	def _set_wallpaper_windowmaker(self, path):
		subprocess.Popen("wmsetbg -s -u %s" % path, shell=True)

	def _set_wallpaper_windows(self, path):
		import ctypes
		ctypes.windll.user32.SystemParametersInfoA(20, 0, path, 0)

	def _set_wallpaper_mac(self, path):
		try:
			from appscript import app, mactypes
			app("Finder").desktop_picture.set(mactypes.File(path))
		except ImportError:
			script = """/usr/bin/osascript<<END
			tell application "Finder" to
			set desktop picture to POSIX file "%s"
			end tell
			END"""
			subprocess.Popen(script % path, shell=True)

	def get_wallpaper(self):
		env = self._get_desktop_environment()
		method = "_get_wallpaper_" + re.compile("[\W]+").sub("_", env)

		if hasattr(self, method) and callable(getattr(self, method)):
			return getattr(self, method)

		raise Exception("Failed to get wallpaper. Unsupported desktop environment.")

	def set_wallpaper(self, path):
		env = self._get_desktop_environment()
		method = "_set_wallpaper_" + re.compile("[\W]+").sub("_", env)

		if hasattr(self, method) and callable(getattr(self, method)):
			return getattr(self, method)(path)

		raise Exception("Failed to set wallpaper. Unsupported desktop environment.")



if __name__ == "__main__":
	wp = Wallpaper()
	wp.set_wallpaper("http://thegamesdb.net/banners/fanart/original/131-1.jpg")
