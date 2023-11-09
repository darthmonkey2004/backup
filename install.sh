#!/bin/bash

mkdesktop() {
	echo "[Desktop Entry]" > backup.desktop
	echo "Version=1.0" >> backup.desktop
	echo "Name=Backup Utility" >> backup.desktop
	echo "Comment=Backup utility using duplicity and python3." >> backup.desktop
	echo "Exec=backup.py --menu" >> backup.desktop
	echo "Path=/home/$USER/.local" >> backup.desktop
	echo "Icon=/home/$USER/.local/backup.png" >> backup.desktop
	echo "Terminal=false" >> backup.desktop
	echo "Type=Application" >> backup.desktop
	echo "Categories=Utility" >> backup.desktop
	echo "StartupWMClass=GUI" >> backup.desktop
	mv backup.desktop "$HOME/.local/share/applications/backup.desktop"
}

setup() {
	cd "$HOME"
	#test for git
	hasgit=$(which git)
	if [ -z "$hasgit" ]; then
		#install if needed
		sudo apt-get install -y git
	fi
	if [ ! -d "$HOME/backup" ]; then
		clone repo
		git clone "https://github.com/darthmonkey2004/backup.git"
	fi
	cd backup
	#create source distro
	python3 setup.py sdist
	#install package using requirements.txt
	package=$(ls dist | grep "tar.gz")
	pip3 install -r requirements.txt "dist/$package"
	#copy icon to user folder (for .desktop)
	cp backup.png "$HOME/.local/backup.png"
	mkdesktop
}

if [ ! -d "$HOME/.backups" ]; then
	cd "$HOME"
	setup
else
	mkdesktop
fi
