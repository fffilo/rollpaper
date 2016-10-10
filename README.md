Rollpaper
=========

Change your desktop wallpapers every few minutes from various sources...

### Supported systems

Supported desktop environments:

- afterstep *
- blackbox *
- cinnamon *
- fluxbox *
- gnome
- gnome2 *
- icewm *
- jwm *
- kde3 *
- lxde *
- mac *
- mate *
- openbox *
- trinity *
- unity *
- windowmaker *
- windows
- xfce4 *

<sup><sub></sub>Note: items with asterisk are not tested yet<sub></sup>

### Install

Example of installation on debian-like systems (adjust code for your environment):

	git clone https://github.com/fffilo/rollpaper /tmp/rollpaper
	sudo mv /tmp/rollpaper/ /usr/share/
	sudo ln -s /usr/share/rollpaper/src/start.py /usr/bin/rollpaper
	sudo chown root:root /usr/share/rollpaper -R
	sudo chown root:root /usr/bin/rollpaper
	sudo chmod 755 /usr/bin/rollpaper

### Usage

To start rollpaper just execute `start.py`

	/usr/bin/python /path/to/rollpaper/start.py

...or if you installed it on your system (see install part), simply

	/usr/bin/rollpaper

### Configuration

...at this moment i'm too lazy to write something here

### To do

- cli arguments
- write configuration documentation
- test desktop environment support
- gui (indicator/trayicon) for easier user experience
- more scrapers
