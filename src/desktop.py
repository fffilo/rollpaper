#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, subprocess, re

try:
	from gi.repository import Gio
except Exception, e:
	pass

try:
	import ctypes
except Exception, e:
	pass

try:
	from appscript import app, mactypes
except Exception, e:
	pass


def process_running(process):
	"""Is process running

	>>> process_running("python")
	True

	>>> process_running("foobar")
	False

	Source:
	http://stackoverflow.com/questions/2035657/what-is-my-current-desktop-environment/21213358#21213358

	"""
	try:
		s = subprocess.Popen(["ps", "axw"], stdout=subprocess.PIPE)
	except:
		s = subprocess.Popen(["tasklist", "/v"], stdout=subprocess.PIPE)

	for x in s.stdout:
		if re.search(process, x):
			return True

	return False

def environment():
	"""Get desktop environment

	>>> environment()
	'gnome'

	Source:
	http://stackoverflow.com/questions/2035657/what-is-my-current-desktop-environment/21213358#21213358

	"""
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
		elif process_running("xfce-mcs-manage"):
			return "xfce4"
		elif process_running("ksmserver"):
			return "kde"

	return "unknown"

def wallpaper(value=None):
	"""Get/set desktop wallpaper

	Each desktop environment has it's own method for
	getting/setting desktop wallpaper.
	This method calls '_set_wallpaper_{environment}'
	or '_get_wallpaper_{environment}' in current
	module (if exists).

	Get wallpaper:

	>>> wallpaper()
	'file:///home/user/Pictures/image.jpeg'

	Set wallpaper:

	>>> wallpaper('file:///home/user/Pictures/image.jpeg')

	Raises a Exception if get/set method can not be found
	(desktop environment is	unknown):

	>>> wallpaper()
	'file:///home/user/Pictures/image.jpeg'
	Traceback (most recent call last):
	...
	Exception: can't get wallpaper for unknown desktop environment.

	>>> wallpaper('file:///home/user/Pictures/image.jpeg')
	Traceback (most recent call last):
	...
	Exception: can't set wallpaper for unknown desktop environment.

	"""
	mod = sys.modules[__name__]
	env = environment()
	method = "set" if bool(value) else "get"
	fn = "_%s_wallpaper_%s" % (method, re.compile("[\W]+").sub("_", env))
	args = [value] if method == "set" else []

	if hasattr(mod, fn):
		return getattr(mod, fn)(*args)

	raise Exception("can't %s wallpaper for %s desktop environment." % (method, env))

def _get_wallpaper_gnome():
	"""Get wallpaper for gnome desktop environment

	"""
	proc = subprocess.Popen(["gsettings", "get", "org.gnome.desktop.background", "picture-uri"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	output, error = proc.communicate()
	if error: raise Exception(error)

	return output.strip("\"\'\r\n")

def _set_wallpaper_gnome(path):
	"""Set wallpaper for gnome desktop environment

	Source:
	http://stackoverflow.com/questions/1977694/change-desktop-background/21213504#21213504

	"""
	try:
		Gio.Settings.new("org.gnome.desktop.background").set_string("picture-uri", path)
	except Exception, e:
		subprocess.Popen(["gsettings", "set", "org.gnome.desktop.background", "picture-uri", path])

def _get_wallpaper_unity():
	"""Get wallpaper for unity desktop environment

	"""
	return _get_wallpaper_gnome()

def _set_wallpaper_unity(path):
	"""Set wallpaper for unity desktop environment

	Source:
	http://stackoverflow.com/questions/1977694/change-desktop-background/21213504#21213504

	"""
	_set_wallpaper_gnome(path)

def _get_wallpaper_cinnamon():
	"""Get wallpaper for cinnamon desktop environment

	"""
	return _get_wallpaper_gnome()

def _set_wallpaper_cinnamon(path):
	"""Set wallpaper for cinnamon desktop environment

	Source:
	http://stackoverflow.com/questions/1977694/change-desktop-background/21213504#21213504

	"""
	_set_wallpaper_gnome(path)

def _get_wallpaper_mate():
	"""Get wallpaper for mate desktop environment

	"""
	try:
		proc = subprocess.Popen(["gsettings", "get", "org.mate.background", "picture-filename"])
	except:
		proc = subprocess.Popen(["mateconftool-2", "-t", "string", "--get", "/desktop/mate/background/picture_filename"])
	output, error = proc.communicate()
	if error: raise Exception(error)

	return output.strip("\"\'\r\n")

def _set_wallpaper_mate(path):
	"""Set wallpaper for mate desktop environment

	Source:
	http://stackoverflow.com/questions/1977694/change-desktop-background/21213504#21213504

	"""
	try:
		subprocess.Popen(["gsettings", "set", "org.mate.background", "picture-filename", "'%s'" % path])
	except:
		subprocess.Popen(["mateconftool-2", "-t", "string", "--set", "/desktop/mate/background/picture_filename", '"%s"' % path])

def _get_wallpaper_gnome2():
	proc = subprocess.Popen(["gconftool-2", "-t", "string", "--get", "/desktop/gnome/background/picture_filename"])
	output, error = proc.communicate()
	if error: raise Exception(error)

	return output.strip("\"\'\r\n")

def _set_wallpaper_gnome2(path):
	"""Set wallpaper for gnome2 desktop environment

	Source:
	http://stackoverflow.com/questions/1977694/change-desktop-background/21213504#21213504

	"""
	subprocess.Popen(["gconftool-2", "-t", "string", "--set", "/desktop/gnome/background/picture_filename", '"%s"' % path])

def _set_wallpaper_kde3(path):
	"""Set wallpaper for kde3 desktop environment

	Source:
	http://stackoverflow.com/questions/1977694/change-desktop-background/21213504#21213504

	"""
	subprocess.Popen('dcop kdesktop KBackgroundIface setWallpaper 0 "%s" 6' % path, shell=True)

def _set_wallpaper_trinity(path):
	"""Set wallpaper for trinity desktop environment

	Source:
	http://stackoverflow.com/questions/1977694/change-desktop-background/21213504#21213504

	"""
	_set_wallpaper_kde3(path)

def _set_wallpaper_xfce4(path):
	"""Set wallpaper for xfce4 desktop environment

	Source:
	http://stackoverflow.com/questions/1977694/change-desktop-background/21213504#21213504

	"""
	subprocess.Popen(["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor0/image-path", "-s", path])
	subprocess.Popen(["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor0/image-style", "-s", "3"])
	subprocess.Popen(["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor0/image-show", "-s", "true"])
	subprocess.Popen(["xfdesktop", "--reload"])

def _set_wallpaper_fluxbox(path):
	"""Set wallpaper for fluxbox desktop environment

	Source:
	http://stackoverflow.com/questions/1977694/change-desktop-background/21213504#21213504

	"""
	subprocess.Popen(["fbsetbg", path])

def _set_wallpaper_jwm(path):
	"""Set wallpaper for jwm desktop environment

	Source:
	http://stackoverflow.com/questions/1977694/change-desktop-background/21213504#21213504

	"""
	_set_wallpaper_fluxbox(path)

def _set_wallpaper_openbox(path):
	"""Set wallpaper for openbox desktop environment

	Source:
	http://stackoverflow.com/questions/1977694/change-desktop-background/21213504#21213504

	"""
	_set_wallpaper_fluxbox(path)

def _set_wallpaper_afterstep(path):
	"""Set wallpaper for afterstep desktop environment

	Source:
	http://stackoverflow.com/questions/1977694/change-desktop-background/21213504#21213504

	"""
	_set_wallpaper_fluxbox(path)

def _set_wallpaper_icewm(path):
	"""Set wallpaper for icewm desktop environment

	Source:
	http://stackoverflow.com/questions/1977694/change-desktop-background/21213504#21213504

	"""
	subprocess.Popen(["icewmbg", path])

def _set_wallpaper_blackbox(path):
	"""Set wallpaper for blackbox desktop environment

	Source:
	http://stackoverflow.com/questions/1977694/change-desktop-background/21213504#21213504

	"""
	subprocess.Popen(["bsetbg", "-full", path])

def _set_wallpaper_lxde(path):
	"""Set wallpaper for lxde desktop environment

	Source:
	http://stackoverflow.com/questions/1977694/change-desktop-background/21213504#21213504

	"""
	subprocess.Popen("pcmanfm --set-wallpaper %s --wallpaper-mode=scaled" % path, shell=True)

def _set_wallpaper_windowmaker(path):
	"""Set wallpaper for windowmaker desktop environment

	Source:
	http://stackoverflow.com/questions/1977694/change-desktop-background/21213504#21213504

	"""
	subprocess.Popen("wmsetbg -s -u %s" % path, shell=True)

def _set_wallpaper_windows(path):
	"""Set wallpaper for windows desktop environment

	Source:
	http://stackoverflow.com/questions/1977694/change-desktop-background/21213504#21213504

	"""
	ctypes.windll.user32.SystemParametersInfoA(20, 0, path, 0)

def _set_wallpaper_mac(path):
	"""Set wallpaper for mac desktop environment

	Source:
	http://stackoverflow.com/questions/1977694/change-desktop-background/21213504#21213504

	"""
	try:
		app("Finder").desktop_picture.set(mactypes.File(path))
	except ImportError:
		script = """/usr/bin/osascript<<END
		tell application "Finder" to
		set desktop picture to POSIX file "%s"
		end tell
		END"""
		subprocess.Popen(script % path, shell=True)


if __name__ == "__main__":
	try:
		print wallpaper()
	except Exception, e:
		print "Exception: " + str(e)
