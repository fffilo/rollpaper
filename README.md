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

After installation start rollpaper with `rollpaper` command.

### Usage

Install rollpaper to your system (see install part), or simply clone repository

	git clone https://github.com/fffilo/rollpaper /path/to/rollpaper

...and start it with

	/usr/bin/python /path/to/rollpaper/src/start.py

### Configuration

...at this moment i'm too lazy to write something here

### To do

- cli arguments
- write configuration documentation
- test desktop environment support
- gui (indicator/trayicon) for easier user experience
- more scrapers
